# Changelog

## [1.0.1] - 2025-05-20
### Changed
- Robust plugin discovery: Now uses importlib and class inspection to only show plugins that define a Plugin class subclassing PluginBase.
- Plugins menu always lists all valid plugins in the plugins folder, regardless of enabled state.
- Plugin enable/disable state is persistent and checkmarks are always correct and visible.
- BooleanVars for plugin menu are now stored to prevent garbage collection and ensure checkmarks remain visible.
- Improved error handling for plugin loading.
- Plugins button moved to the Settings section in the GUI for better UX.
- Minor code cleanup and improved logging for plugin menu updates and toggling.

### Fixed
- Fixed bug where plugin checkmarks were not visible in the Plugins menu.
- Fixed plugin menu not updating checkmarks immediately after toggling.

### Security
- Improved plugin loading safety by checking for valid loader before executing modules.

---

## [1.0.0] - 2025-05-18
### Added
- GUI with `Treeview` for system/folder scans.
- Size filtering (All, 100MB+, 500MB+, 1GB+, custom).
- Real-time search bar with Clear button.
- Persistent column sorting (size, name, etc.).
- Plugin system with:
  - `python`: Pip caches, `__pycache__`, Python history.
  - `nodejs`: Npm caches, `node_modules`.
  - `python_installs`: System Python, Homebrew, pyenv installations.
- Logging to `cleanup.log` with UI error messages.
- Dark/light mode support.
- Navigation: Home, Up, Go Deep (no prompt).
- Progress bar for scan progress.
- Undo for trashed items.

### Notes
- Initial public release as a hobby project.
- Contributions welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).

### NOTICE:
macOS Cleanup Tool
Copyright (c) 2025 XClassicPeter

The concept, design, and implementation of the macOS Cleanup Tool, including its GUI, plugin system, and scanning logic, are the intellectual property of XClassicPeter. This software is licensed under the MIT License (see LICENSE), which permits use, modification, and distribution with attribution. Any derivative works must retain this notice and the original copyright.

For inquiries, contact via GitHub Issues: https://github.com/XClassicPeter/macos-cleanup-tool/issues
