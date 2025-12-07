"""
Tool registry pattern implementation.

Provides a central registry where tools register themselves via decorators.
The registry:
- Collects tool schemas for LLM context
- Dispatches execution to correct tool implementations
- Validates arguments against schemas before execution
- Handles tool discovery at startup
"""
from weave.tools.schema import ToolSchema
from typing import Callable

class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.schemas  = {}

    def register(self, schema: ToolSchema) -> Callable:
        """Decorator to register a tool with its schema."""
        def decorator(func):
            self.tools[schema.name] = func
            self.schemas[schema.name] = schema
            return func
        return decorator

    def get_schema(self, name: str) -> ToolSchema | None:
        """Get schema for a tool."""
        schema = (self.schemas).get(name)
        if schema is None:
            raise KeyError(f'Schema "{name}" not found in registry')
        return schema

    def get_all_schemas(self) -> list[ToolSchema]:
        """Get all registered tool schemas."""
        return list(self.schemas.values())
        

    def execute(self, name: str, args: dict) -> any | None:
        """Execute a registered tool."""
        pass