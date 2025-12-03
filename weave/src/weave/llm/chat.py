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
from weave.tui.models import MessageContent
from typing import Sequence, cast

def format_messages_for_llm(messages: Sequence[ChatMessage | MessageContent]) -> list[MessageContent]:
    """Format messages for LLM consumption."""
    formatted: list[MessageContent] = []
    for msg in messages:
        if isinstance(msg, ChatMessage):
            role = msg.role
            content = msg.content
        else:
            msg = cast(MessageContent, msg)
            role = msg.get("role", "user")
            content = msg.get("content", "")
        formatted.append({"role": role, "content": content})  # type: ignore[typeddict-item]
    return formatted