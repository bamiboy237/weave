"""
Weave chats manager - in-memory storage stub.

TODO: Replace with SQLite persistence in Phase 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from weave.tui.models import ChatData, ChatMessage


@dataclass
class ChatsManager:
    """In-memory chat storage manager.
    
    This is a stub implementation that stores chats in memory.
    Replace with SQLite persistence when implementing Phase 4.
    """
    
    # Class-level storage for chats (in-memory)
    _chats: dict[int, ChatData] = None  # type: ignore
    _next_id: int = 1

    def __post_init__(self) -> None:
        if ChatsManager._chats is None:
            ChatsManager._chats = {}

    @staticmethod
    def _ensure_storage() -> None:
        """Ensure the storage dict exists."""
        if ChatsManager._chats is None:
            ChatsManager._chats = {}

    @staticmethod
    async def all_chats() -> list[ChatData]:
        """Get all non-archived chats."""
        ChatsManager._ensure_storage()
        # Return chats sorted by most recent first
        chats = list(ChatsManager._chats.values())
        chats.sort(key=lambda c: c.update_time, reverse=True)
        return chats

    @staticmethod
    async def get_chat(chat_id: int) -> ChatData:
        """Get a specific chat by ID."""
        ChatsManager._ensure_storage()
        chat = ChatsManager._chats.get(chat_id)
        if not chat:
            raise RuntimeError(f"Chat with ID {chat_id} not found.")
        return chat

    @staticmethod
    async def rename_chat(chat_id: int, new_title: str) -> None:
        """Rename a chat."""
        ChatsManager._ensure_storage()
        chat = ChatsManager._chats.get(chat_id)
        if chat:
            chat.title = new_title

    @staticmethod
    async def get_messages(chat_id: int) -> list[ChatMessage]:
        """Get all messages for a chat."""
        ChatsManager._ensure_storage()
        chat = ChatsManager._chats.get(chat_id)
        if not chat:
            raise RuntimeError(f"Chat with ID {chat_id} not found.")
        return chat.messages

    @staticmethod
    async def create_chat(chat_data: ChatData) -> int:
        """Create a new chat and return its ID."""
        ChatsManager._ensure_storage()
        chat_id = ChatsManager._next_id
        ChatsManager._next_id += 1
        
        chat_data.id = chat_id
        chat_data.create_timestamp = datetime.now(timezone.utc)
        ChatsManager._chats[chat_id] = chat_data
        
        return chat_id

    @staticmethod
    async def archive_chat(chat_id: int) -> None:
        """Archive (delete from memory) a chat."""
        ChatsManager._ensure_storage()
        if chat_id in ChatsManager._chats:
            del ChatsManager._chats[chat_id]

    @staticmethod
    async def add_message_to_chat(chat_id: int, message: ChatMessage) -> None:
        """Add a message to an existing chat."""
        ChatsManager._ensure_storage()
        chat = ChatsManager._chats.get(chat_id)
        if not chat:
            raise RuntimeError(f"Chat with ID {chat_id} not found.")
        chat.messages.append(message)

