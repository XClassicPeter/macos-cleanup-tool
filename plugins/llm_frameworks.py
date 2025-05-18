import os
import logging
from plugins.plugin_base import PluginBase
from scanner import get_size

class Plugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.logger.info("LLM Frameworks plugin initialized")

    def scan(self):
        self.logger.info("Starting LLM Frameworks plugin scan")
        items = []
        paths = [
            (os.path.expanduser("~/.ollama/models"), "Ollama Cache"),
            (os.path.expanduser("~/.cache/lm_studio"), "LM Studio Cache"),
            (os.path.expanduser("~/.cache/llama_cpp"), "LLaMA.cpp Cache"),
            (os.path.expanduser("~/.cache/vllm"), "vLLM Cache"),
            (os.path.expanduser("~/.localai/models"), "LocalAI Cache"),
            (os.path.expanduser("~/.localai/logs"), "LocalAI Logs"),
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

        self.logger.info(f"LLM Frameworks plugin scan completed: {len(items)} items found")
        return items