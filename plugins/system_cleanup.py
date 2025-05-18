import os
import logging
from plugins.plugin_base import PluginBase
from scanner import get_size

class Plugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.logger.info("System Cleanup plugin initialized")

    def scan(self):
        self.logger.info("Starting System Cleanup plugin scan")
        items = []
        paths = [
            ("/Library/Caches", "System Cache"),
            (os.path.expanduser("~/Library/Caches"), "User Cache"),
            ("/Library/Logs", "System Logs"),
            (os.path.expanduser("~/Library/Logs"), "User Logs"),
            (os.path.expanduser("~/Library/Logs/DiagnosticReports"), "Crash Reports"),
            ("/Library/Logs/DiagnosticReports", "Crash Reports"),
        ]
        exclusions = [
            os.path.expanduser("~/Library/Caches/pip"),
            os.path.expanduser("~/.cache/pip"),
            os.path.expanduser("~/Library/Caches/npm"),
            os.path.expanduser("~/.npm"),
            os.path.expanduser("~/Library/Caches/CocoaPods"),
            os.path.expanduser("~/Library/Caches/Homebrew"),
            os.path.expanduser("~/.cache/yarn"),
            os.path.expanduser("~/.cache/lm_studio"),
            os.path.expanduser("~/.ollama"),
            os.path.expanduser("~/.cache/vllm"),
            os.path.expanduser("~/.localai"),
            os.path.expanduser("~/Library/Parallels"),
            os.path.expanduser("~/Library/Containers/com.utmapp.UTM"),
            os.path.expanduser("~/Library/Logs/UTM"),
        ]

        for path, category in paths:
            if not os.path.exists(path):
                self.logger.debug(f"Path does not exist: {path}")
                continue
            if any(path.startswith(excl) for excl in exclusions):
                self.logger.debug(f"Path excluded (handled by other plugin): {path}")
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

        self.logger.info(f"System Cleanup plugin scan completed: {len(items)} items found")
        return items