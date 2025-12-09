"""
Base tool class/protocol.

Defines the interface all tools must implement:
- Schema definition
- Execution method
- Input validation
- Error handling conventions
"""
import os
from weave.tools.schema import ToolSchema, ToolParameter
from weave.tools.file_ops import read_file, validate_file_path, list_directory, edit_file, FileEdit

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

class ReadFileTool(Tool):
    schema = ToolSchema(
        name="read_file",
        description="Safely reads a file with error handling.",
        parameters=[
            ToolParameter(name="path", type="string", description="File path relative to working directory", required=True),
            ToolParameter(name="max_chars", type="integer", description="Max characters to read", required=False)
        ]
    )
    def execute(self, **kwargs) -> str:
        path = kwargs.get("path", "")
        max_chars = kwargs.get("max_chars")
        is_valid, file_path, error = validate_file_path(os.getcwd(), path)
        if not is_valid or file_path is None:
            return error or "Unknown error occurred"
        return read_file(file_path, max_chars)
    
class ListDirectoryTool(Tool):
    schema = ToolSchema(
        name="list_directory",
        description="Lists contents of a directory with file sizes and types.",
        parameters=[
            ToolParameter(name="path", type="string", description="Directory path relative to working directory", required=True),
            ToolParameter(name="max_depth", type="integer", description="Max depth to list", required=False)
        ]
    )
    def execute(self, **kwargs) -> str:
        path: str = kwargs.get("path", "")
        max_depth = kwargs.get("max_depth", 2)
        is_valid, dir_path, error = validate_file_path(os.getcwd(), path)
        if not is_valid or dir_path is None:
            return error or "Unknown error occurred"
        return list_directory(dir_path, max_depth)

class EditFileTool(Tool):
    schema = ToolSchema(
        name = "edit_file",
        description = "Performs targeted edits on a file without rewriting the entire content.",
        parameters = [
            ToolParameter(name="path", type="string", description="File path relative to working directory", required=True),
            ToolParameter(name="edits", type="list", description="List of edits to perform", required=True),
        ]
    )

    def execute(self, **kwargs) -> str:
        path: str = kwargs.get("path", "")
        edits_raw: list[dict] = kwargs.get("edits", [])
        edits = [
            FileEdit(
                type=e.get("type", ""),
                line_start=e.get("line_start", 0),
                line_end=e.get("line_end", 0),
                content=e.get("content", "")
            ) for e in edits_raw
        ]
        is_valid, file_path, error = validate_file_path(os.getcwd(), path)
        if not is_valid or file_path is None:
            return error or "Unknown error occurred"
        return edit_file(file_path, edits)