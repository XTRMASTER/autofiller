## 2024-05-16 - Prevent Runtime Crashes from Missing Imports & Silenced Errors
**Bug/Pattern:** `os` was used in `app/ui/main_window.py` without being imported, which leads to `NameError` at runtime when loading documents for a new shipment. Furthermore, there were multiple `except: pass` blocks which masked underlying errors, making debugging harder and silently failing operations.
**Root Cause:** Lack of static analysis (linting) integration in development workflow, allowing undefined variables to slip into code and relying on bare `except` blocks for quick and dirty error handling.
**Fix Applied:** Added `import os` to `app/ui/main_window.py`. Replaced `except: pass` with `except Exception as e: print(f"...")` in `main_window.py` and `presets_panel.py`.
**Prevention:** Always run linters (like `flake8`) to catch undefined names before committing. Avoid `except: pass` completely; always catch specific exceptions or, at a minimum, log the generic exception to the console to surface failures.

## 2024-05-16 - Prevent UI Freezes During Document Generation
**Bug/Pattern:** In desktop applications (like those built with Tkinter/CustomTkinter), long-running tasks such as generating or batch-processing Word and Excel documents are executed on the main UI thread. This causes the application interface to become entirely unresponsive (freezing) until the operation completes, leading to poor user experience or the OS prompting to kill the app.
**Root Cause:** Synchronous file operations block the Tkinter `mainloop`, preventing it from handling UI events (like clicks, dragging, or repainting).
**Fix Applied:** Documented as a future preventive improvement. (No code changed yet as per Caretaker philosophy for today's focused task).
**Prevention:** Future implementations of the batch document processor or large template loaders should utilize Python's `threading` module (or `concurrent.futures.ThreadPoolExecutor`) to offload I/O-bound document modifications from the main thread. A queue or `after()` callback mechanism should be used to safely update the GUI with progress or completion status once the background thread finishes.
