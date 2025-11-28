"""
Weave home screen - main entry point for the TUI.
"""

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
    BINDINGS = [Binding("escape", "app.quit", "Quit", key_display="esc")]


class HomeScreen(Screen[None]):
    CSS = """\
ChatList {
    height: 1fr;
    width: 1fr;
    background: $background 15%;
}
"""

    BINDINGS = [
        Binding(
            "ctrl+j,alt+enter",
            "send_message",
            "Send message",
            priority=True,
            key_display="^j",
            tooltip="Send a message to the local LLM.",
        ),
    ]

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.weave = cast("Weave", self.app)

    def on_mount(self) -> None:
        self.chats_manager = ChatsManager()

    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield HomePromptInput(id="home-prompt")
        yield ChatList()
        yield Welcome()
        yield Footer()

    @on(ScreenResume)
    async def reload_screen(self) -> None:
        chat_list = self.query_one(ChatList)
        await chat_list.reload_and_refresh()
        self.show_welcome_if_required()

    @on(ChatList.ChatOpened)
    async def open_chat_screen(self, event: ChatList.ChatOpened):
        chat_id = event.chat.id
        assert chat_id is not None
        chat = await self.chats_manager.get_chat(chat_id)
        await self.app.push_screen(ChatScreen(chat))

    @on(ChatList.CursorEscapingTop)
    def cursor_escaping_top(self):
        self.query_one(HomePromptInput).focus()

    @on(PromptInput.PromptSubmitted)
    async def create_new_chat(self, event: PromptInput.PromptSubmitted) -> None:
        text = event.text
        await self.weave.launch_chat(prompt=text)

    @on(PromptInput.CursorEscapingBottom)
    async def move_focus_below(self) -> None:
        self.focus_next(ChatList)

    def action_send_message(self) -> None:
        prompt_input = self.query_one(PromptInput)
        prompt_input.action_submit_prompt()

    def show_welcome_if_required(self) -> None:
        chat_list = self.query_one(ChatList)
        if chat_list.option_count == 0:
            welcome = self.query_one(Welcome)
            welcome.display = "block"
        else:
            welcome = self.query_one(Welcome)
            welcome.display = "none"

