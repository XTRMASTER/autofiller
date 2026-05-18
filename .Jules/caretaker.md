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

## 2026-05-18 - Word Template Formatting Preservation & Recursion Safety

**Bug/Pattern:**
Variables replaced in Word templates were causing the entire paragraph to lose its inline formatting (bold, italic, etc.). A subsequent attempt to fix it introduced a regression where multiple replacements or replacing text with a subset of itself caused an infinite recursion/loop.
**Root Cause:**
The original implementation flattened all paragraph "runs" into a single run to simplify text replacement, destroying the underlying XML structure of styles. The naive fix used recursive or first-match replacement which got stuck on self-referential replacements (e.g. replacing 'cat' with 'catty' in a loop).
**Fix Applied:**
Implemented a precise algorithm in `WordHandler._replace_text_in_paragraph` that identifies exactly which run(s) a variable spans across. It accurately cuts and splices text while retaining run objects and uses an offset tracker (`start_search`) to continue replacements without re-evaluating newly inserted text.
**Prevention:**
Always test string replacement functions against multiple occurrences in a single string, and test edge cases where the replacement text contains the original search text.
