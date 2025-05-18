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
        python_paths = [
            ("/Library/Frameworks/Python.framework", "System Python"),
            ("/Library/Python", "System Python Library"),
            (os.path.expanduser("~/.pyenv"), "Pyenv Install"),
            ("/usr/local/Cellar/python", "Homebrew Python"),
        ]
        homebrew_python = glob.glob("/usr/local/Cellar/python@*")
        python_paths.extend([(path, "Homebrew Python") for path in homebrew_python])

        conda_paths = [
            (os.path.expanduser("~/miniconda3/envs"), "Conda Environment"),
            (os.path.expanduser("~/anaconda3/envs"), "Conda Environment"),
            ("/opt/anaconda3/envs", "Conda Environment"),
            ("/opt/miniconda3/envs", "Conda Environment"),
        ]

        for path, category in python_paths + conda_paths:
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
            self.logger.info(f"Found {category}: {path} ({size})")

        home = os.path.expanduser("~")
        for root, dirs, files in os.walk(home, topdown=True):
            if root[len(home) + 1:].count(os.sep) > 2:
                dirs[:] = []
                continue
            if "pyvenv.cfg" in files:
                path = root
                size = get_size(path)
                if size != "0B":
                    name = os.path.basename(path)
                    items.append({
                        "category": "Virtual Environment",
                        "name": name,
                        "short_name": name,
                        "path": path,
                        "size": size
                    })
                    self.logger.info(f"Found Virtual Environment: {path} ({size})")
                else:
                    self.logger.debug(f"Empty or inaccessible venv: {path}")
                dirs[:] = []

        self.logger.info(f"Python Installs plugin scan completed: {len(items)} items found")
        return items
