import os
import logging
from plugins.plugin_base import PluginBase
from scanner import get_size

class Plugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.logger.info("Python plugin initialized")

    def scan(self):
        self.logger.info("Starting Python plugin scan")
        items = []
        python_paths = [
            (os.path.expanduser("~/Library/Caches/pip"), "Pip Cache"),
            (os.path.expanduser("~/.cache/pip"), "Pip Cache"),
            (os.path.expanduser("~/.python_history"), "Python History"),
            (os.path.expanduser("~/.ipython/profile_default/history.sqlite"), "IPython History"),
        ]
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
            self.logger.info(f"Found Python item: {path} ({size})")
        # Scan for __pycache__ directories in home directory (limited depth)
        home = os.path.expanduser("~")
        for root, dirs, _ in os.walk(home, topdown=True):
            if root[len(home) + 1:].count(os.sep) > 2:  # Limit to depth 2
                dirs[:] = []
                continue
            if "__pycache__" in dirs:
                path = os.path.join(root, "__pycache__")
                size = get_size(path)
                if size != "0B":
                    items.append({
                        "category": "Python Cache",
                        "name": "__pycache__",
                        "short_name": "__pycache__",
                        "path": path,
                        "size": size
                    })
                    self.logger.info(f"Found __pycache__: {path} ({size})")
                dirs.remove("__pycache__")  # Avoid redundant scanning
        self.logger.info(f"Python plugin scan completed: {len(items)} items found")
        return items