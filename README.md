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
