from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from api.schemas import MemoryCreateRequest
from memory.memory_manager import memory_manager

router = APIRouter(prefix="/memory", tags=["Memory"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_memories(user_id: str = "user_default"):
    """
    Returns list of stored long-term memories for a user.
    """
    return memory_manager.list_user_memories(user_id=user_id)

@router.post("")
async def create_memory(req: MemoryCreateRequest):
    """
    Saves a new user preference to long-term memory.
    """
    mid = memory_manager.save_preference(user_id=req.user_id, content=req.content)
    return {"message": "Memory saved successfully", "memory_id": mid, "content": req.content}

@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """
    Deletes a memory item from ChromaDB & SQLite vector store.
    """
    success = memory_manager.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Memory '{memory_id}' not found.")
    return {"message": f"Memory '{memory_id}' deleted successfully."}
