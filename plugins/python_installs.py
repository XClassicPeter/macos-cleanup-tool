import os
import glob
import logging
from plugins.plugin_base import PluginBase
from scanner import get_size

class Plugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.logger.info("Python Installs plugin initialized")

    def scan(self):
        self.logger.info("Starting Python Installs plugin scan")
        items = []
        # Common Python installation paths on macOS
        python_paths = [
            ("/Library/Frameworks/Python.framework/Versions", "System Python"),
            ("/Library/Python", "System Python Library"),
            (os.path.expanduser("~/.pyenv"), "Pyenv Install"),
            ("/usr/local/Cellar/python", "Homebrew Python"),  # For older Homebrew installs
        ]
        # Add Homebrew Python versions (e.g., /usr/local/Cellar/python@3.10)
        homebrew_python = glob.glob("/usr/local/Cellar/python@*")
        python_paths.extend([(path, "Homebrew Python") for path in homebrew_python])

        for path, category in python_paths:
            if not os.path.exists(path):
                self.logger.debug(f"Path does not exist: {path}")
                continue
            size = get_size(path)
            if size == "0B":
                self.logger.debug(f"Empty or inaccessible path: {path}")
                continue
            name = os.path.basename(path)
            items.append({
                "category": category,
                "name": name,
                "short_name": name,
                "path": path,
                "size": size
            })
            self.logger.info(f"Found Python installation: {path} ({size})")

        self.logger.info(f"Python Installs plugin scan completed: {len(items)} items found")
        return items