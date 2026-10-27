from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AgentRunRequest(BaseModel):
    user_input: str = Field(..., description="High-level natural language goal prompt")
    user_id: str = Field(default="user_default", description="User identifier")

class AgentApprovalRequest(BaseModel):
    task_id: str = Field(..., description="Target task ID awaiting approval")
    approved: bool = Field(..., description="True to approve execution, False to reject")

class TaskResponse(BaseModel):
    task_id: str
    user_id: str
    goal_prompt: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    steps: List[Dict[str, Any]] = []

class MemoryResponse(BaseModel):
    memory_id: str
    user_id: str
    content: str
    memory_type: str
    created_at: str

class MemoryCreateRequest(BaseModel):
    content: str
    memory_type: str = "preference"
    user_id: str = "user_default"
