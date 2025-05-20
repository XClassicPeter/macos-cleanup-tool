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

<<<<<<< HEAD
Toggle plugins (Python, Nodejs, Python Installs) in the `settings.py` file.

Check `cleanup.log` for errors.

## Plugins

The macOS Cleanup Tool uses a plugin system to scan specific types of temporary files, caches, and artifacts. Each plugin targets a category of cleanup tasks, helping you reclaim disk space. All plugins are enabled by default and can be toggled in the **Plugins** menu. Below is a list of available plugins and what they scan:

- **Python**: Python-related caches and temporary files.
  - Paths: `~/Library/Caches/pip`, `~/.cache/pip`, `~/.python_history`, `~/.ipython/`, `__pycache__` directories.
  - Categories: Pip Cache, Python History, IPython History, Python Cache.

- **Node.js**: Node.js-related caches and modules.
  - Paths: `~/Library/Caches/npm`, `~/.npm`, `node_modules` directories.
  - Categories: NPM Cache, Node.js Cache.

- **Python Installs**: Python installations and virtual environments.
  - Paths: `/Library/Frameworks/Python.framework`, `/usr/local/Cellar/python@*`, `~/.pyenv`, `~/miniconda3/envs`, virtual environments (`venv` with `pyvenv.cfg`).
  - Categories: System Python, Homebrew Python, Pyenv Install, Conda Environment, Virtual Environment.

- **System Cleanup**: General macOS caches, logs, and crash reports.
  - Paths: `/Library/Caches`, `~/Library/Caches`, `/Library/Logs`, `~/Library/Logs`, `~/Library/Logs/DiagnosticReports`, `/Library/Logs/DiagnosticReports`.
  - Categories: System Cache, User Cache, System Logs, User Logs, Crash Reports.

- **Developer Tools**: Artifacts from Apple development and package managers.
  - Paths: `~/Library/Developer/Xcode/DerivedData`, `~/Library/Developer/Xcode/Archives`, `~/Library/Caches/Homebrew`, `~/Library/Caches/CocoaPods`, `~/.gem`, `~/.cache/yarn`.
  - Categories: Xcode Artifacts, Homebrew Cache, CocoaPods Cache, Ruby Gems, Yarn Cache.

- **LLM Frameworks**: Caches and logs from local AI/ML frameworks.
  - Paths: `~/.ollama/models`, `~/.cache/lm_studio`, `~/.cache/llama_cpp`, `~/.cache/vllm`, `~/.localai/{models,logs}`.
  - Categories: Ollama Cache, LM Studio Cache, LLaMA.cpp Cache, vLLM Cache, LocalAI Cache.

- **Virtual Machines**: Disk images, snapshots, and caches from virtualization software.
  - Paths: `~/Parallels`, `~/Documents/Parallels`, `~/Library/Parallels`, `~/vmware`, `~/Documents/Virtual Machines`, `~/VirtualBox VMs`, `~/Library/VirtualBox`, `~/.qemu`, `~/Library/Containers/com.utmapp.UTM/Data/Documents`, `~/Documents/UTM`, `~/Library/Logs/UTM`.
  - Categories: Parallels VM, VMware VM, VirtualBox VM, QEMU VM, UTM VM.
=======
The cleanup tool is built around a flexible plugin system. Each plugin targets a specific set of caches, logs, or temporary files. Plugins are located in the `plugins/` directory and are auto-discovered at runtime.

### Built-in Plugins

- **System Cleanup:**
  - Scans and cleans system/user caches and logs (see `plugins/system_cleanup.py`).
- **Python:**
  - Cleans pip caches, `__pycache__`, Python history (see `plugins/python.py`).
- **Node.js:**
  - Cleans npm caches, `node_modules` (see `plugins/nodejs.py`).
- **Python Installs:**
  - Cleans system Python, Homebrew, and pyenv installations (see `plugins/python_installs.py`).
- **Virtual Machines:**
  - Cleans Parallels, UTM, and related VM files (see `plugins/virtual_machines.py`).
- **LLM Frameworks, Developer Tools:**
  - Cleans caches for machine learning and development tools (see respective plugin files).

### Using Plugins

- Enable or disable plugins from the Plugins button in Settings or from the Plugins menu in the menubar.
- Each plugin can be toggled independently. Checkmarks indicate enabled plugins.
- Plugin actions and scan results are integrated into the main UI.

### Developing Plugins

1. **Create a new file** in `plugins/` (e.g., `my_plugin.py`).
2. **Inherit from `PluginBase`:**
    ```python
    from plugins.plugin_base import PluginBase

    class Plugin(PluginBase):
        def __init__(self):
            super().__init__()
            self.logger.info("My Plugin initialized")

        def scan(self):
            items = []
            # ... populate items ...
            return items
    ```
3. **Implement the `scan()` method:**
    - Return a list of dicts with keys: `category`, `name`, `short_name`, `path`, `size`.
    - Use `get_size(path)` from `scanner.py` for size calculation.
    - Use logging for debug/info.
4. **Test your plugin:**
    - Launch the app and enable your plugin from the Plugins menu.
    - Check `cleanup.log` for output and errors.

**Best Practices:**
- Avoid scanning or deleting critical system files.
- Use exclusions for files handled by other plugins.
- Log actions for traceability.

---

## Troubleshooting & FAQ

- **Permissions:** Some folders may require elevated permissions. Run with appropriate rights if needed.
- **Missing dependencies:** Ensure `send2trash` is installed.
- **Logs:** Check `cleanup.log` for errors and debugging info.

---
>>>>>>> f1864fc (v1.0.1: Robust plugin discovery, improved plugin management UI, persistent checkmarks, and bug fixes\n\n- Plugin discovery now uses importlib and class inspection (only valid PluginBase subclasses are listed)\n- Plugins menu always lists all valid plugins, checkmarks are persistent and visible\n- Plugins button moved to Settings section\n- Improved error handling and logging for plugin loading\n- Updated documentation and changelog for v1.0.1\n- Minor code cleanup and UI improvements\n- Security: safer plugin loading and critical path protection)

## Contributing

- Report bugs via [GitHub Issues](https://github.com/XClassicPeter/macos-cleanup-tool/issues).
- Suggest features (note limited capacity for review).
- See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

MIT License. See [LICENSE](LICENSE).

---

## Notice

The concept and implementation of macOS Cleanup Tool are owned by Peter. See [NOTICE](NOTICE) for details.

---

## Contact

File issues or questions via [GitHub Issues](https://github.com/XClassicPeter/macos-cleanup-tool/issues).
