"""Weave home screen - main entry point for the TUI."""

from typing import TYPE_CHECKING, cast

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.events import ScreenResume
from textual.screen import Screen
from textual.widgets import Footer

from weave.tui.chats_manager import ChatsManager
from weave.tui.widgets.chat_list import ChatList
from weave.tui.widgets.prompt_input import PromptInput
from weave.tui.widgets.app_header import AppHeader
from weave.tui.screens.chat_screen import ChatScreen
from weave.tui.widgets.welcome import Welcome

if TYPE_CHECKING:
    from weave.tui.app import Weave


class HomePromptInput(PromptInput):
    """Prompt input variant for the home screen with quit binding."""

    BINDINGS = [Binding("escape", "app.quit", "Quit", key_display="esc")]


class HomeScreen(Screen[None]):
    """Main home screen showing chat list and prompt input."""

    CSS = """\
ChatList {
    height: 1fr;
    width: 1fr;
    background: $background 15%;
}
"""

    BINDINGS = [
        Binding(
            "ctrl+e,alt+enter",
            "send_message",
            "Send message",
            priority=True,
            key_display="^e",
            tooltip="Send a message to the local LLM.",
        ),
    ]

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,  # noqa: A002  # pylint: disable=redefined-builtin
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.weave = cast("Weave", self.app)
        self.chats_manager = ChatsManager()

    def on_mount(self) -> None:
        """Handle screen mount event."""

    def compose(self) -> ComposeResult:
        """Compose the home screen layout."""
        yield AppHeader()
        yield HomePromptInput(id="home-prompt")
        yield ChatList()
        yield Welcome()
        yield Footer()

    @on(ScreenResume)
    async def reload_screen(self) -> None:
        """Reload chat list when screen resumes."""
        chat_list = self.query_one(ChatList)
        await chat_list.reload_and_refresh()
        self.show_welcome_if_required()

    @on(ChatList.ChatOpened)
    async def open_chat_screen(self, event: ChatList.ChatOpened) -> None:
        """Open the selected chat in a new screen."""
        chat_id = event.chat.id
        assert chat_id is not None
        chat = await self.chats_manager.get_chat(chat_id)
        await self.app.push_screen(ChatScreen(chat))

    @on(ChatList.CursorEscapingTop)
    def cursor_escaping_top(self) -> None:
        """Move focus to prompt when cursor escapes chat list."""
        self.query_one(HomePromptInput).focus()

    @on(PromptInput.PromptSubmitted)
    async def create_new_chat(self, event: PromptInput.PromptSubmitted) -> None:
        """Create a new chat from the submitted prompt."""
        text = event.text
        await self.weave.launch_chat(prompt=text)

    @on(PromptInput.CursorEscapingBottom)
    async def move_focus_below(self) -> None:
        """Move focus to chat list when cursor escapes prompt."""
        self.focus_next(ChatList)

    def action_send_message(self) -> None:
        """Trigger prompt submission."""
        prompt_input = self.query_one(PromptInput)
        prompt_input.action_submit_prompt()

    def show_welcome_if_required(self) -> None:
        """Show or hide welcome message based on chat list state."""
        chat_list = self.query_one(ChatList)
        if chat_list.option_count == 0:
            welcome = self.query_one(Welcome)
            welcome.display = "block"
        else:
            welcome = self.query_one(Welcome)
            welcome.display = "none"