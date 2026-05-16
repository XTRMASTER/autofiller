import customtkinter as ctk
from .base_view import BaseView


class HomeView(BaseView):
    """The main landing view of the application."""

    def __init__(self, master: ctk.CTkFrame, **kwargs: object) -> None:
        super().__init__(master, **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text="Welcome to the Application",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.label.pack(pady=40, padx=20)

        self.card = ctk.CTkFrame(self, corner_radius=12)
        self.card.pack(pady=20, padx=20, fill="x")

        self.card_label = ctk.CTkLabel(
            self.card,
            text="This is a clean, modern, single-window application.\n\n"
            "Select other views from the sidebar.",
            font=ctk.CTkFont(size=14),
        )
        self.card_label.pack(pady=20, padx=20)
