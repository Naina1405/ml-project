import logging
from typing import Dict, List, Optional, Any
from tools.base import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for all agent tools.

    Usage
    -----
    Register tools at import time via tools/__init__.py:

        from tools.registry import tool_registry
        from tools.web_search import WebSearchTool
        tool_registry.register(WebSearchTool())

    The agent nodes resolve tools by name at runtime.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance. Raises ValueError on duplicate names."""
        if tool.name in self._tools:
            logger.warning(
                f"[ToolRegistry] Overwriting existing tool '{tool.name}'. "
                "Ensure this is intentional."
            )
        self._tools[tool.name] = tool
        logger.debug(f"[ToolRegistry] Registered tool '{tool.name}'")

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Return the tool with the given name, or None if not found."""
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return a list of schema dicts for all registered tools."""
        return [t.get_schema() for t in self._tools.values()]

    @property
    def tool_names(self) -> List[str]:
        """Convenience property returning all registered tool names."""
        return list(self._tools.keys())

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute_tool(self, name: str, kwargs: Dict[str, Any]) -> ToolResult:
        """
        Look up and execute a tool by name.

        Returns a failed ToolResult (instead of raising) when the tool is
        not found, so the agent can handle the failure gracefully.
        """
        tool = self.get_tool(name)
        if not tool:
            err = f"Tool '{name}' not found. Available: {self.tool_names}"
            logger.error(f"[ToolRegistry] {err}")
            return ToolResult(success=False, error=err, tool_name=name)
        return tool.execute(**kwargs)

    def __len__(self) -> int:
        return len(self._tools)

    def __repr__(self) -> str:
        return f"ToolRegistry({self.tool_names})"


# Module-level singleton
tool_registry = ToolRegistry()
