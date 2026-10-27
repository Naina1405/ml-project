"""
agent/graph.py
==============
Builds and exposes ``agent_graph``, the central orchestration engine.

Strategy
--------
1. Try to build a compiled LangGraph ``StateGraph`` (preferred – handles
   streaming, checkpointing, and interrupt/resume natively).
2. Fall back to the lightweight ``NativeStateGraph`` shim if LangGraph is
   not installed or compilation fails.
"""
import logging
from typing import Dict, Any

from agent.state import AgentState
from agent.nodes import (
    understand_goal_node,
    create_plan_node,
    select_tool_node,
    approval_gate_node,
    execute_tool_node,
    evaluate_result_node,
    update_memory_node,
    finalize_node,
)
from agent.edges import (
    route_after_select_tool,
    route_after_approval_gate,
    route_after_evaluation,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Native fallback runtime (no LangGraph dependency)
# ---------------------------------------------------------------------------

class NativeStateGraph:
    """
    Lightweight, synchronous, cyclic state-graph runner.

    Faithfully mirrors the LangGraph StateGraph topology so the agent
    behaves identically whether LangGraph is installed or not.
    """

    def invoke(self, initial_state: Dict[str, Any]) -> AgentState:
        state: AgentState = dict(initial_state)  # type: ignore[assignment]

        # --- Phase 1: understand & plan -------------------------------------
        state = understand_goal_node(state)
        state = create_plan_node(state)

        # --- Phase 2: tool-execution loop -----------------------------------
        max_iterations = 50  # safety cap to prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            state = select_tool_node(state)
            next_node = route_after_select_tool(state)

            if next_node == "update_memory":
                state = update_memory_node(state)
                state = finalize_node(state)
                break

            if next_node == "approval_gate":
                state = approval_gate_node(state)
                gate_next = route_after_approval_gate(state)

                if gate_next == "pause":
                    # Return current state so the UI can re-invoke with approval
                    break
                elif gate_next == "finalize":
                    state = finalize_node(state)
                    break
                elif gate_next == "execute_tool":
                    state = execute_tool_node(state)
                # fall through to evaluate_result
            else:
                # "execute_tool"
                state = execute_tool_node(state)

            # Evaluate after execution
            state = evaluate_result_node(state)
            eval_next = route_after_evaluation(state)

            if eval_next == "finalize":
                state = finalize_node(state)
                break
            elif eval_next == "update_memory":
                state = update_memory_node(state)
                state = finalize_node(state)
                break
            # else: "select_tool" → continue loop

        else:
            # Exceeded iteration cap
            logger.error("[NativeStateGraph] Safety cap reached – forcing finalize.")
            state["task_status"] = "FAILED"
            state["error_message"] = "Agent exceeded maximum iteration limit."
            state = finalize_node(state)

        return state


# ---------------------------------------------------------------------------
# LangGraph builder
# ---------------------------------------------------------------------------

def build_agent_graph():
    """
    Attempts to compile a LangGraph StateGraph.
    Falls back to NativeStateGraph if LangGraph is unavailable.
    """
    try:
        from langgraph.graph import StateGraph, END  # type: ignore

        workflow = StateGraph(AgentState)

        # Register all nodes
        workflow.add_node("understand_goal", understand_goal_node)
        workflow.add_node("create_plan", create_plan_node)
        workflow.add_node("select_tool", select_tool_node)
        workflow.add_node("approval_gate", approval_gate_node)
        workflow.add_node("execute_tool", execute_tool_node)
        workflow.add_node("evaluate_result", evaluate_result_node)
        workflow.add_node("update_memory", update_memory_node)
        workflow.add_node("finalize", finalize_node)

        # Entry point
        workflow.set_entry_point("understand_goal")

        # Deterministic edges
        workflow.add_edge("understand_goal", "create_plan")
        workflow.add_edge("create_plan", "select_tool")
        workflow.add_edge("execute_tool", "evaluate_result")
        workflow.add_edge("update_memory", "finalize")
        workflow.add_edge("finalize", END)

        # Conditional edges (routing functions)
        workflow.add_conditional_edges(
            "select_tool",
            route_after_select_tool,
            {
                "approval_gate": "approval_gate",
                "execute_tool": "execute_tool",
                "update_memory": "update_memory",
            },
        )
        workflow.add_conditional_edges(
            "approval_gate",
            route_after_approval_gate,
            {
                "pause": END,
                "execute_tool": "execute_tool",
                "finalize": "finalize",
            },
        )
        workflow.add_conditional_edges(
            "evaluate_result",
            route_after_evaluation,
            {
                "select_tool": "select_tool",
                "update_memory": "update_memory",
                "finalize": "finalize",
            },
        )

        compiled = workflow.compile()
        logger.info("[AgentGraph] LangGraph StateGraph compiled successfully.")
        return compiled

    except Exception as exc:
        logger.warning(
            f"[AgentGraph] LangGraph unavailable ({exc}). "
            "Falling back to NativeStateGraph runtime."
        )
        return NativeStateGraph()


# Module-level singleton – imported by the API and UI layers
agent_graph = build_agent_graph()
