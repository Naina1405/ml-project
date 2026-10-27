import os
import uuid
from typing import List, Dict, Any, Optional
from config.settings import settings
from db.crud import db_add_memory, db_list_memories, db_delete_memory

class LongTermMemory:
    """
    Long-Term Memory using ChromaDB for vector retrieval and SQLite for structured metadata storage.
    """
    def __init__(self):
        self.chroma_collection = None
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(settings.CHROMA_PERSIST_DIR))
            self.chroma_collection = client.get_or_create_collection(name="user_memories")
        except Exception as e:
            self.chroma_collection = None

    def add_memory(self, user_id: str, content: str, memory_type: str = "preference") -> str:
        memory_id = db_add_memory(user_id=user_id, content=content, memory_type=memory_type)

        if self.chroma_collection:
            try:
                self.chroma_collection.add(
                    ids=[memory_id],
                    documents=[content],
                    metadatas=[{"user_id": user_id, "memory_type": memory_type}]
                )
            except Exception:
                pass

        return memory_id

    def retrieve_memories(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        memories = []
        if self.chroma_collection and query.strip():
            try:
                results = self.chroma_collection.query(
                    query_texts=[query],
                    n_results=limit,
                    where={"user_id": user_id}
                )
                if results and results.get("documents") and results["documents"][0]:
                    for idx, doc in enumerate(results["documents"][0]):
                        mem_id = results["ids"][0][idx]
                        meta = results["metadatas"][0][idx] if results.get("metadatas") else {}
                        memories.append({
                            "memory_id": mem_id,
                            "content": doc,
                            "memory_type": meta.get("memory_type", "preference"),
                            "score": 1.0
                        })
                    return memories
            except Exception:
                pass

        # Fallback to SQLite
        records = db_list_memories(user_id=user_id)
        query_words = set(query.lower().split()) if query else set()
        
        scored_mems = []
        for r in records:
            score = 0.5
            if query_words:
                content_words = set(r["content"].lower().split())
                overlap = len(query_words.intersection(content_words))
                if overlap > 0:
                    score += 0.5 * (overlap / len(query_words))
            scored_mems.append((score, {
                "memory_id": r["memory_id"],
                "content": r["content"],
                "memory_type": r["memory_type"],
                "created_at": str(r.get("created_at", ""))
            }))

        scored_mems.sort(key=lambda x: x[0], reverse=True)
        return [m[1] for m in scored_mems[:limit]]

    def delete_memory(self, memory_id: str) -> bool:
        success = db_delete_memory(memory_id)
        if self.chroma_collection and success:
            try:
                self.chroma_collection.delete(ids=[memory_id])
            except Exception:
                pass
        return success

    def list_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        return db_list_memories(user_id)

