"""
Weave - Main TUI Application.

An on-device coding agent with local LLM inference.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from textual.app import App
from textual.binding import Binding
from textual.reactive import Reactive, reactive

from weave.tui.chats_manager import ChatsManager
from weave.tui.models import ChatData, ChatMessage, MessageContent, WeaveModel, DEFAULT_MODEL
from weave.tui.screens.chat_screen import ChatScreen
from weave.tui.screens.help_screen import HelpScreen
from weave.tui.screens.home_screen import HomeScreen
from weave.tui.themes import BUILTIN_THEMES, Theme, load_user_themes


class Weave(App[None]):
    """Weave TUI Application."""
    
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = Path(__file__).parent / "weave.scss"
    BINDINGS = [
        Binding("q", "app.quit", "Quit", show=False),
        Binding("f1,?", "help", "Help"),
    ]

    # Use weave_theme to avoid conflict with Textual's built-in theme
    weave_theme: Reactive[str | None] = reactive(None, init=False)
    DEFAULT_SYSTEM_PROMPT = """You are an autonomous coding agent. Keep working until the user's query is completely resolved before yielding back.

Your thinking should be thorough - it's fine if it's long. Be concise but thorough. Avoid unnecessary repetition.

You MUST iterate and keep going until the problem is solved. You have everything you need to resolve problems autonomously.

Only terminate your turn when you are sure the problem is solved. Go step by step, verify your changes are correct. NEVER end your turn without truly completing the task.

Workflow:
1. Understand the problem deeply. Break it into manageable parts.
2. Investigate the codebase. Explore files, search for key functions, gather context.
3. Develop a clear, step-by-step plan with a todo list.
4. Implement incrementally. Make small, testable changes.
5. Debug as needed. Use debugging techniques to isolate issues.
6. Test frequently after each change.
7. Iterate until the root cause is fixed.
8. Reflect and validate. Think about edge cases.

When debugging:
- Determine root cause rather than addressing symptoms
- Use print statements or logs to inspect program state
- Revisit assumptions if unexpected behavior occurs

Be casual, friendly, yet professional. Communicate clearly and concisely."""

    def __init__(
        self,
        theme_name: str = "cursor",
        system_prompt: str | None = None,
    ):
        if system_prompt is None:
            system_prompt = self.DEFAULT_SYSTEM_PROMPT
        # Load themes
        available_themes: dict[str, Theme] = BUILTIN_THEMES.copy()
        try:
            available_themes |= load_user_themes()
        except Exception:
            pass  # Ignore user theme loading errors

        self.themes: dict[str, Theme] = available_themes
        self._theme_name = theme_name
        self.system_prompt = system_prompt
        self.current_model = DEFAULT_MODEL

        super().__init__()

    async def on_mount(self) -> None:
        await self.push_screen(HomeScreen())
        self.weave_theme = self._theme_name

    async def launch_chat(self, prompt: str) -> None:
        """Launch a new chat with the given prompt."""
        current_time = datetime.datetime.now(datetime.timezone.utc)
        
        system_message: MessageContent = {
            "content": self.system_prompt,
            "role": "system",
        }
        user_message: MessageContent = {
            "content": prompt,
            "role": "user",
        }
        
        chat = ChatData(
            id=None,
            title=None,
            create_timestamp=None,
            model=self.current_model,
            messages=[
                ChatMessage(
                    message=system_message,
                    timestamp=current_time,
                    model=self.current_model,
                ),
                ChatMessage(
                    message=user_message,
                    timestamp=current_time,
                    model=self.current_model,
                ),
            ],
        )
        chat.id = await ChatsManager.create_chat(chat_data=chat)
        await self.push_screen(ChatScreen(chat))

    async def action_help(self) -> None:
        if isinstance(self.screen, HelpScreen):
            self.pop_screen()
        else:
            await self.push_screen(HelpScreen())

    def get_css_variables(self) -> dict[str, str]:
        if self.weave_theme:
            theme = self.themes.get(self.weave_theme)
            if theme:
                color_system = theme.to_color_system().generate()
            else:
                color_system = {}
        else:
            color_system = {}

        return {**super().get_css_variables(), **color_system}

    def watch_weave_theme(self, theme: str | None) -> None:
        self.refresh_css(animate=False)
        self.screen._update_styles()

    @property
    def theme_object(self) -> Theme | None:
        try:
            if self.weave_theme:
                return self.themes[self.weave_theme]
        except KeyError:
            pass
        return None


def main() -> None:
    """Run the Weave TUI application."""
    app = Weave()
    app.run()


if __name__ == "__main__":
    main()
