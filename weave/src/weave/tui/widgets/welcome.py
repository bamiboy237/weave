"""
Welcome widget shown on the home screen when no chat history exists.
"""

from rich.console import RenderableType
from textual.widgets import Static


class Welcome(Static):
    MESSAGE = """
To get started, type a message in the box at the top of the
screen and press [b u]ctrl+j[/] or [b u]alt+enter[/] to send it.

Weave runs entirely on your local machine using llama.cpp.
No API keys required, no data leaves your computer.

For help and keyboard shortcuts, press [b u]F1[/] or [b u]?[/].

[@click='open_repo'][b]https://github.com/your-username/weave[/][/]
"""

    BORDER_TITLE = "Welcome to Weave!"

    def render(self) -> RenderableType:
        return self.MESSAGE

    def _action_open_repo(self) -> None:
        import webbrowser
        webbrowser.open("https://github.com/your-username/weave")

