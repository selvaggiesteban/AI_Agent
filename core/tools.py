from typing import Any, Dict, List, Optional, Callable
from core.logger import logger

class Tool:
    """
    Base class for all AI Agent capabilities.
    Every tool must define its name, description, and execution logic.
    """
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "No description provided."

    def execute(self, **kwargs) -> Any:
        """
        Executes the tool logic.
        Args are passed as keyword arguments from the Orchestrator.
        """
        raise NotImplementedError("Each tool must implement the execute() method.")

class ToolRegistry:
    """
    Registry to manage and discover available tools.
    """
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Registers a tool instance."""
        self._tools[tool.name] = tool
        logger.info(f"Tool registered: {tool.name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """Retrieves a tool by its name."""
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        """Returns a list of all registered tools and their descriptions for the LLM."""
        return [
            {"name": name, "description": tool.description}
            for name, tool in self._tools.items()
        ]

# Global instance for the project
registry = ToolRegistry()
