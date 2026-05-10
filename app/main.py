import sys
import os
import customtkinter as ctk

# Add the parent directory to sys.path so 'app' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ui.main_window import MainWindow

def main():
    # Set theme and appearance
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
