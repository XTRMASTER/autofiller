import logging
import os
import sys

# Ensure the app directory is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk

from app.core.theme_manager import ThemeManager
from app.core.view_manager import ViewManager
from app.ui.components.sidebar import Sidebar
from app.ui.components.titlebar import TitleBar
from app.ui.views.home_view import HomeView
from app.ui.views.settings_view import SettingsView
from app.utils.config import get_settings_path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class App(ctk.CTk):  # type: ignore
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        # Window setup
        self.title("Modern CTK App")
        self.geometry("900x600")
        self.minsize(600, 400)

        # Use custom title bar by removing standard OS decorations
        self.overrideredirect(True)

        # Core Managers
        self.theme_manager = ThemeManager(config_path=get_settings_path("ModernCTKApp"))

        # Apply initial theme
        ctk.set_appearance_mode(self.theme_manager.appearance_mode)

        # Main Layout structure

        # Custom Title Bar
        self.title_bar = TitleBar(
            master=self,
            title="Modern CTK App",
            on_minimize=self._minimize,
            on_maximize_restore=self._maximize_restore,
            on_close=self._close,
        )
        self.title_bar.pack(fill="x", side="top")

        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, side="top")

        # Sidebar
        self.sidebar = Sidebar(
            self.content_frame,
            on_nav=self._on_sidebar_nav,
            theme_manager=self.theme_manager,
        )
        self.sidebar.pack(side="left", fill="y")

        # Main View Container
        self.view_container = ctk.CTkFrame(
            self.content_frame, corner_radius=0, fg_color="transparent"
        )
        self.view_container.pack(side="left", fill="both", expand=True)
        self.view_container.grid_rowconfigure(0, weight=1)
        self.view_container.grid_columnconfigure(0, weight=1)

        # View Manager
        self.view_manager = ViewManager(self.view_container)

        # Register Views
        self.view_manager.register_view("home", HomeView)
        self.view_manager.register_view(
            "settings", SettingsView, theme_manager=self.theme_manager
        )

        # Configure Sidebar
        self.sidebar.add_button("Home", "home")
        self.sidebar.add_button("Settings", "settings")

        # Link theme manager to sidebar
        self.theme_manager.register_callback(self._on_theme_changed)
        self._on_theme_changed()  # Initial apply

        # Show initial view
        self.sidebar.set_active("home")
        self.view_manager.show_view("home")

        # Window protocols
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Alt-F4>", lambda e: self._close())

        self._is_maximized = False

    def _on_sidebar_nav(self, view_name: str) -> None:
        self.view_manager.show_view(view_name)

    def _on_theme_changed(self) -> None:
        self.sidebar.update_accent_color(self.theme_manager.accent_color)

    def _minimize(self) -> None:
        self.iconify()

    def _maximize_restore(self) -> None:
        if self._is_maximized:
            self.state("normal")
            self._is_maximized = False
        else:
            self.state("zoomed")
            self._is_maximized = True

    def _close(self) -> None:
        try:
            self.theme_manager.save_settings()
            self.destroy()
        except Exception as e:
            logger.error("Error during close: %s", e)
            sys.exit(1)


def main() -> None:
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        logger.critical("Application failed to start: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
