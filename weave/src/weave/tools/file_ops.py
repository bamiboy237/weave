"""
File operation tools.

Implements safe file system operations:
- read_file: Read file contents as string
- write_file: Create or overwrite files
- edit_file: Perform targeted edits on files
- list_directory: List files and subdirectories
- search_files: Find text patterns across files

All operations are sandboxed to prevent path traversal attacks.
Paths are resolved relative to a configured working directory.
"""
from pathlib import Path
from typing import Optional
import re
from dataclasses import dataclass


@dataclass
class FileEdit:
    """Represents a single file edit operation"""
    type: str  # 'insert', 'replace', 'delete', 'append'
    line_start: int
    line_end: Optional[int] = None
    content: str = ""


def validate_file_path(working_dir: str, file_path: str) -> tuple[bool, Optional[Path], Optional[str]]:
    """
    Validates that a file path is within the safe working directory.
    Returns:
        Tuple of (is_valid, resolved_path, error_message)
    """
    safe_zone: Path = Path(working_dir).resolve()
    file: Path = (safe_zone / file_path).resolve()
    if not file.is_relative_to(safe_zone):
        return (
            False,
            None,
            f'Error: Cannot access "{file_path}" as it is outside the permitted working directory',
        )
    return (True, file, None)


def read_file(file: Path, max_chars: Optional[int] = None) -> str:
    """
    Safely reads a file with error handling.
    Args:
        file: Path object to read
        max_chars: Optional character limit for truncation
    """
    try:
        with file.open("r", encoding="utf-8") as f:
            contents: str = f.read()
            if max_chars and len(contents) > max_chars:
                contents = contents[:max_chars]
                contents += f"\n\n... File '{file}' truncated at {max_chars} characters"
        return contents
    except OSError as e:
        return f"Error accessing '{file}': {e}"
    

def write_file(file: Path, contents: str) -> str: 
    """
    Safely writes content to a file with error handling.
    Args:
        file: Path object to write to
        contents: Content to write
    """
    try: 
        file.parent.mkdir(parents=True, exist_ok=True)  # create parent dirs if non-existent
        with file.open("w", encoding="utf-8") as f:
            f.write(contents)
        return f"Successfully wrote to '{file}'"
    except OSError as e:
        return f"Error writing to '{file}': {e}"


def edit_file(file: Path, edits: list[FileEdit]) -> str:
    """
    Performs targeted edits on a file without rewriting the entire content.
    
    Args:
        file: Path object to edit
        edits: List of FileEdit operations to apply
        
    Returns:
        Success/error message
    """
    try:
        with file.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        
        sorted_edits = sorted(edits, key=lambda e: e.line_start, reverse=True)
        
        for edit in sorted_edits:
            if edit.type == 'insert':
                lines.insert(edit.line_start - 1, edit.content + '\n')
                
            elif edit.type == 'replace':
                if edit.line_end is None:
                    edit.line_end = edit.line_start
                new_lines = [line + '\n' for line in edit.content.split('\n') if line or edit.content == '']
                lines[edit.line_start - 1:edit.line_end] = new_lines
                
            elif edit.type == 'delete':
                if edit.line_end is None:
                    edit.line_end = edit.line_start
                del lines[edit.line_start - 1:edit.line_end]
                
            elif edit.type == 'append':
                lines.append(edit.content + '\n')
        
        with file.open("w", encoding="utf-8") as f:
            f.writelines(lines)
        
        return f"Successfully edited '{file}' with {len(edits)} operation(s)"
        
    except OSError as e:
        return f"Error editing '{file}': {e}"
    except IndexError as e:
        return f"Error: Invalid line number in edit operation for '{file}': {e}"


def insert_at_line(file: Path, file_path: str, line_num: int, content: str) -> str:
    """
    Convenience function to insert content at a specific line.
    
    Args:
        file: Path object to edit
        file_path: Original file path string (for messages)
        line_num: Line number to insert before (1-indexed)
        content: Content to insert
    """
    return edit_file(file, [FileEdit('insert', line_num, content=content)])


