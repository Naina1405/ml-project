import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseTool
from db.crud import db_create_task, db_list_tasks, db_update_task_status, db_delete_task

class TaskManagerInput(BaseModel):
    action: str = Field(description="Action to perform: 'create', 'list', 'update', 'delete'")
    title: Optional[str] = Field(default=None, description="Task title or goal description")
    task_id: Optional[str] = Field(default=None, description="ID of task for update or delete")
    status: Optional[str] = Field(default=None, description="Updated status: PENDING, COMPLETED, FAILED")
    user_id: str = Field(default="user_default", description="Owner user ID")

class TaskManagerTool(BaseTool):
    name = "task_manager"
    description = "Manages personal tasks. Actions: create, list, update, delete."
    args_schema = TaskManagerInput
    requires_approval = False

    def _run(self, action: str, title: Optional[str] = None, task_id: Optional[str] = None, 
             status: Optional[str] = None, user_id: str = "user_default") -> Dict[str, Any]:
        if action == "create":
            if not title:
                raise ValueError("Title is required for creating a task.")
            res = db_create_task(user_id=user_id, goal_prompt=title, status="PENDING")
            return {"message": "Task created successfully", "task_id": res["task_id"], "title": title, "status": "PENDING"}

        elif action == "list":
            tasks = db_list_tasks(user_id=user_id)
            return {
                "count": len(tasks),
                "tasks": [{"task_id": t["task_id"], "title": t["goal_prompt"], "status": t["status"], "created_at": str(t.get("created_at", ""))} for t in tasks]
            }

        elif action == "update":
            if not task_id:
                raise ValueError("Task ID is required for updating.")
            st = status or "COMPLETED"
            ok = db_update_task_status(task_id=task_id, status=st)
            if not ok:
                raise ValueError(f"Task ID '{task_id}' not found.")
            return {"message": "Task updated successfully", "task_id": task_id, "status": st}

        elif action == "delete":
            if not task_id:
                raise ValueError("Task ID is required for deleting.")
            ok = db_delete_task(task_id=task_id)
            if not ok:
                raise ValueError(f"Task ID '{task_id}' not found.")
            return {"message": "Task deleted successfully", "task_id": task_id}

        else:
            raise ValueError(f"Unsupported action '{action}'. Valid actions: create, list, update, delete.")
