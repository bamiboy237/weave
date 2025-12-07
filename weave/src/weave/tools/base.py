"""
Base tool class/protocol.

Defines the interface all tools must implement:
- Schema definition
- Execution method
- Input validation
- Error handling conventions
"""
from weave.tools.schema import ToolSchema

class Tool:
    """Base class for all tools."""
    schema: ToolSchema

    def execute(self, **kwargs) -> str:
        """
        Execute the tool with the given arguments.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            str: Result of execution or error message
            
        Raises:
            NotImplementedError: Subclasses must implement this
        """
        raise NotImplementedError("Subclasses must implement execute()")