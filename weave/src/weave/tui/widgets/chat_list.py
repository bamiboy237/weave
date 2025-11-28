"""
Chat list widget for displaying chat history.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import humanize
from rich.console import RenderResult, Console, ConsoleOptions
from rich.markup import escape
from rich.padding import Padding
from rich.text import Text
from textual import events, on
from textual.binding import Binding
from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from weave.tui.chats_manager import ChatsManager
from weave.tui.models import ChatData

if TYPE_CHECKING:
    from weave.tui.app import Weave


@dataclass
class ChatListItemRenderable:
    """Rich renderable for a chat list item."""
    chat: ChatData

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = now - self.chat.update_time
        time_ago = humanize.naturaltime(delta)
        time_ago_text = Text(time_ago, style="dim i")
        model = self.chat.model
        subtitle = f"[dim]{escape(model.display_name or model.name)}"
        if model.provider:
            subtitle += f" [i]via[/] {escape(model.provider)}"
        model_text = Text.from_markup(subtitle)
        title = self.chat.title or self.chat.short_preview.replace("\n", " ")
        yield Padding(
            Text.assemble(title, "\n", model_text, "\n", time_ago_text),
            pad=(0, 0, 0, 1),
        )


class ChatListItem(Option):
    """Option list item for a chat."""
    
    def __init__(self, chat: ChatData) -> None:
        super().__init__(ChatListItemRenderable(chat))
        self.chat = chat


class ChatList(OptionList):
    """Widget for displaying a list of chats."""
    
    BINDINGS = [
        Binding(
            "escape",
            "app.focus('home-prompt')",
            "Focus prompt",
            key_display="esc",
            tooltip="Return focus to the prompt input.",
        ),
        Binding(
            "a",
            "archive_chat",
            "Archive chat",
            key_display="a",
            tooltip="Archive the highlighted chat.",
        ),
        Binding("j,down", "cursor_down", "Down", show=False),
        Binding("k,up", "cursor_up", "Up", show=False),
        Binding("l,right,enter", "select", "Select", show=False),
        Binding("g,home", "first", "First", show=False),
        Binding("G,end", "last", "Last", show=False),
        Binding("pagedown", "page_down", "Page Down", show=False),
        Binding("pageup", "page_up", "Page Up", show=False),
    ]

    @dataclass
    class ChatOpened(Message):
        chat: ChatData

    class CursorEscapingTop(Message):
        """Cursor attempting to move out-of-bounds at top of list."""

    class CursorEscapingBottom(Message):
        """Cursor attempting to move out-of-bounds at bottom of list."""

    def __init__(
        self,
        *content: Option,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(*content, name=name, id=id, classes=classes, disabled=disabled)
        self._chat_items: list[ChatListItem] = []

    async def on_mount(self) -> None:
        await self.reload_and_refresh()

    @on(OptionList.OptionSelected)
    async def post_chat_opened(self, event: OptionList.OptionSelected) -> None:
        assert isinstance(event.option, ChatListItem)
        chat = event.option.chat
        await self.reload_and_refresh()
        self.post_message(ChatList.ChatOpened(chat=chat))

    @on(OptionList.OptionHighlighted)
    @on(events.Focus)
    def show_border_subtitle(self) -> None:
        if self.highlighted is not None:
            self.border_subtitle = self.get_border_subtitle()
        elif self.option_count > 0:
            self.highlighted = 0

    def on_blur(self) -> None:
        self.border_subtitle = None

    async def reload_and_refresh(self, new_highlighted: int = -1) -> None:
        """Reload the chats and refresh the widget."""
        self._chat_items = await self.load_chat_list_items()
        old_highlighted = self.highlighted
        self.clear_options()
        self.add_options(self._chat_items)
        self.border_title = self.get_border_title()
        if new_highlighted > -1:
            self.highlighted = new_highlighted
        else:
            self.highlighted = old_highlighted

        self.refresh()

    async def load_chat_list_items(self) -> list[ChatListItem]:
        chats = await self.load_chats()
        return [ChatListItem(chat) for chat in chats]

    async def load_chats(self) -> list[ChatData]:
        all_chats = await ChatsManager.all_chats()
        return all_chats

    async def action_archive_chat(self) -> None:
        if self.highlighted is None:
            return

        item = cast(ChatListItem, self.get_option_at_index(self.highlighted))
        self._chat_items.pop(self.highlighted)
        self.remove_option_at_index(self.highlighted)

        chat_id = item.chat.id
        if chat_id is not None:
            await ChatsManager.archive_chat(chat_id)

        self.border_title = self.get_border_title()
        self.border_subtitle = self.get_border_subtitle()
        self.app.notify(
            item.chat.title or f"Chat archived.",
            title="Chat archived",
        )
        self.refresh()

    def get_border_title(self) -> str:
        return f"History ({len(self._chat_items)})"

    def get_border_subtitle(self) -> str:
        if self.highlighted is None:
            return ""
        return f"{self.highlighted + 1} / {self.option_count}"

    def create_chat(self, chat_data: ChatData) -> None:
        new_chat_list_item = ChatListItem(chat_data)
        self._chat_items = [new_chat_list_item, *self._chat_items]
        self.clear_options()
        self.add_options(self._chat_items)
        self.highlighted = 0
        self.refresh()

    def action_cursor_up(self) -> None:
        if self.highlighted == 0:
            self.post_message(self.CursorEscapingTop())
        else:
            return super().action_cursor_up()

