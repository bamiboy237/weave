"""
Weave data models for the TUI.

Simplified models for chat data without external LLM dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal, TypedDict


class MessageContent(TypedDict, total=False):
    """Message content structure compatible with LLM message formats."""
    content: str
    role: Literal["system", "user", "assistant", "tool", "function"]


@dataclass
class WeaveModel:
    """Represents a local LLM model configuration."""
    id: str
    name: str
    display_name: str | None = None
    provider: str = "local"
    
    @property
    def lookup_key(self) -> str:
        return self.id


# Default model placeholder - will be replaced when llama.cpp integration is added
DEFAULT_MODEL = WeaveModel(
    id="local",
    name="Local Model",
    display_name="Local LLM",
    provider="llama.cpp",
)


@dataclass
class ChatMessage:
    """A single message in a chat conversation."""
    message: MessageContent
    timestamp: datetime | None
    model: WeaveModel

    @property
    def role(self) -> str:
        return self.message.get("role", "user")

    @property
    def content(self) -> str:
        return self.message.get("content", "")


@dataclass
class ChatData:
    """Represents a chat conversation."""
    id: int | None  # Can be None before the chat gets assigned ID
    model: WeaveModel
    title: str | None
    create_timestamp: datetime | None
    messages: list[ChatMessage] = field(default_factory=list)

    @property
    def short_preview(self) -> str:
        """Get a short preview of the first user message."""
        first_message = self.first_user_message
        if first_message:
            content = first_message.message.get("content", "")
            if content and isinstance(content, str):
                if len(content) > 77:
                    return content[:77] + "..."
                return content
        return ""

    @property
    def system_prompt(self) -> ChatMessage | None:
        """Get the system prompt message."""
        if self.messages:
            return self.messages[0]
        return None

    @property
    def first_user_message(self) -> ChatMessage | None:
        """Get the first user message."""
        if len(self.messages) > 1:
            return self.messages[1]
        return None

    @property
    def non_system_messages(self) -> list[ChatMessage]:
        """Get all messages except the system prompt."""
        return self.messages[1:] if self.messages else []

    @property
    def update_time(self) -> datetime:
        """Get the timestamp of the last message."""
        if self.messages:
            message_timestamp = self.messages[-1].timestamp
            if message_timestamp:
                return message_timestamp.astimezone().replace(tzinfo=UTC)
        return datetime.now(UTC)

