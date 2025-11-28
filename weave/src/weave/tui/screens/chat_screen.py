"""
Weave chat screen - active conversation view.
"""

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer

from weave.tui.chats_manager import ChatsManager
from weave.tui.widgets.response_status import ResponseStatus
from weave.tui.widgets.chat import Chat
from weave.tui.models import ChatData


class ChatScreen(Screen[None]):
    AUTO_FOCUS = "ChatPromptInput"
    BINDINGS = [
        Binding(
            key="escape",
            action="app.focus('prompt')",
            description="Focus prompt",
            key_display="esc",
            tooltip="Return focus to the prompt input.",
        ),
    ]

    def __init__(self, chat_data: ChatData):
        super().__init__()
        self.chat_data = chat_data
        self.chats_manager = ChatsManager()

    def compose(self) -> ComposeResult:
        yield Chat(self.chat_data)
        yield Footer()

    @on(Chat.NewUserMessage)
    def new_user_message(self, event: Chat.NewUserMessage) -> None:
        """Handle a new user message."""
        self.query_one(Chat).allow_input_submit = False
        response_status = self.query_one(ResponseStatus)
        response_status.set_awaiting_response()
        response_status.display = True

    @on(Chat.AgentResponseStarted)
    def start_awaiting_response(self) -> None:
        """Prevent sending messages because the agent is typing."""
        response_status = self.query_one(ResponseStatus)
        response_status.set_agent_responding()
        response_status.display = True

    @on(Chat.AgentResponseComplete)
    async def agent_response_complete(self, event: Chat.AgentResponseComplete) -> None:
        """Allow the user to send messages again."""
        self.query_one(ResponseStatus).display = False
        self.query_one(Chat).allow_input_submit = True
        
        if self.chat_data.id is None:
            raise RuntimeError("Chat has no ID. This is likely a bug in Weave.")

        await self.chats_manager.add_message_to_chat(
            chat_id=self.chat_data.id, message=event.message
        )

