from typing import Dict, Any
from tools.registry import tool_registry

class Baseline1Chatbot:
    """
    Baseline 1: LLM Chatbot without tools.
    Generates text responses but cannot execute actions.
    """
    def run(self, prompt: str) -> Dict[str, Any]:
        return {
            "prompt": prompt,
            "response": f"I am a basic conversational chatbot. I understand you want to: '{prompt}', but I cannot execute tools.",
            "tool_calls": [],
            "completed": False
        }

class Baseline2DirectTools:
    """
    Baseline 2: LLM + Direct Tools without planning loop, state graph, failure recovery, or approval gate.
    """
    def run(self, prompt: str) -> Dict[str, Any]:
        # Direct heuristic execution without graph retry
        tool_name = "web_search"
        if "email" in prompt.lower():
            tool_name = "email"
            res = tool_registry.execute_tool("email", {"action": "send", "recipient": "prof.smith@edu", "subject": "Update", "body": prompt})
        elif "reminder" in prompt.lower() or "schedule" in prompt.lower():
            tool_name = "scheduler"
            res = tool_registry.execute_tool("scheduler", {"action": "create", "message": prompt})
        else:
            res = tool_registry.execute_tool("web_search", {"query": prompt, "num_results": 3})

        return {
            "prompt": prompt,
            "tool_used": tool_name,
            "tool_result": res.model_dump(),
            "completed": res.success
        }
