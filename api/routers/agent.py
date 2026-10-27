import json
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.schemas import AgentRunRequest, AgentApprovalRequest
from agent.graph import agent_graph
from db.crud import db_list_tasks

router = APIRouter(prefix="/agent", tags=["Agent"])

# In-memory store for paused task states waiting for approval
_paused_agent_states = {}

async def _stream_agent_execution(user_input: str, user_id: str) -> AsyncGenerator[str, None]:
    state = {
        "user_input": user_input,
        "user_id": user_id,
        "execution_trace": []
    }
    
    # Run graph execution
    final_state = agent_graph.invoke(state)
    
    # Stream step traces one by one
    trace = final_state.get("execution_trace", [])
    for step in trace:
        data = {
            "task_id": final_state.get("task_id"),
            "status": final_state.get("task_status"),
            "step_name": step["step_name"],
            "details": step["details"],
            "step_status": step.get("status", "COMPLETED"),
            "timestamp": step["timestamp"]
        }
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(0.1)

    # Save state if awaiting approval
    if final_state.get("task_status") == "AWAITING_APPROVAL":
        _paused_agent_states[final_state["task_id"]] = final_state
        data = {
            "task_id": final_state["task_id"],
            "status": "AWAITING_APPROVAL",
            "message": "Execution paused waiting for user approval.",
            "tool_selected": final_state.get("tool_selected"),
            "tool_input": final_state.get("tool_input")
        }
        yield f"data: {json.dumps(data)}\n\n"
    else:
        # Stream final response
        data = {
            "task_id": final_state.get("task_id"),
            "status": final_state.get("task_status"),
            "final_response": final_state.get("final_response", ""),
            "complete": True
        }
        yield f"data: {json.dumps(data)}\n\n"

@router.post("/run")
async def run_agent(req: AgentRunRequest):
    """
    Executes the autonomous agent graph and streams step events via Server-Sent Events (SSE).
    """
    return StreamingResponse(
        _stream_agent_execution(req.user_input, req.user_id),
        media_type="text/event-stream"
    )

@router.post("/approve")
async def approve_agent_task(req: AgentApprovalRequest):
    """
    Submits human approval decision (True/False) for a paused task and resumes execution graph.
    """
    state = _paused_agent_states.get(req.task_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"No paused agent task found with ID '{req.task_id}'.")
    
    state["approved_by_user"] = req.approved
    state["requires_approval"] = False
    
    # Resume agent execution graph
    resumed_state = agent_graph.invoke(state)
    if req.task_id in _paused_agent_states:
        del _paused_agent_states[req.task_id]

    return {
        "task_id": req.task_id,
        "approved": req.approved,
        "status": resumed_state.get("task_status"),
        "final_response": resumed_state.get("final_response", ""),
        "execution_trace": resumed_state.get("execution_trace", [])
    }
