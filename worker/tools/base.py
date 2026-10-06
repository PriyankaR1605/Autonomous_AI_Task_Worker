from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    output: str
    data: Dict[str, Any] = {}
    error: str = ""
    screenshot_path: str = ""

class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool action and return a standardized ToolResult."""
        pass
