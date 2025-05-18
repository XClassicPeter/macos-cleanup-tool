# macOS Cleanup Tool

A lightweight Python GUI tool to clean up temporary files and caches on macOS. This is a hobby project to help users free up disk space, with plugins for Python, Node.js, and Python installations.

## Features
- Scan system temps or folders with size filtering (100MB+, 500MB+, 1GB+).
- Real-time search by category, name, or path.
- Persistent column sorting (size, name, etc.).
- Plugins for Python caches, Node.js caches, and Python installations.
- Move items to Trash with undo support.
- Dark/light mode support.
- Logs to `cleanup.log` for debugging.

## Installation
Requires Python 3.13 and Tk 8.6 (included with macOS Python).

```bash
pip install send2trash
git clone https://github.com/XClassicPeter/macos-cleanup-tool.git
cd macos-cleanup-tool
python cleanup.py
```

## Usage
Launch: python cleanup.py

Click "Scan System" or "Home" to scan.

Filter by size (dropdown or custom MB) or search (e.g., "pip").

Right-click items to Open in Finder (Cmd+F), Move to Trash (Cmd+T), or Clean Folder (Cmd+E).

Toggle plugins (Python, Nodejs, Python Installs) in the Plugins menu.

Check cleanup.log for errors.

## Plugins
Python: Pip caches, __pycache__, Python history.

Nodejs: Npm caches, node_modules.

Python Installs: System Python, Homebrew, pyenv installations.

## Contributing
This is a hobby project with limited maintenance time. Please:
Report bugs via GitHub Issues.

Suggest features, but note limited capacity for review.

See CONTRIBUTING.md for details.

## License
MIT License. See LICENSE.

## Notice
The concept and implementation of macOS Cleanup Tool are owned by Peter. See NOTICE for details.

## Contact
File issues at GitHub Issues.
