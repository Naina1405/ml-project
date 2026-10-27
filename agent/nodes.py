import json
import uuid
import logging
import datetime
from typing import Dict, Any, List

from agent.state import AgentState
from config.settings import settings
from db.crud import db_create_task, db_update_task_status, db_create_step
from memory.memory_manager import memory_manager
from tools.registry import tool_registry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ML Classifier — lazy-loaded singleton
# ---------------------------------------------------------------------------
_ml_classifier = None


def _get_ml_classifier():
    """
    Returns a trained intent classifier (advanced → baseline → None fallback).
    The model is loaded once and cached for the process lifetime.
    """
    global _ml_classifier
    if _ml_classifier is None:
        try:
            from models.transformer_classifier import TransformerEmbeddingClassifier
            clf = TransformerEmbeddingClassifier()
            clf.load("advanced_model.pkl")
            if clf.is_trained:
                _ml_classifier = clf
                logger.info("[Classifier] Loaded TransformerEmbeddingClassifier (advanced_model.pkl)")
                return _ml_classifier
        except Exception as e:
            logger.debug(f"[Classifier] Advanced model unavailable: {e}")

        try:
            from models.baseline_classifier import BaselineIntentClassifier
            clf = BaselineIntentClassifier()
            clf.load("baseline_model.pkl")
            if clf.is_trained:
                _ml_classifier = clf
                logger.info("[Classifier] Loaded BaselineIntentClassifier (baseline_model.pkl)")
                return _ml_classifier
        except Exception as e:
            logger.debug(f"[Classifier] Baseline model unavailable: {e}")

        _ml_classifier = None  # Explicit None sentinel
    return _ml_classifier


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


def _log_trace(
    state: AgentState,
    step_name: str,
    details: str,
    status: str = "COMPLETED",
) -> None:
    """Append a trace event to the state's execution_trace list."""
    if state.get("execution_trace") is None:
        state["execution_trace"] = []
    state["execution_trace"].append(
        {
            "timestamp": _now(),
            "step_name": step_name,
            "details": details,
            "status": status,
        }
    )
    logger.debug(f"[Trace] [{status}] {step_name}: {details}")


# ---------------------------------------------------------------------------
# Node: Understand Goal
# ---------------------------------------------------------------------------

def understand_goal_node(state: AgentState) -> AgentState:
    """
    Step 1 – Classify intent, retrieve relevant memories, initialise task record.
    """
    user_input = state.get("user_input", "")
    user_id = state.get("user_id", settings.DEFAULT_USER_ID)
    task_id = state.get("task_id") or str(uuid.uuid4())[:8]

    # --- ML intent classification -------------------------------------------
    clf = _get_ml_classifier()
    intent = "general_task"
    confidence = 0.0

    if clf and getattr(clf, "is_trained", False):
        try:
            intent, confidence = clf.predict(user_input)
        except Exception as exc:
            logger.warning(f"[Classifier] Prediction failed: {exc}")
            intent, confidence = "general_task", 0.0

    # --- Retrieve contextual memories ----------------------------------------
    try:
        memories = memory_manager.retrieve_relevant_memories(
            user_id=user_id, query=user_input, limit=3
        )
    except Exception as exc:
        logger.warning(f"[Memory] Retrieval failed: {exc}")
        memories = []

    # --- Persist task to DB ---------------------------------------------------
    try:
        db_create_task(
            user_id=user_id,
            goal_prompt=user_input,
            task_id=task_id,
            status="IN_PROGRESS",
        )
    except Exception as exc:
        logger.warning(f"[DB] Task creation failed: {exc}")

    state.update(
        {
            "task_id": task_id,
            "intent": intent,
            "intent_confidence": round(float(confidence), 4),
            "memory_context": memories,
            "current_step": 0,
            "retry_count": 0,
            "max_retries": settings.MAX_RETRIES,
            "task_status": "IN_PROGRESS",
        }
    )

    _log_trace(
        state,
        "Understand Goal",
        f"Intent: '{intent}' (conf={confidence:.2f}). "
        f"Retrieved {len(memories)} memory context(s).",
    )
    return state


# ---------------------------------------------------------------------------
# Node: Create Plan
# ---------------------------------------------------------------------------

INTENT_PLAN_MAP: Dict[str, List[str]] = {
    "multi_step_task": [
        "Search web for relevant information",
        "Compare options and identify best candidate",
        "Save best result to user memory",
        "Schedule a reminder or calendar event",
    ],
    "compare_information": [
        "Search web for relevant information",
        "Compare options and identify best candidate",
        "Save comparison summary to memory",
    ],
    "send_email": [
        "Draft email content",
        "Request human approval to send email",
        "Send email to recipient",
    ],
    "create_reminder": ["Schedule reminder via APScheduler"],
    "cancel_task": ["Cancel existing scheduled task"],
    "create_calendar_event": ["Create calendar event with provided details"],
    "save_memory": ["Save user preference or note to long-term memory"],
    "retrieve_memory": ["Retrieve relevant stored preferences from memory"],
    "search_information": ["Search web for details and return summarised result"],
    "summarize_information": ["Search web for details and return summarised result"],
}

