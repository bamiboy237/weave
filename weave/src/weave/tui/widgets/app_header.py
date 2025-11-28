"""
Application header widget.
"""

from typing import TYPE_CHECKING, cast

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Label

if TYPE_CHECKING:
    from weave.tui.app import Weave


class AppHeader(Widget):
    """Header widget for the home screen."""
    
    COMPONENT_CLASSES = {"app-title", "app-subtitle"}

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.weave: "Weave" = cast("Weave", self.app)

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="cl-header-container"):
                yield Label(
                    Text("Weave") + Text(" v0.1.0", style="dim"),
                    id="weave-title",
                )
            model = self.weave.current_model
            yield Label(self._get_model_text(model.display_name or model.name), id="model-label")

    def _get_model_text(self, model_name: str) -> str:
        return f"[dim]{model_name}[/]"

    def update_model_label(self, model_name: str) -> None:
        model_label = self.query_one("#model-label", Label)
        model_label.update(self._get_model_text(model_name))

