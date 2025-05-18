
# Contributing to macOS Cleanup Tool

Thank you for your interest! This is a hobby project with limited time for maintenance, so contributions are welcome but should be simple and focused.

## Reporting Issues
- Use [GitHub Issues](https://github.com/XClassicPeter/macos-cleanup-tool/issues).
- Provide:
  - Bug description.
  - Steps to reproduce.
  - `cleanup.log` contents.
  - Environment: Python (`python --version`), Tk (`tkinter.Tk().tk.call('info', 'patchlevel')`), macOS (`sw_vers`).

## Suggesting Features
- Open an issue with a clear description.
- Note: Due to time constraints, only high-impact features will be considered.

## Submitting Pull Requests
- PRs are welcome but may take time to review.
- Steps:
  1. Fork and branch (`git checkout -b fix-bug`).
  2. Follow PEP 8, use docstrings, log events/errors.
  3. Test with `python cleanup.py`.
  4. Open PR with issue reference.
- Focus on small changes (e.g., bug fixes, new plugins).

## Adding Plugins
- Create `plugins/<name>.py`:
  ```python
  from plugins.plugin_base import PluginBase
  from scanner import get_size

  class Plugin(PluginBase):
      def scan(self):
          return [{"category": "My Plugin", "name": "test", "short_name": "test", "path": "/path", "size": get_size("/path")}]```
    
- Add to settings.py DEFAULTS if default-enabled.
- Test and submit as a PR.

## Code Style
- PEP 8.

## Docstrings for public methods.
- Use logging.getLogger(__name__) for events/errors.

## Testing
- Run python cleanup.py.
- Verify UI, logs, and functionality (scan, search, delete, plugins).
