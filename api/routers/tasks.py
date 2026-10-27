from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from db.crud import db_list_tasks, db_delete_task
from api.schemas import TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_tasks(user_id: str = "user_default"):
    """
    Returns list of all user tasks with status and creation timestamps.
    """
    return db_list_tasks(user_id=user_id)

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """
    Deletes a task by ID.
    """
    success = db_delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return {"message": f"Task '{task_id}' deleted successfully."}
