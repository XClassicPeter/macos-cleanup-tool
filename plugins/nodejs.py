import os
import logging
from plugins.plugin_base import PluginBase
from scanner import get_size

class Plugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.logger.info("Node.js plugin initialized")

    def scan(self):
        self.logger.info("Starting Node.js plugin scan")
        items = []
        npm_paths = [
            (os.path.expanduser("~/Library/Caches/npm"), "NPM Cache"),
            (os.path.expanduser("~/.npm"), "NPM Cache"),
        ]
        for path, category in npm_paths:
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
            self.logger.info(f"Found Node.js item: {path} ({size})")
        # Scan for node_modules directories in home directory (limited depth)
        home = os.path.expanduser("~")
        for root, dirs, _ in os.walk(home, topdown=True):
            if root[len(home) + 1:].count(os.sep) > 2:  # Limit to depth 2
                dirs[:] = []
                continue
            if "node_modules" in dirs:
                path = os.path.join(root, "node_modules")
                size = get_size(path)
                if size != "0B":
                    items.append({
                        "category": "Node.js Cache",
                        "name": "node_modules",
                        "short_name": "node_modules",
                        "path": path,
                        "size": size
                    })
                    self.logger.info(f"Found node_modules: {path} ({size})")
                dirs.remove("node_modules")  # Avoid redundant scanning
        self.logger.info(f"Node.js plugin scan completed: {len(items)} items found")
        return items