DEFAULT_PLAN = ["Analyse objective and execute the most appropriate tool"]


def create_plan_node(state: AgentState) -> AgentState:
    """
    Step 2 – Produce an ordered execution plan from the classified intent.
    """
    intent = state.get("intent", "general_task")
    plan = INTENT_PLAN_MAP.get(intent, DEFAULT_PLAN)

    state["current_plan"] = plan

    steps_str = "\n".join(f"  {i + 1}. {s}" for i, s in enumerate(plan))
    _log_trace(
        state,
        "Create Plan",
        f"Decomposed into {len(plan)} subtask(s) for intent '{intent}':\n{steps_str}",
    )
    return state


# ---------------------------------------------------------------------------
# Node: Select Tool
# ---------------------------------------------------------------------------

def _resolve_tool(step_desc: str, user_input: str, intent: str, state: AgentState):
    """
    Heuristic tool-selector returning (tool_name, tool_input, requires_approval).
    Order matters: more specific patterns should come first.
    """
    sl = step_desc.lower()
    ui = user_input.lower()
    uid = state.get("user_id", settings.DEFAULT_USER_ID)

    # E-mail (sensitive)
    if "email" in sl or intent == "send_email" or "email" in ui:
        if "send" in sl or "send" in ui or intent == "send_email":
            # Extract recipient from input if possible
            recipient = "recipient@example.com"
            for word in user_input.split():
                if "@" in word and "." in word:
                    recipient = word.strip(".,;:")
                    break
            return (
                "email",
                {
                    "action": "send",
                    "recipient": recipient,
                    "subject": f"Task Report: {user_input[:60]}",
                    "body": f"Automated report for task:\n\n{user_input}",
                },
                True,  # requires_approval
            )
        return (
            "email",
            {
                "action": "draft",
                "recipient": "recipient@example.com",
                "subject": f"Draft: {user_input[:60]}",
                "body": f"Draft content for:\n{user_input}",
            },
            False,
        )

    # Memory – save
    if ("save" in sl or "memory" in sl or "preference" in sl) and "retrieve" not in sl:
        return (
            "memory",
            {
                "action": "save",
                "content": f"User preference: {user_input}",
                "user_id": uid,
            },
            False,
        )

    # Memory – retrieve
    if "retrieve" in sl or ("memory" in sl and "save" not in sl):
        return (
            "memory",
            {"action": "retrieve", "query": user_input, "user_id": uid},
            False,
        )

    # Scheduler / reminder
    if "reminder" in sl or "schedule" in sl or intent in ("create_reminder", "cancel_task"):
        return (
            "scheduler",
            {
                "action": "create",
                "message": f"Reminder: {user_input[:80]}",
                "trigger_seconds": 86400,  # default: 24 h
            },
            False,
        )

    # Calendar
    if "calendar" in sl or "event" in sl or intent == "create_calendar_event":
        return (
            "calendar",
            {
                "action": "create",
                "title": f"Event: {user_input[:60]}",
                "datetime": "tomorrow 10:00",
            },
            False,
        )

    # Task manager
    if "task" in sl and "manager" in sl:
        return (
            "task_manager",
            {"action": "create", "title": user_input[:120]},
            False,
        )

    # Default: web search
    return (
        "web_search",
        {"query": user_input, "num_results": 5},
        False,
    )


def select_tool_node(state: AgentState) -> AgentState:
    """
    Step 3 – Choose the appropriate tool for the current plan step.
    """
    plan = state.get("current_plan", [])
    current_step = state.get("current_step", 0)
    user_input = state.get("user_input", "")
    intent = state.get("intent", "")

    if current_step >= len(plan):
        state["tool_selected"] = None
        state["tool_input"] = None
        state["requires_approval"] = False
        return state

    step_desc = plan[current_step]
    tool_name, tool_input, requires_approval = _resolve_tool(
        step_desc, user_input, intent, state
    )

    state["tool_selected"] = tool_name
    state["tool_input"] = tool_input
    state["requires_approval"] = requires_approval

    _log_trace(
        state,
        "Select Tool",
        f"Step {current_step + 1}/{len(plan)}: '{step_desc}' → [{tool_name}]"
        f"  approval_required={requires_approval}",
    )
    return state


# ---------------------------------------------------------------------------
# Node: Approval Gate
# ---------------------------------------------------------------------------

def approval_gate_node(state: AgentState) -> AgentState:
    """
    Step 4 – Pause execution for human review when a sensitive action is selected.
    """
    if state.get("requires_approval") and not state.get("approved_by_user"):
        state["task_status"] = "AWAITING_APPROVAL"
        _log_trace(
            state,
            "Approval Gate",
            f"⚠️ Sensitive action [{state.get('tool_selected')}] paused for human review.",
            status="WAITING_APPROVAL",
        )
    else:
        state["task_status"] = "IN_PROGRESS"
    return state


