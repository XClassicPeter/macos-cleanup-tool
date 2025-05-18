import os
import glob
import logging
from plugins.plugin_base import PluginBase
from scanner import get_size

class Plugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.logger.info("Developer Tools plugin initialized")

    def scan(self):
        self.logger.info("Starting Developer Tools plugin scan")
        items = []
        paths = [
            (os.path.expanduser("~/Library/Developer/Xcode/DerivedData"), "Xcode Artifacts"),
            (os.path.expanduser("~/Library/Developer/Xcode/Archives"), "Xcode Artifacts"),
            (os.path.expanduser("~/Library/Caches/Homebrew"), "Homebrew Cache"),
            (os.path.expanduser("~/Library/Caches/CocoaPods"), "CocoaPods Cache"),
            (os.path.expanduser("~/.gem"), "Ruby Gems"),
            (os.path.expanduser("~/.cache/yarn"), "Yarn Cache"),
        ]
        exclusions = glob.glob(os.path.expanduser("/usr/local/Cellar/python@*"))

        for path, category in paths:
            if not os.path.exists(path):
                self.logger.debug(f"Path does not exist: {path}")
                continue
            if any(path.startswith(excl) for excl in exclusions):
                self.logger.debug(f"Path excluded (handled by python_installs): {path}")
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

        self.logger.info(f"Developer Tools plugin scan completed: {len(items)} items found")
        return items