import logging
from agent.state import AgentState

logger = logging.getLogger(__name__)


def route_after_select_tool(state: AgentState) -> str:
    """
    Routing function after the select_tool node.

    Returns
    -------
    "approval_gate" – tool requires human approval and hasn't been approved yet.
    "execute_tool"  – tool is ready to run (no approval needed / already approved).
    "update_memory" – no tool selected (all plan steps exhausted); wrap up.
    """
    tool = state.get("tool_selected")
    if not tool:
        logger.debug("[Route:select_tool] No tool selected → update_memory")
        return "update_memory"

    if state.get("requires_approval") and not state.get("approved_by_user"):
        logger.debug(f"[Route:select_tool] Tool '{tool}' requires approval → approval_gate")
        return "approval_gate"

    logger.debug(f"[Route:select_tool] Tool '{tool}' → execute_tool")
    return "execute_tool"


def route_after_approval_gate(state: AgentState) -> str:
    """
    Routing function after the approval_gate node.

    Returns
    -------
    "pause"        – waiting for human decision (LangGraph interrupt point).
    "execute_tool" – user approved; proceed with execution.
    "finalize"     – user rejected; cancel and generate final response.
    """
    status = state.get("task_status")

    if status == "AWAITING_APPROVAL":
        logger.debug("[Route:approval_gate] Status=AWAITING_APPROVAL → pause")
        return "pause"

    if state.get("approved_by_user") is False:
        state["task_status"] = "CANCELLED"
        state["final_response"] = "Task execution was rejected at the human-approval gate."
        logger.debug("[Route:approval_gate] User rejected → finalize")
        return "finalize"

    logger.debug("[Route:approval_gate] Approved → execute_tool")
    return "execute_tool"


def route_after_evaluation(state: AgentState) -> str:
    """
    Routing function after the evaluate_result node.

    Returns
    -------
    "finalize"      – task failed; terminate with error report.
    "select_tool"   – retry current step OR advance to next plan step.
    "update_memory" – all plan steps completed successfully.
    """
    status = state.get("task_status")
    if status == "FAILED":
        logger.debug("[Route:evaluate] Status=FAILED → finalize")
        return "finalize"

    retry_count = state.get("retry_count", 0)
    if retry_count > 0:
        logger.debug(f"[Route:evaluate] retry_count={retry_count} → select_tool (retry)")
        return "select_tool"

    current_step = state.get("current_step", 0)
    plan_length = len(state.get("current_plan") or [])

    if current_step < plan_length:
        logger.debug(f"[Route:evaluate] step {current_step}/{plan_length} → select_tool (next)")
        return "select_tool"

    logger.debug("[Route:evaluate] All steps done → update_memory")
    return "update_memory"
