from typing import Any, Callable

import customtkinter as ctk


class TitleBar(ctk.CTkFrame):  # type: ignore
    """Custom title bar with window controls and theme toggle."""

    def __init__(
        self,
        master: ctk.CTk,
        title: str,
        on_minimize: Callable[[], None],
        on_maximize_restore: Callable[[], None],
        on_close: Callable[[], None],
        **kwargs: object,
    ) -> None:
        # Minimal height, inherit colors
        super().__init__(master, height=40, corner_radius=0, **kwargs)
        self.pack_propagate(False)

        self.master_window = master

        # Left side - Title
        self.title_label = ctk.CTkLabel(
            self,
            text=f"  {title}",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
        )
        self.title_label.pack(side="left", padx=10)

        # Right side - Window controls
        # Using simple text for buttons; in a real app, use icons
        self.close_btn = ctk.CTkButton(
            self,
            text="✕",
            width=40,
            height=40,
            corner_radius=0,
            fg_color="transparent",
            hover_color="#E81123",
            text_color=("black", "white"),
            command=on_close,
        )
        self.close_btn.pack(side="right")

        self.max_btn = ctk.CTkButton(
            self,
            text="□",
            width=40,
            height=40,
            corner_radius=0,
            fg_color="transparent",
            text_color=("black", "white"),
            command=on_maximize_restore,
        )
        self.max_btn.pack(side="right")

        self.min_btn = ctk.CTkButton(
            self,
            text="—",
            width=40,
            height=40,
            corner_radius=0,
            fg_color="transparent",
            text_color=("black", "white"),
            command=on_minimize,
        )
        self.min_btn.pack(side="right")

        # Dragging support
        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Double-Button-1>", lambda e: on_maximize_restore())
        self.title_label.bind("<Button-1>", self._start_drag)
        self.title_label.bind("<B1-Motion>", self._on_drag)
        self.title_label.bind("<Double-Button-1>", lambda e: on_maximize_restore())

        self._x = 0
        self._y = 0

    def _start_drag(self, event: Any) -> None:
        self._x = event.x
        self._y = event.y

    def _on_drag(self, event: Any) -> None:
        if isinstance(self.master_window, ctk.CTk):
            x = self.master_window.winfo_x() - self._x + event.x
            y = self.master_window.winfo_y() - self._y + event.y
            self.master_window.geometry(f"+{x}+{y}")
