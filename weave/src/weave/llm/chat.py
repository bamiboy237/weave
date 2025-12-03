"""
Chat completion formatting.

Handles conversation structure for the LLM:
- Message formatting (system, user, assistant roles)
- Chat template application (ChatML, Qwen format, etc.)
- Multi-turn conversation history
- Tool call message formatting
"""
from __future__ import annotations

from weave.tui.models import ChatMessage

def format_messages_for_llm(messages: list[ChatMessage]) -> list[dict[str, str]]:
    """Format messages for LLM consumption."""
    formatted = []
    for msg in messages:
        role = msg.role
        content = msg.content
        formatted.append({"role": role, "content": content})
    return formatted