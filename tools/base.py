import time
import logging
import traceback
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    """
    Standardised return type for every tool invocation.

    Attributes
    ----------
    success          : True when _run() completed without raising an exception.
    data             : The structured payload returned by _run().
    error            : Human-readable error message (None on success).
    execution_time_ms: Wall-clock execution time in milliseconds.
    tool_name        : Name of the tool that produced this result.
    """

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    tool_name: str = ""


class BaseTool:
    """
    Abstract base class for all agent tools.

    Subclasses must define:
      - name          : Unique snake_case identifier.
      - description   : One-sentence capability description (shown in UI/API).
      - args_schema   : Pydantic model that validates and documents accepted kwargs.
      - _run(**kwargs): Core implementation returning a JSON-serialisable value.
    """

    name: str = "base_tool"
    description: str = "Base Tool — override this description in subclasses."
    args_schema: Type[BaseModel] = BaseModel
    requires_approval: bool = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def execute(self, **kwargs) -> ToolResult:
        """
        Validate arguments, call _run(), and wrap the result in a ToolResult.
        Exceptions are caught, logged, and returned as failed ToolResults.
        """
        start = time.perf_counter()
        try:
            validated = self.args_schema(**kwargs)
            data = self._run(**validated.model_dump())
            elapsed = (time.perf_counter() - start) * 1000
            logger.debug(f"[{self.name}] succeeded in {elapsed:.1f} ms")
            return ToolResult(
                success=True,
                data=data,
                execution_time_ms=round(elapsed, 2),
                tool_name=self.name,
            )
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            err_msg = f"{type(exc).__name__}: {exc}"
            logger.error(f"[{self.name}] failed in {elapsed:.1f} ms — {err_msg}")
            logger.debug(traceback.format_exc())
            return ToolResult(
                success=False,
                error=err_msg,
                execution_time_ms=round(elapsed, 2),
                tool_name=self.name,
            )

    # ------------------------------------------------------------------
    # Subclass contract
    # ------------------------------------------------------------------

    def _run(self, **kwargs) -> Any:
        """Override in subclasses to implement the tool's core logic."""
        raise NotImplementedError(f"Tool '{self.name}' must implement _run().")

    # ------------------------------------------------------------------
    # Schema / metadata
    # ------------------------------------------------------------------

    def get_schema(self) -> Dict[str, Any]:
        """Return a JSON-serialisable schema dict for API/UI introspection."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.args_schema.model_json_schema(),
            "requires_approval": self.requires_approval,
        }
