from typing import List, Dict, Any, Optional

class ShortTermMemory:
    """
    Short-Term Memory maintains transient task state, conversation history, 
    intermediate tool observations, and active step reasoning.
    """
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.scratchpad: List[str] = []
        self.context: Dict[str, Any] = {}

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def add_observation(self, tool_name: str, result: Any):
        self.scratchpad.append(f"Tool [{tool_name}] returned: {result}")

    def update_context(self, key: str, value: Any):
        self.context[key] = value

    def get_summary(self) -> str:
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.history[-5:]])
        scratchpad_str = "\n".join(self.scratchpad[-5:])
        return f"Recent Conversation:\n{history_str}\n\nRecent Observations:\n{scratchpad_str}"

    def clear(self):
        self.history.clear()
        self.scratchpad.clear()
        self.context.clear()
