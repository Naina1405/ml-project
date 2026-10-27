import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

class UserBase(BaseModel):
    name: str = "Default User"

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    user_id: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class TaskStepBase(BaseModel):
    step_number: int
    action: str
    tool_used: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None
    status: str = "EXECUTING"
    error_message: Optional[str] = None

class TaskStepResponse(TaskStepBase):
    step_id: str
    task_id: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    goal_prompt: str
    user_id: Optional[str] = "user_default"

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    task_id: str
    status: str
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    steps: List[TaskStepResponse] = []

    class Config:
        from_attributes = True

class MemoryBase(BaseModel):
    content: str
    memory_type: str = "preference"

class MemoryCreate(MemoryBase):
    user_id: Optional[str] = "user_default"

class MemoryResponse(MemoryBase):
    memory_id: str
    user_id: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True
