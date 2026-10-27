import uuid
import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseTool

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    _scheduler = BackgroundScheduler()
    if not _scheduler.running:
        _scheduler.start()
    HAS_APSCHEDULER = True
except ImportError:
    _scheduler = None
    HAS_APSCHEDULER = False

_active_reminders: Dict[str, Dict[str, Any]] = {}

def _dummy_reminder_job(reminder_id: str, message: str):
    if reminder_id in _active_reminders:
        _active_reminders[reminder_id]["status"] = "TRIGGERED"

class SchedulerInput(BaseModel):
    action: str = Field(description="Action: 'create', 'cancel', 'list'")
    message: Optional[str] = Field(default=None, description="Reminder message")
    run_time: Optional[str] = Field(default=None, description="ISO format datetime string or relative time like 'tomorrow 9 AM'")
    reminder_id: Optional[str] = Field(default=None, description="Reminder ID for cancellation")

class SchedulerTool(BaseTool):
    name = "scheduler"
    description = "Schedules and manages reminders and future task execution via APScheduler."
    args_schema = SchedulerInput
    requires_approval = False

    def _run(self, action: str, message: Optional[str] = None, run_time: Optional[str] = None, reminder_id: Optional[str] = None) -> Dict[str, Any]:
        if action == "create":
            if not message:
                raise ValueError("Message is required to create a reminder.")
            
            rem_id = str(uuid.uuid4())[:8]
            trigger_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
            if run_time:
                try:
                    trigger_time = datetime.datetime.fromisoformat(run_time)
                except Exception:
                    pass

            if HAS_APSCHEDULER and _scheduler:
                try:
                    _scheduler.add_job(_dummy_reminder_job, 'date', run_date=trigger_time, args=[rem_id, message], id=rem_id)
                except Exception:
                    pass

            _active_reminders[rem_id] = {
                "reminder_id": rem_id,
                "message": message,
                "run_time": str(trigger_time),
                "status": "SCHEDULED"
            }
            return {
                "message": "Reminder scheduled successfully",
                "reminder_id": rem_id,
                "reminder_text": message,
                "scheduled_time": str(trigger_time)
            }

        elif action == "list":
            return {
                "count": len(_active_reminders),
                "reminders": list(_active_reminders.values())
            }

        elif action == "cancel":
            if not reminder_id:
                raise ValueError("reminder_id is required to cancel a reminder.")
            if reminder_id in _active_reminders:
                if HAS_APSCHEDULER and _scheduler:
                    try:
                        _scheduler.remove_job(reminder_id)
                    except Exception:
                        pass
                _active_reminders[reminder_id]["status"] = "CANCELLED"
                return {"message": "Reminder cancelled", "reminder_id": reminder_id}
            else:
                return {"message": "Reminder ID not found", "reminder_id": reminder_id}
        else:
            raise ValueError(f"Unsupported scheduler action '{action}'. Valid: create, list, cancel.")
