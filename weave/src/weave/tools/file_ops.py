"""
File operation tools.

Implements safe file system operations:
- read_file: Read file contents as string
- write_file: Create or overwrite files
- list_directory: List files and subdirectories
- search_files: Find text patterns across files

All operations are sandboxed to prevent path traversal attacks.
Paths are resolved relative to a configured working directory.
"""

