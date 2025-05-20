# macOS Cleanup Tool
# Copyright (c) 2025 XClassicPeter
# Licensed under the MIT License. See LICENSE for details.

import os
import subprocess
import glob
import importlib.util
import logging
from plugins.plugin_base import PluginBase

CRITICAL_SYSTEM_PATHS = {
    os.path.expanduser(p) for p in [
        "~/Library",
        "~/Documents",
        "~/Desktop",
        "~/Downloads",
        "~/Pictures",
        "~/Music",
        "~/Movies",
        "~/.Trash",
        "/System",
        "/Library",
        "/Applications",
        "/Users",
        "/private",
    ]
}

def get_size(path):
    try:
        if not os.path.exists(path):
            logging.getLogger(__name__).warning(f"Path does not exist: {path}")
            return "0B"
        result = subprocess.run(
            ["du", "-sh", path],
            capture_output=True,
            text=True,
            timeout=30
        )
        size = result.stdout.split("\t")[0]
        return size if size else "0B"
    except (subprocess.SubprocessError, OSError) as e:
        logging.getLogger(__name__).error(f"Failed to get size for {path}: {e}")
        return "0B"

def _should_exclude(path, exclusions):
    path = os.path.expanduser(path)
    for excl in exclusions:
        excl = os.path.expanduser(excl).rstrip("/")
        if path.rstrip("/").startswith(excl):
            logging.getLogger(__name__).info(f"Excluded path: {path}")
            return True
    return False

def load_plugins():
    logger = logging.getLogger(__name__)
    plugins = []
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if not os.path.exists(plugins_dir):
        logger.warning("Plugins directory not found")
        return plugins
    for py_file in glob.glob(os.path.join(plugins_dir, "*.py")):
        module_name = os.path.basename(py_file).replace(".py", "")
        if module_name in ["__init__", "plugin_base"]:
            continue
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        if not spec:
            logger.warning(f"Could not load spec for {module_name}")
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, PluginBase) and attr != PluginBase:
                plugins.append((module_name, attr()))
                logger.info(f"Loaded plugin: {module_name}")
    return plugins

def scan_system(progress_callback=lambda c, p: None, max_depth=3, exclusions=None):
    logger = logging.getLogger(__name__)
    logger.info("Starting system scan")
    if exclusions is None:
        exclusions = []
    items = []
    temp_paths = [
        ("System Temp", "/private/tmp"),
        ("User Temp", os.path.expanduser("~/Library/Caches")),
        ("Logs", "/private/var/log"),
        ("User Logs", os.path.expanduser("~/Library/Logs")),
    ]
    total = len(temp_paths) + 1  # +1 for plugins
    for idx, (category, path) in enumerate(temp_paths):
        if _should_exclude(path, exclusions):
            continue
        size = get_size(path)
        if size != "0B":
            items.append({
                "category": category,
                "name": os.path.basename(path),
                "short_name": os.path.basename(path),
                "path": path,
                "size": size
            })
        progress_callback(category, (idx + 1) / total * 50)
    # Scan plugins
    plugins = load_plugins()
    plugin_items = []
    import settings
    enabled_plugins = settings.load_settings().get("plugins", {})
    for plugin_name, plugin in plugins:
        try:
            if plugin_name in enabled_plugins and not enabled_plugins.get(plugin_name, True):
                logger.info(f"Skipping disabled plugin: {plugin_name}")
                continue
            plugin_items.extend(plugin.scan())
            logger.info(f"Scanned plugin: {plugin_name}")
        except Exception as e:
            logger.error(f"Plugin {plugin_name} failed: {e}")
    for item in plugin_items:
        if not isinstance(item, dict) or not all(k in item for k in ["category", "name", "path", "size"]):
            logger.warning(f"Invalid plugin item: {item}")
            continue
        if _should_exclude(item["path"], exclusions):
            continue
        item["short_name"] = item.get("short_name", item["name"])
        items.append(item)
    progress_callback("Plugins", 100)
    logger.info("System scan completed")
    return items

def scan_folder(folder, category, progress_callback=lambda c, p: None, max_depth=3, exclusions=None):
    logger = logging.getLogger(__name__)
    logger.info(f"Scanning folder: {folder}")
    if exclusions is None:
        exclusions = []
    items = []
    folder = os.path.expanduser(folder)
    if not os.path.isdir(folder) or _should_exclude(folder, exclusions):
        return items
    
    # Track directories scanned for progress estimation
    dir_count = 0
    total_dirs_estimated = 100  # Rough estimate; adjust if needed

    def scan_recursive(path, depth, current_category):
        nonlocal dir_count
        if depth > max_depth:
            return
        try:
            for entry in os.scandir(path):
                if _should_exclude(entry.path, exclusions):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    dir_count += 1
                    size = get_size(entry.path)
                    if size != "0B":
                        items.append({
                            "category": current_category,
                            "name": entry.name,
                            "short_name": entry.name,
                            "path": entry.path,
                            "size": size
                        })
                    # Send progress update (cap at 99% to avoid premature 100%)
                    progress = min(99, (dir_count / total_dirs_estimated) * 100)
                    progress_callback(current_category, progress)
                    logger.debug(f"Progress: {current_category} ({progress:.1f}%)")
                    scan_recursive(entry.path, depth + 1, current_category)
        except (PermissionError, OSError) as e:
            logger.error(f"Error scanning {path}: {e}")

    scan_recursive(folder, 1, category)
    # Final progress update
    progress_callback(category, 100)
    logger.info(f"Folder scan completed: {folder}, {len(items)} items found")
    return items
