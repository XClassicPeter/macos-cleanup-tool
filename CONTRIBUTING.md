# Contributing to macOS Cleanup Tool

Thank you for your interest! This is a hobby project with limited time for maintenance, so contributions are welcome but should be simple and focused.

---

## Reporting Issues
- Use [GitHub Issues](https://github.com/XClassicPeter/macos-cleanup-tool/issues).
- Please provide:
  - Bug description
  - Steps to reproduce
  - Relevant `cleanup.log` output
  - Environment details: Python version (`python --version`), Tk version (`python -c 'import tkinter; print(tkinter.Tk().tk.call("info", "patchlevel"))'`), macOS version (`sw_vers`)

---

## Suggesting Features
- Open an issue with a clear description.
- Note: Only high-impact or widely useful features will be considered due to limited time.

---

## Submitting Pull Requests
- PRs are welcome but may take time to review.
- Steps:
  1. Fork the repo and create a branch (`git checkout -b my-feature`)
  2. Follow PEP 8, use docstrings, and log events/errors
  3. Test with `python cleanup.py` (verify UI, logs, and plugin behavior)
  4. Open a PR referencing the related issue
- Focus on small, focused changes (bug fixes, new plugins, or documentation improvements)

---

## Adding Plugins

- Create a new file in `plugins/` (e.g., `my_plugin.py`).
- Inherit from `PluginBase` and implement the `scan()` method.

**Example:**
```python
from plugins.plugin_base import PluginBase
from scanner import get_size
import os

class Plugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.logger.info("MyPlugin initialized")

    def scan(self):
        items = []
        # Example: Find all .log files in ~/Desktop
        desktop = os.path.expanduser("~/Desktop")
        for fname in os.listdir(desktop):
            if fname.endswith(".log"):
                path = os.path.join(desktop, fname)
                items.append({
                    "category": "Custom Logs",
                    "name": fname,
                    "short_name": fname,
                    "path": path,
                    "size": get_size(path),
                })
        return items
```
- Test your plugin by launching the app and enabling it from the Plugins menu.
- Check `cleanup.log` for output and errors.
- If you want your plugin enabled by default, add it to `settings.py` DEFAULTS.
- Submit your plugin as a PR.

---

## Code Style
- Follow PEP 8 for all code.
- Use docstrings for public methods.
- Use `logging.getLogger(__name__)` for logging events and errors.

---

## Testing
- Run `python cleanup.py`.
- Verify UI, logs, and all main features (scan, search, delete, plugins).
