"""
Weave - An on-device coding agent with local LLM inference.

This package provides a fully offline coding assistant with:
- Local LLM inference via llama-cpp-python
- Persistent memory across sessions
- Extensible tool system
- Tool chains for complex workflows
- Textual-based terminal UI with theming support
"""

from weave.tui import Weave, main

__all__ = ["Weave", "main"]
