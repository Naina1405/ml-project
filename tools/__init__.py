from tools.base import BaseTool, ToolResult
from tools.registry import tool_registry, ToolRegistry
from tools.web_search import WebSearchTool
from tools.task_manager import TaskManagerTool
from tools.scheduler import SchedulerTool
from tools.calendar_tool import CalendarTool
from tools.email_tool import EmailTool
from tools.memory_tool import MemoryTool

# Auto-register default tools
web_search_tool = WebSearchTool()
task_manager_tool = TaskManagerTool()
scheduler_tool = SchedulerTool()
calendar_tool = CalendarTool()
email_tool = EmailTool()
memory_tool = MemoryTool()

for t in [web_search_tool, task_manager_tool, scheduler_tool, calendar_tool, email_tool, memory_tool]:
    tool_registry.register(t)

__all__ = [
    "BaseTool", "ToolResult", "tool_registry", "ToolRegistry",
    "web_search_tool", "task_manager_tool", "scheduler_tool",
    "calendar_tool", "email_tool", "memory_tool"
]
