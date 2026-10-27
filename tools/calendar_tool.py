import uuid
import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseTool

# In-memory calendar database
_calendar_events: Dict[str, Dict[str, Any]] = {}

class CalendarInput(BaseModel):
    action: str = Field(description="Action: 'create', 'list', 'update', 'delete'")
    title: Optional[str] = Field(default=None, description="Event title")
    start_time: Optional[str] = Field(default=None, description="Start date/time ISO string")
    end_time: Optional[str] = Field(default=None, description="End date/time ISO string")
    description: Optional[str] = Field(default=None, description="Event details")
    event_id: Optional[str] = Field(default=None, description="Event ID for update/delete")

class CalendarTool(BaseTool):
    name = "calendar"
    description = "Manages user calendar events (create, list, update, delete)."
    args_schema = CalendarInput
    requires_approval = False

    def _run(self, action: str, title: Optional[str] = None, start_time: Optional[str] = None, 
             end_time: Optional[str] = None, description: Optional[str] = None, 
             event_id: Optional[str] = None) -> Dict[str, Any]:
        if action == "create":
            if not title:
                raise ValueError("Title is required to create a calendar event.")
            eid = str(uuid.uuid4())[:8]
            st = start_time or str(datetime.datetime.now() + datetime.timedelta(days=1))
            et = end_time or str(datetime.datetime.now() + datetime.timedelta(days=1, hours=1))
            
            event = {
                "event_id": eid,
                "title": title,
                "start_time": st,
                "end_time": et,
                "description": description or ""
            }
            _calendar_events[eid] = event
            return {"message": "Calendar event created", "event": event}

        elif action == "list":
            return {
                "count": len(_calendar_events),
                "events": list(_calendar_events.values())
            }

        elif action == "delete":
            if not event_id:
                raise ValueError("event_id is required to delete an event.")
            if event_id in _calendar_events:
                del _calendar_events[event_id]
                return {"message": f"Event '{event_id}' deleted successfully"}
            raise ValueError(f"Event ID '{event_id}' not found.")

        else:
            raise ValueError(f"Unsupported action '{action}'. Valid: create, list, delete.")
