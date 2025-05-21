import os
import logging
from plugins.plugin_base import PluginBase
from scanner import get_size

class Plugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.logger.info("Virtual Machines plugin initialized")

    def scan(self):
        self.logger.info("Starting Virtual Machines plugin scan")
        items = []
        paths = [
            (os.path.expanduser("~/Parallels"), "Parallels VM"),
            (os.path.expanduser("~/Documents/Parallels"), "Parallels VM"),
            (os.path.expanduser("~/Library/Parallels"), "Parallels VM"),
            (os.path.expanduser("~/vmware"), "VMware VM"),
            (os.path.expanduser("~/Documents/Virtual Machines"), "VMware VM"),
            (os.path.expanduser("~/VirtualBox VMs"), "VirtualBox VM"),
            (os.path.expanduser("~/Library/VirtualBox"), "VirtualBox VM"),
            (os.path.expanduser("~/.qemu"), "QEMU VM"),
            (os.path.expanduser("~/Library/Containers/com.utmapp.UTM/Data/Documents"), "UTM VM"),
            (os.path.expanduser("~/Documents/UTM"), "UTM VM"),
            (os.path.expanduser("~/Library/Logs/UTM"), "UTM VM"),
            (os.path.expanduser("~/.wine"), "Wine"),
            (os.path.expanduser("~/Library/Application Support/com.codeweavers.CrossOver"), "CrossOver"),
            (os.path.expanduser("~/Library/Application Support/Heroic"), "Heroic Games Launcher"),
            (os.path.expanduser("~/Library/Containers/com.isaacmarovitz.Whisky"), "Whisky"),
            (os.path.expanduser("~/Library/Application Support/CrossOver"), "CrossOver"),
        ]

        for path, category in paths:
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

        self.logger.info(f"Virtual Machines plugin scan completed: {len(items)} items found")
        return items