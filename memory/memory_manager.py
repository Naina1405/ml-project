from typing import List, Dict, Any, Optional
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory

class MemoryManager:
    """
    Unified Memory Manager bridging Short-Term state and Long-Term persistent store.
    """
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()

    def save_preference(self, user_id: str, content: str) -> str:
        return self.long_term.add_memory(user_id=user_id, content=content, memory_type="preference")

    def retrieve_relevant_memories(self, user_id: str, query: str, limit: int = 3) -> List[str]:
        results = self.long_term.retrieve_memories(user_id=user_id, query=query, limit=limit)
        return [r["content"] for r in results]

    def delete_memory(self, memory_id: str) -> bool:
        return self.long_term.delete_memory(memory_id)

    def list_user_memories(self, user_id: str) -> List[Dict[str, Any]]:
        return self.long_term.list_all_memories(user_id)

memory_manager = MemoryManager()