# ---------------------------------------------------------------------------
# Node: Execute Tool
# ---------------------------------------------------------------------------

def execute_tool_node(state: AgentState) -> AgentState:
    """
    Step 5 – Invoke the selected tool and record the result in the DB.
    """
    tool_name = state.get("tool_selected")
    tool_input = state.get("tool_input") or {}
    task_id = state.get("task_id", "unknown")
    plan = state.get("current_plan", [])
    step_num = state.get("current_step", 0) + 1

    if not tool_name:
        return state

    _log_trace(
        state,
        "Execute Tool",
        f"Calling [{tool_name}] with params: {json.dumps(tool_input, default=str)}",
    )

    result = tool_registry.execute_tool(tool_name, tool_input)

    # Persist step record
    action_label = plan[step_num - 1] if (step_num - 1) < len(plan) else "Execute Tool"
    try:
        db_create_step(
            task_id=task_id,
            step_number=step_num,
            action=action_label,
            tool_used=tool_name,
            tool_input=tool_input,
            tool_output=result.model_dump(),
            status="SUCCESS" if result.success else "FAILED",
            error_message=result.error,
        )
    except Exception as exc:
        logger.warning(f"[DB] Step record failed: {exc}")

    state["tool_output"] = result.model_dump()
    return state


# ---------------------------------------------------------------------------
# Node: Evaluate Result
# ---------------------------------------------------------------------------

def evaluate_result_node(state: AgentState) -> AgentState:
    """
    Step 6 – Assess tool output; advance to next step, retry, or fail.
    """
    tool_output = state.get("tool_output") or {}
    success = tool_output.get("success", False)
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", settings.MAX_RETRIES)

    if success:
        new_step = state.get("current_step", 0) + 1
        state["current_step"] = new_step
        state["retry_count"] = 0
        _log_trace(
            state,
            "Evaluate Result",
            f"✅ Step completed successfully. Advancing to step {new_step + 1}.",
        )
    else:
        error = tool_output.get("error", "Unknown tool error")
        if retry_count < max_retries:
            state["retry_count"] = retry_count + 1
            _log_trace(
                state,
                "Failure Recovery",
                f"⚠️ Tool failed: {error}. "
                f"Retry {state['retry_count']}/{max_retries} with modified strategy.",
                status="RETRYING",
            )
        else:
            state["task_status"] = "FAILED"
            state["error_message"] = f"Failed after {max_retries} retries: {error}"
            _log_trace(
                state,
                "Evaluate Result",
                f"❌ Exceeded max retries ({max_retries}). Reason: {error}",
                status="FAILED",
            )

    return state


# ---------------------------------------------------------------------------
# Node: Update Memory
# ---------------------------------------------------------------------------

def update_memory_node(state: AgentState) -> AgentState:
    """
    Step 7 – Persist a task-completion memory entry to ChromaDB + SQLite.
    """
    user_id = state.get("user_id", settings.DEFAULT_USER_ID)
    user_input = state.get("user_input", "")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    summary = (
        f"[{date_str}] Completed: '{user_input[:100]}' "
        f"via intent '{state.get('intent', 'unknown')}' "
        f"({len(state.get('current_plan', []))} steps)."
    )

    try:
        memory_manager.save_preference(user_id=user_id, content=summary)
    except Exception as exc:
        logger.warning(f"[Memory] Save failed: {exc}")

    _log_trace(
        state,
        "Update Memory",
        "Task summary persisted to ChromaDB + SQLite long-term memory.",
    )
    return state


# ---------------------------------------------------------------------------
# Node: Finalize
# ---------------------------------------------------------------------------

def finalize_node(state: AgentState) -> AgentState:
    """
    Step 8 – Compose the final response and close out the DB task record.
    """
    user_input = state.get("user_input", "")
    task_id = state.get("task_id", "")
    trace = state.get("execution_trace") or []

    if state.get("task_status") != "FAILED":
        state["task_status"] = "COMPLETED"

        trace_lines = "\n".join(
            f"  [{t['timestamp']}] {t['step_name']}: {t['details']}" for t in trace
        )
        state["final_response"] = (
            f"✅ Goal accomplished: \"{user_input}\"\n\n"
            f"Execution Summary:\n{trace_lines}"
        )
        _log_trace(
            state,
            "Finalize Task",
            "All plan steps completed. Final execution report generated.",
        )
    else:
        state["final_response"] = (
            f"❌ Task failed: {state.get('error_message', 'Unknown error')}"
        )

    # Update DB record
    try:
        db_update_task_status(task_id=task_id, status=state["task_status"])
    except Exception as exc:
        logger.warning(f"[DB] Task status update failed: {exc}")

    return state
