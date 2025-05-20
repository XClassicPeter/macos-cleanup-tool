# macOS Cleanup Tool

A lightweight, extensible Python GUI for cleaning up temporary files and caches on macOS. Designed to help users reclaim disk space, it features a plugin system for targeting Python, Node.js, system, and other cache types.

---

## Features

- Scan system and user temp folders with size filtering (100MB+, 500MB+, 1GB+)
- Real-time search by category, name, or path
- Persistent column sorting (size, name, etc.)
- Move items to Trash with undo support
- Dark/light mode support
- Logging to `cleanup.log` for debugging
- Extensible plugin system (see below)

---

## Installation

**Requirements:**
- Python 3.13 or newer
- Tk 8.6 (included with macOS Python)

**Setup:**
```bash
pip install send2trash
# Clone the repository
git clone https://github.com/XClassicPeter/macos-cleanup-tool.git
cd macos-cleanup-tool
python cleanup.py
```

---

## Usage

- **Launch:**
  ```bash
  python cleanup.py
  ```
- **Scan:**
  Click "Scan System" or "Home" to scan for files.
- **Filter:**
  Use the size dropdown or enter a custom MB value. Search by keyword (e.g., "pip").
- **Actions:**
  - Right-click items for:
    - Open in Finder (`Cmd+F`)
    - Move to Trash (`Cmd+T`)
    - Clean Folder (`Cmd+E`)
- **Plugins:**
  Manage plugins from the Plugins button in the Settings section or from the Plugins menu in the menubar. Enable/disable plugins with checkmarks. All valid plugins in the `plugins/` folder are always listed.
- **Logs:**
  Check `cleanup.log` for errors or debugging info.

---

## Plugin System

The cleanup tool is built around a flexible plugin system. Each plugin targets a specific set of caches, logs, or temporary files. Plugins are located in the `plugins/` directory and are auto-discovered at runtime.

### Built-in Plugins

- **Python**: Pip caches, `__pycache__`, Python history
- **Node.js**: Npm caches, `node_modules`
- **Python Installs**: System Python, Homebrew, pyenv installations
- **System Cleanup**: System/user caches, logs, crash reports
- **Developer Tools**: Xcode, Homebrew, CocoaPods, Ruby Gems, Yarn
- **LLM Frameworks**: Ollama, LM Studio, LLaMA.cpp, vLLM, LocalAI
- **Virtual Machines**: Parallels, VMware, VirtualBox, QEMU, UTM

See the `plugins/` folder for details on each plugin's targets.

### Using Plugins

- Enable or disable plugins from the Plugins button in Settings or from the Plugins menu in the menubar.
- Each plugin can be toggled independently. Checkmarks indicate enabled plugins.
- Plugin actions and scan results are integrated into the main UI.

### Developing Plugins

1. **Create a new file** in `plugins/` (e.g., `my_plugin.py`).
2. **Inherit from `PluginBase` and implement the `scan()` method.**

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

**Best Practices:**
- Return a list of dicts with keys: `category`, `name`, `short_name`, `path`, `size`.
- Use `get_size(path)` from `scanner.py` for size calculation.
- Use logging for debug/info.
- Avoid scanning or deleting critical system files.
- Use exclusions for files handled by other plugins.
- Log actions for traceability.

**Testing:**
- Launch the app and enable your plugin from the Plugins menu.
- Check `cleanup.log` for output and errors.

---

## Troubleshooting & FAQ

- **Permissions:** Some folders may require elevated permissions. Run with appropriate rights if needed.
- **Missing dependencies:** Ensure `send2trash` is installed.
- **Logs:** Check `cleanup.log` for errors and debugging info.

---

## Contributing

- Report bugs via [GitHub Issues](https://github.com/XClassicPeter/macos-cleanup-tool/issues).
- Suggest features (note limited capacity for review).
- See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

MIT License. See [LICENSE](LICENSE).

---

## Notice

The concept and implementation of macOS Cleanup Tool are owned by XClassicPeter. See [NOTICE](NOTICE) for details.

---

## Contact

File issues or questions via [GitHub Issues](https://github.com/XClassicPeter/macos-cleanup-tool/issues).
