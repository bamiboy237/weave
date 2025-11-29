"""A stopwatch application built with Textual."""
from time import monotonic

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header

class TimeDisplay(Digits):
    """A widget to display elapsed time."""
    start_time = reactive(monotonic)
    elapsed_time = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when the widget is mounted."""
        self.set_interval(1 / 60, self.update_time)

    def update_time(self) -> None:
        """Method to update the time to the current time."""
        self.time = monotonic() - self.start_time

    def watch_time(self, time: float) -> None:
        """Method to watch the time and update the time display."""


class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00")

def on_button_pressed(self, event: Button.Pressed) -> None:
    """Event handler called when a button is pressed."""
    if event.button.id == "start":
        self.add_class("running")
    elif event.button.id == "stop":
        self.remove_class("started")

class StopwatchApp(App):
    """A textual app to manage stopwatches."""

    CSS_PATH = "stopwatch.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode")
    ]
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch())

    def action_toggle_dark(self) -> None:
        """An action to toggle the dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()