import customtkinter as ctk


class BaseView(ctk.CTkFrame):  # type: ignore
    """Base class for all views in the application."""

    def __init__(self, master: ctk.CTkFrame, **kwargs: object) -> None:
        super().__init__(master, **kwargs)

    def on_show(self) -> None:
        """Called when the view is displayed."""
        pass

    def on_hide(self) -> None:
        """Called when the view is hidden."""
        pass
