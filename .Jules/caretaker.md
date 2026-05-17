## 2026-05-16 - CustomTkinter UI Components Fix

**Bug/Pattern:**
The custom title bar wasn't showing in the UI, and the sidebar accent color was reverting to default when changing tabs, breaking the requested custom appearance.

**Root Cause:**
1. The custom `TitleBar` was not being imported and instantiated inside `main.py`, rendering it as dead code.
2. In `sidebar.py`, the `set_active` method hardcoded the default color to `["#3B82F6", "#3B82F6"]` when switching tabs, instead of using the custom accent color configured in `ThemeManager`.

**Fix Applied:**
1. Modified `main.py` to instantiate `TitleBar` with required arguments and packed it into the window layout.
2. Modified `Sidebar` to accept the `ThemeManager` during instantiation.
3. Updated the `set_active` method in `Sidebar` to apply the current accent color retrieved from `theme_manager.accent_color`.

**Prevention:**
Thoroughly test new components to ensure they appear as expected on-screen instead of just validating the logic via tests or code analyzers. Always link the UI elements back to the single source of truth for theming to avoid hardcoded defaults taking precedence over user settings.

## 2026-05-17 - Unblocking UI Threads & Preserving Document Formatting

**Bug/Pattern:**
1. The Tkinter GUI would completely freeze during batch processing or when applying variables to multiple documents because the file operations were blocking the main event loop.
2. Replacing text variables in `.docx` templates was destroying original font styling (colors, boldness, etc.) because it reconstructed paragraphs entirely from scratch.

**Root Cause:**
1. Running CPU-bound and I/O-bound synchronous iteration over templates inside Tkinter callbacks instead of background threads.
2. The `_replace_in_paragraph` logic inside `app/core/word_handler.py` was clearing all native `Run` objects and converting the updated text into a single raw unstyled string run.

**Fix Applied:**
1. Offloaded loops calling `apply_variables_to_template` into `threading.Thread(daemon=True)` worker threads. Progress and UI feedback are now passed back safely via `self.after(0, ...)`.
2. Modified the text replacement algorithm to iterate and apply replacements at the individual `run.text` level, preserving all existing text styles within the document.

**Prevention:**
1. Any iterative loop performing file parsing or writing inside a UI framework must run in an asynchronous or threaded context to ensure the application remains responsive.
2. When parsing and modifying structured document formats like Word/Excel, favor incremental mutations on existing node elements over destructive rebuilding to retain original layout properties.
