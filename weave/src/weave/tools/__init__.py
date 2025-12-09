"""
Tool implementations.

Contains all tools available to the agent:
- File operations (read, write, list, search)
- HTTP requests
- Web scraping
- Shell commands (whitelisted)

Tools self-register with the core registry via decorators.
"""

from weave.core.registry import ToolRegistry
from weave.tools.base import ReadFileTool, ListDirectoryTool, EditFileTool

# global tool registry
registry = ToolRegistry()

# register tools
@registry.register(ReadFileTool.schema)
def read_file_tool(**kwargs) -> str:
    return ReadFileTool().execute(**kwargs)

@registry.register(ListDirectoryTool.schema)
def list_directory_tool(**kwargs) -> str:
    return ListDirectoryTool().execute(**kwargs)

@registry.register(EditFileTool.schema)
def edit_file_tool(**kwargs) -> str:
    return EditFileTool().execute(**kwargs)