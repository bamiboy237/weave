"""
Main chat widget for conversation display and interaction.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from textual.widgets import Label
from textual import on, work, events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget

from weave.tui.chats_manager import ChatsManager
from weave.tui.models import ChatData, ChatMessage, MessageContent
from weave.tui.widgets.response_status import ResponseStatus
from weave.tui.widgets.chat_header import ChatHeader, TitleStatic
from weave.tui.widgets.prompt_input import PromptInput
from weave.tui.widgets.chatbox import Chatbox


if TYPE_CHECKING:
    from weave.tui.app import Weave


class ChatPromptInput(PromptInput):
    BINDINGS = [Binding("escape", "app.pop_screen", "Close chat", key_display="esc")]


class Chat(Widget):
    """Main chat widget that manages the conversation."""
    
    BINDINGS = [
        Binding("ctrl+r", "rename", "Rename", key_display="^r"),
        Binding("shift+down", "scroll_container_down", show=False),
        Binding("shift+up", "scroll_container_up", show=False),
        Binding(
            key="g",
            action="focus_first_message",
            description="First message",
            key_display="g",
            show=False,
        ),
        Binding(
            key="G",
            action="focus_latest_message",
            description="Latest message",
            show=False,
        ),
    ]

    allow_input_submit = reactive(True)
    """Used to lock the chat input while the agent is responding."""

    def __init__(self, chat_data: ChatData) -> None:
        super().__init__()
        self.chat_data = chat_data
        self.weave: "Weave" = cast("Weave", self.app)
        self.model = chat_data.model

    @dataclass
    class AgentResponseStarted(Message):
        pass

    @dataclass
    class AgentResponseComplete(Message):
        chat_id: int | None
        message: ChatMessage
        chatbox: Chatbox

    @dataclass
    class AgentResponseFailed(Message):
        """Sent when the agent fails to respond."""
        last_message: ChatMessage

    @dataclass
    class NewUserMessage(Message):
        content: str

    def compose(self) -> ComposeResult:
        yield ResponseStatus()
        yield ChatHeader(chat=self.chat_data, model=self.model)

        with VerticalScroll(id="chat-container") as vertical_scroll:
            vertical_scroll.can_focus = False

        yield ChatPromptInput(id="prompt")

    async def on_mount(self, _: events.Mount) -> None:
        """When the component is mounted, load the chat."""
        await self.load_chat(self.chat_data)

    @property
    def chat_container(self) -> VerticalScroll:
        return self.query_one("#chat-container", VerticalScroll)

    @property
    def is_empty(self) -> bool:
        """True if the conversation is empty."""
        return len(self.chat_data.messages) == 1  # Contains system message at first.

    def scroll_to_latest_message(self):
        container = self.chat_container
        container.refresh()
        container.scroll_end(animate=False, force=True)

    @on(AgentResponseFailed)
    def restore_state_on_agent_failure(self, event: Chat.AgentResponseFailed) -> None:
        original_prompt = event.last_message.message.get("content", "")
        if isinstance(original_prompt, str):
            self.query_one(ChatPromptInput).text = original_prompt

    async def new_user_message(self, content: str) -> None:
        """Handle a new user message."""
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        user_message: MessageContent = {
            "content": content,
            "role": "user",
        }

        user_chat_message = ChatMessage(user_message, now_utc, self.chat_data.model)
        self.chat_data.messages.append(user_chat_message)
        user_message_chatbox = Chatbox(user_chat_message, self.chat_data.model)

        await self.chat_container.mount(user_message_chatbox)

        self.scroll_to_latest_message()
        self.post_message(self.NewUserMessage(content))

        if self.chat_data.id is not None:
            await ChatsManager.add_message_to_chat(
                chat_id=self.chat_data.id, message=user_chat_message
            )

        prompt = self.query_one(ChatPromptInput)
        prompt.submit_ready = False
        self.stream_agent_response()

    @work(thread=True, group="agent_response")
    async def stream_agent_response(self) -> None:
        """Stream response from the local LLM.
        
        TODO: Integrate with llama.cpp inference in Phase 1.
        Currently returns a placeholder response.
        """
        model = self.chat_data.model

        ai_message: MessageContent = {
            "content": "",
            "role": "assistant",
        }
        now = datetime.datetime.now(datetime.timezone.utc)

        message = ChatMessage(message=ai_message, model=model, timestamp=now)
        response_chatbox = Chatbox(
            message=message,
            model=self.chat_data.model,
            classes="response-in-progress",
        )
        self.post_message(self.AgentResponseStarted())
        self.app.call_from_thread(self.chat_container.mount, response_chatbox)

        import asyncio
        from weave.llm.chat import format_messages_for_llm
        from weave.llm.client import stream_chat_completion
        
        formatted_messages = format_messages_for_llm(self.chat_data.messages)
        llm_response = stream_chat_completion(formatted_messages)
        
        try:
            for chunk in llm_response:
                response_chatbox.border_title = "Agent is responding..."
                self.app.call_from_thread(
                    response_chatbox.append_chunk, chunk + " "
                )
                
                scroll_y = self.chat_container.scroll_y
                max_scroll_y = self.chat_container.max_scroll_y
                if scroll_y in range(max_scroll_y - 3, max_scroll_y + 1):
                    self.app.call_from_thread(
                        self.chat_container.scroll_end, animate=False
                    )
                
                await asyncio.sleep(0.05)  # Simulate streaming delay
                
        except Exception as e:
            self.notify(
                f"Error: {e}",
                title="Error",
                severity="error",
                timeout=10,
            )
            self.post_message(self.AgentResponseFailed(self.chat_data.messages[-1]))
        else:
            self.post_message(
                self.AgentResponseComplete(
                    chat_id=self.chat_data.id,
                    message=response_chatbox.message,
                    chatbox=response_chatbox,
                )
            )

    @on(AgentResponseFailed)
    @on(AgentResponseStarted)
    async def agent_started_responding(
        self, event: AgentResponseFailed | AgentResponseStarted
    ) -> None:
        try:
            awaiting_reply = self.chat_container.query_one("#awaiting-reply", Label)
        except NoMatches:
            pass
        else:
            if awaiting_reply:
                await awaiting_reply.remove()

    @on(AgentResponseComplete)
    def agent_finished_responding(self, event: AgentResponseComplete) -> None:
        # Ensure the thread is updated with the message from the agent
        self.chat_data.messages.append(event.message)
        event.chatbox.border_title = "Agent"
        event.chatbox.remove_class("response-in-progress")
        prompt = self.query_one(ChatPromptInput)
        prompt.submit_ready = True

    @on(PromptInput.PromptSubmitted)
    async def user_chat_message_submitted(
        self, event: PromptInput.PromptSubmitted
    ) -> None:
        if self.allow_input_submit is True:
            user_message = event.text
            await self.new_user_message(user_message)

    @on(PromptInput.CursorEscapingTop)
    async def on_cursor_up_from_prompt(
        self, event: PromptInput.CursorEscapingTop
    ) -> None:
        self.focus_latest_message()

    @on(Chatbox.CursorEscapingBottom)
    def move_focus_to_prompt(self) -> None:
        self.query_one(ChatPromptInput).focus()

    @on(TitleStatic.ChatRenamed)
    async def handle_chat_rename(self, event: TitleStatic.ChatRenamed) -> None:
        if event.chat_id == self.chat_data.id and event.new_title:
            self.chat_data.title = event.new_title
            header = self.query_one(ChatHeader)
            header.update_header(self.chat_data, self.model)
            await ChatsManager.rename_chat(event.chat_id, event.new_title)

    def get_latest_chatbox(self) -> Chatbox:
        return self.query(Chatbox).last()

    def focus_latest_message(self) -> None:
        try:
            self.get_latest_chatbox().focus()
        except NoMatches:
            pass

    def action_rename(self) -> None:
        title_static = self.query_one(TitleStatic)
        title_static.begin_rename()

    def action_focus_latest_message(self) -> None:
        self.focus_latest_message()

    def action_focus_first_message(self) -> None:
        try:
            self.query(Chatbox).first().focus()
        except NoMatches:
            pass

    def action_scroll_container_up(self) -> None:
        if self.chat_container:
            self.chat_container.scroll_up()

    def action_scroll_container_down(self) -> None:
        if self.chat_container:
            self.chat_container.scroll_down()

    async def load_chat(self, chat_data: ChatData) -> None:
        chatboxes = [
            Chatbox(chat_message, chat_data.model)
            for chat_message in chat_data.non_system_messages
        ]
        await self.chat_container.mount_all(chatboxes)
        self.chat_container.scroll_end(animate=False, force=True)
        chat_header = self.query_one(ChatHeader)
        chat_header.update_header(
            chat=chat_data,
            model=chat_data.model,
        )

        # If the last message didn't receive a response, try again.
        messages = chat_data.messages
        if messages and messages[-1].message.get("role") == "user":
            prompt = self.query_one(ChatPromptInput)
            prompt.submit_ready = False
            self.stream_agent_response()

    def action_close(self) -> None:
        self.app.clear_notifications()
        self.app.pop_screen()

