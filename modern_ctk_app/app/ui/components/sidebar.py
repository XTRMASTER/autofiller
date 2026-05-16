from typing import Callable, Dict, Optional

import customtkinter as ctk

from ...core.theme_manager import ThemeManager


class Sidebar(ctk.CTkFrame):  # type: ignore
    """Sidebar navigation containing view buttons."""

    def __init__(
        self,
        master: ctk.CTkFrame,
        on_nav: Callable[[str], None],
        theme_manager: ThemeManager,
        **kwargs: object,
    ) -> None:
        super().__init__(master, width=200, corner_radius=0, **kwargs)
        self.pack_propagate(False)
        self.on_nav = on_nav
        self.theme_manager = theme_manager
        self.buttons: Dict[str, ctk.CTkButton] = {}
        self.current_active: Optional[str] = None

        # Header or Logo area
        self.logo_label = ctk.CTkLabel(
            self, text="Navigation", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.logo_label.pack(pady=(20, 10), padx=20, anchor="w")

    def add_button(self, text: str, view_name: str) -> None:
        """Add a navigation button to the sidebar."""
        btn = ctk.CTkButton(
            self,
            text=text,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=lambda v=view_name: self._on_button_click(v),
        )
        btn.pack(pady=5, padx=10, fill="x")
        self.buttons[view_name] = btn

    def _on_button_click(self, view_name: str) -> None:
        self.set_active(view_name)
        self.on_nav(view_name)

    def set_active(self, view_name: str) -> None:
        """Update button styles to reflect active state."""
        if self.current_active and self.current_active in self.buttons:
            # Reset previous active button
            self.buttons[self.current_active].configure(fg_color="transparent")

        if view_name in self.buttons:
            # Apply current accent color from theme manager
            self.buttons[view_name].configure(fg_color=self.theme_manager.accent_color)
            self.current_active = view_name

    def update_accent_color(self, hex_color: str) -> None:
        """Update active button color to match theme."""
        if self.current_active and self.current_active in self.buttons:
            self.buttons[self.current_active].configure(fg_color=hex_color)
