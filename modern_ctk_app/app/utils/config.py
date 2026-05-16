import os
import pathlib


def get_app_data_dir(app_name: str) -> str:
    """Get the appropriate application data directory for the current OS."""
    home = pathlib.Path.home()
    if os.name == "nt":  # Windows
        app_data = os.environ.get("APPDATA")
        if app_data:
            base_dir = pathlib.Path(app_data)
        else:
            base_dir = home / "AppData" / "Roaming"
    else:  # macOS / Linux
        # Use ~/.config as standard for linux, fallback for mac
        base_dir = home / ".config"

    app_dir = base_dir / app_name
    app_dir.mkdir(parents=True, exist_ok=True)
    return str(app_dir)


def get_settings_path(app_name: str) -> str:
    """Get the path to the settings file."""
    return os.path.join(get_app_data_dir(app_name), "settings.json")
