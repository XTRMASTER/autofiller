from typing import Dict, Optional, Type
import customtkinter as ctk
import logging
from ..ui.views.base_view import BaseView

logger = logging.getLogger(__name__)


class ViewManager:
    """Manages switching between different views in the main content area."""

    def __init__(self, container: ctk.CTkFrame) -> None:
        self.container = container
        self.views: Dict[str, BaseView] = {}
        self.current_view_name: Optional[str] = None

    def register_view(
        self, name: str, view_class: Type[BaseView], **kwargs: object
    ) -> None:
        """Register a view class. It will be instantiated immediately and grid off."""
        if name in self.views:
            logger.warning("View %s is already registered.", name)
            return

        try:
            view_instance = view_class(self.container, **kwargs)
            self.views[name] = view_instance
            # Grid config to fill container
            view_instance.grid(row=0, column=0, sticky="nsew")
            view_instance.grid_remove()  # Hide initially
        except Exception as e:
            logger.error("Failed to register view %s: %s", name, e)

    def show_view(self, name: str) -> None:
        """Show the view with the given name, hiding the current one."""
        if name not in self.views:
            logger.error("Cannot show view %s: Not registered.", name)
            return

        if self.current_view_name == name:
            return  # Already showing

        # Hide current
        if self.current_view_name and self.current_view_name in self.views:
            self.views[self.current_view_name].grid_remove()
            self.views[self.current_view_name].on_hide()

        # Show new
        self.views[name].grid()
        self.views[name].on_show()
        self.current_view_name = name
        logger.info("Switched to view: %s", name)
