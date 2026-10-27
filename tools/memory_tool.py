from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseTool
from memory.memory_manager import memory_manager

class MemoryInput(BaseModel):
    action: str = Field(description="Action: 'save', 'retrieve', 'delete'")
    content: Optional[str] = Field(default=None, description="Memory content string to save or search query")
    memory_id: Optional[str] = Field(default=None, description="ID of memory for deletion")
    user_id: str = Field(default="user_default", description="Owner user ID")

class MemoryTool(BaseTool):
    name = "memory"
    description = "Saves user preferences to long-term vector memory, retrieves context, or deletes memories."
    args_schema = MemoryInput
    requires_approval = False

    def _run(self, action: str, content: Optional[str] = None, memory_id: Optional[str] = None, user_id: str = "user_default") -> Dict[str, Any]:
        if action == "save":
            if not content:
                raise ValueError("Content is required to save a memory.")
            mid = memory_manager.save_preference(user_id=user_id, content=content)
            return {"message": "Memory saved to long-term storage", "memory_id": mid, "content": content}

        elif action == "retrieve":
            query = content or ""
            memories = memory_manager.retrieve_relevant_memories(user_id=user_id, query=query, limit=5)
            return {"query": query, "count": len(memories), "memories": memories}

        elif action == "delete":
            if not memory_id:
                raise ValueError("memory_id is required to delete a memory.")
            success = memory_manager.delete_memory(memory_id)
            if success:
                return {"message": f"Memory '{memory_id}' deleted successfully"}
            return {"message": f"Memory '{memory_id}' not found or could not be deleted"}

        else:
            raise ValueError(f"Unsupported memory action '{action}'. Valid: save, retrieve, delete.")