def replace_lines(file: Path, start: int, end: int, content: str) -> str:
    """
    Convenience function to replace a range of lines.
    
    Args:
        file: Path object to edit
        file_path: Original file path string (for messages)
        start: Starting line number (1-indexed, inclusive)
        end: Ending line number (1-indexed, inclusive)
        content: New content to replace with
    """
    return edit_file(file, [FileEdit('replace', start, end, content)])


def list_directory(directory: Path, max_depth: int = 2) -> str:
    """
    Lists contents of a directory with file sizes and types.
    
    Args:
        directory: Path object to list
        dir_path: Original directory path string (for messages)
        max_depth: Maximum recursion depth for subdirectories
    """
    try:
        if not directory.exists():
            return f"Error: Directory '{str(directory)}' does not exist"
        
        if not directory.is_dir():
            return f"Error: '{str(directory)}' is not a directory"
        
        result = [f"Contents of '{str(directory)}':"]
        
        def list_recursive(path: Path, depth: int, prefix: str = ""):
            if depth > max_depth:
                return
            
            indent = "  " * depth
            try:
                items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                for item in items:
                    if item.is_dir():
                        result.append(f"{indent}📁 {item.name}/")
                        list_recursive(item, depth + 1, prefix + "  ")
                    else:
                        size = item.stat().st_size
                        size_str = format_file_size(size)
                        result.append(f"{indent}📄 {item.name} ({size_str})")
            except PermissionError:
                result.append(f"{indent}⚠️  [Permission Denied]")
        
        list_recursive(directory, 0)
        return "\n".join(result)
        
    except OSError as e:
        return f"Error listing directory '{str(directory)}': {e}"


def search_files(directory: Path, pattern: str, 
                file_pattern: str = "*", max_results: int = 50) -> str:
    """
    Searches for a text pattern across files in a directory.
    
    Args:
        directory: Path object to search in
        dir_path: Original directory path string (for messages)
        pattern: Text pattern to search for (supports regex)
        file_pattern: Glob pattern for files to search (e.g., "*.py")
        max_results: Maximum number of results to return
    """
    try:
        if not directory.exists() or not directory.is_dir():
            return f"Error: '{str(directory)}' is not a valid directory"
        
        results = []
        regex = re.compile(pattern, re.IGNORECASE)
        
        for file_path in directory.rglob(file_pattern):
            if not file_path.is_file():
                continue
            
            try:
                with file_path.open("r", encoding="utf-8", errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            relative_path = file_path.relative_to(directory)
                            results.append(f"{relative_path}:{line_num}: {line.strip()}")
                            
                            if len(results) >= max_results:
                                results.append(f"\n... Showing first {max_results} results")
                                return "\n".join(results)
            except Exception:
                # Skip files that can't be read
                continue
        
        if not results:
            return f"No matches found for pattern '{pattern}' in {str(directory)}"
        
        return "\n".join(results)
        
    except OSError as e:
        return f"Error searching in '{str(directory)}': {e}"


def get_file_info(file: Path, file_path: str) -> str:
    """
    Gets information about a file (size, type, line count).
    
    Args:
        file: Path object to get info about
        file_path: Original file path string (for messages)
    """
    try:
        if not file.exists():
            return f"Error: File '{file_path}' does not exist"
        
        stat = file.stat()
        size = format_file_size(stat.st_size)
        
        info = [f"File: {file_path}"]
        info.append(f"Size: {size}")
        info.append(f"Type: {file.suffix or 'no extension'}")
        
        # Try to count lines if it's a text file
        try:
            with file.open("r", encoding="utf-8") as f:
                line_count = sum(1 for _ in f)
            info.append(f"Lines: {line_count}")
        except Exception:
            info.append("Lines: [binary file]")
        
        return "\n".join(info)
        
    except OSError as e:
        return f"Error getting info for '{file_path}': {e}"


def format_file_size(size_bytes: float) -> str:
    """Formats file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
