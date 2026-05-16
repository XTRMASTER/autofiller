import customtkinter as ctk
from .base_view import BaseView
from ...core.theme_manager import ThemeManager


class SettingsView(BaseView):
    """View for configuring application settings."""

    def __init__(
        self, master: ctk.CTkFrame, theme_manager: ThemeManager, **kwargs: object
    ) -> None:
        super().__init__(master, **kwargs)
        self.theme_manager = theme_manager

        # Header
        self.label = ctk.CTkLabel(
            self, text="Settings", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label.pack(pady=(20, 10), padx=20, anchor="w")

        # Theme Settings Card
        self.theme_card = ctk.CTkFrame(self, corner_radius=12)
        self.theme_card.pack(pady=10, padx=20, fill="x")

        self.theme_title = ctk.CTkLabel(
            self.theme_card, text="Appearance", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.theme_title.pack(pady=(15, 10), padx=15, anchor="w")

        # Appearance Mode
        self.mode_frame = ctk.CTkFrame(self.theme_card, fg_color="transparent")
        self.mode_frame.pack(fill="x", padx=15, pady=5)

        self.mode_label = ctk.CTkLabel(self.mode_frame, text="Mode:")
        self.mode_label.pack(side="left", padx=(0, 10))

        self.mode_switch = ctk.CTkSwitch(
            self.mode_frame, text="Dark Mode", command=self._on_mode_change
        )
        self.mode_switch.pack(side="left")

        # Set initial state
        if self.theme_manager.appearance_mode == "dark":
            self.mode_switch.select()

        # Accent Color
        self.accent_frame = ctk.CTkFrame(self.theme_card, fg_color="transparent")
        self.accent_frame.pack(fill="x", padx=15, pady=15)

        self.accent_label = ctk.CTkLabel(self.accent_frame, text="Accent Color:")
        self.accent_label.pack(side="left", padx=(0, 10))

        colors = [
            ("Blue", "#3B82F6"),
            ("Emerald", "#10B981"),
            ("Violet", "#8B5CF6"),
            ("Rose", "#F43F5E"),
            ("Amber", "#F59E0B"),
            ("Teal", "#14B8A6"),
        ]

        self.color_buttons: list[ctk.CTkButton] = []
        for _name, hex_val in colors:
            btn = ctk.CTkButton(
                self.accent_frame,
                text="",
                width=30,
                height=30,
                corner_radius=15,
                fg_color=hex_val,
                hover_color=hex_val,
                command=lambda h=hex_val: self._on_color_change(h),
            )
            btn.pack(side="left", padx=5)
            self.color_buttons.append(btn)

        # Custom hex input
        self.hex_entry = ctk.CTkEntry(
            self.accent_frame, placeholder_text="Hex (e.g. #FF0000)", width=120
        )
        self.hex_entry.pack(side="left", padx=(15, 5))

        self.hex_btn = ctk.CTkButton(
            self.accent_frame, text="Apply", width=60, command=self._apply_custom_hex
        )
        self.hex_btn.pack(side="left")

        # Register for theme updates
        self.theme_manager.register_callback(self._update_colors)
        self._update_colors()

    def _on_mode_change(self) -> None:
        if self.mode_switch.get() == 1:
            self.theme_manager.set_appearance_mode("dark")
        else:
            self.theme_manager.set_appearance_mode("light")

    def _on_color_change(self, hex_val: str) -> None:
        self.theme_manager.set_accent_color(hex_val)

    def _apply_custom_hex(self) -> None:
        val = self.hex_entry.get()
        import re

        if re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", val):
            self.theme_manager.set_accent_color(val)

    def _update_colors(self) -> None:
        accent = self.theme_manager.accent_color
        self.mode_switch.configure(progress_color=accent)
        self.hex_btn.configure(fg_color=accent)
