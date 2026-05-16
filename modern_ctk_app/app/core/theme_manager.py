import json
import logging
import os
from typing import Callable, Literal

import customtkinter as ctk

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages application theme state and persistence."""

    def __init__(self, config_path: str, default_accent: str = "#3B82F6") -> None:
        self.config_path: str = config_path
        self.accent_color: str = default_accent
        self.appearance_mode: Literal["light", "dark"] = "light"
        self._callbacks: list[Callable[[], None]] = []
        self.load_settings()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register a function to be called when theme changes."""
        self._callbacks.append(callback)

    def _notify_callbacks(self) -> None:
        """Call all registered callbacks."""
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                logger.error("Error in theme callback: %s", e)

    def load_settings(self) -> None:
        """Load settings from JSON config file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.accent_color = data.get("accent_color", self.accent_color)
                mode = data.get("appearance_mode", "light")
                if mode in ["light", "dark"]:
                    self.appearance_mode = mode
        except FileNotFoundError:
            logger.info("Config not found, using defaults.")
        except json.JSONDecodeError as exc:
            logger.error("Corrupted config file: %s", exc)

        self.apply_theme()

    def save_settings(self) -> None:
        """Save settings to JSON config file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "accent_color": self.accent_color,
                        "appearance_mode": self.appearance_mode,
                    },
                    f,
                    indent=4,
                )
        except Exception as e:
            logger.error("Failed to save settings: %s", e)

    def apply_theme(self) -> None:
        """Apply current theme settings to customtkinter."""
        ctk.set_appearance_mode(self.appearance_mode)
        # CustomTkinter only has limited built-in themes.
        # We rely on callbacks to update widgets with our accent color.
        self._notify_callbacks()

    def set_appearance_mode(self, mode: Literal["light", "dark"]) -> None:
        """Set the appearance mode (light or dark)."""
        self.appearance_mode = mode
        self.apply_theme()
        self.save_settings()

    def set_accent_color(self, color: str) -> None:
        """Set the accent color."""
        # Simple regex check could be added here
        self.accent_color = color
        self._notify_callbacks()
        self.save_settings()

    def get_bg_color(self) -> str:
        return "#FFFFFF" if self.appearance_mode == "light" else "#121212"

    def get_fg_color(self) -> str:
        return "#F0F0F0" if self.appearance_mode == "light" else "#1E1E1E"

    def get_text_color(self) -> str:
        return "#000000" if self.appearance_mode == "light" else "#FFFFFF"
