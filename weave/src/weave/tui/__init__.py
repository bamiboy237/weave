"""
Weave Terminal User Interface.

Built with Textual - a modern TUI framework for Python.

Provides:
- Multi-screen navigation (home, chat, help)
- Theme system with 8+ built-in themes
- Vim-style keyboard navigation
- Streaming message display
- Chat history management
"""

from weave.tui.app import Weave, main

__all__ = ["Weave", "main"]
