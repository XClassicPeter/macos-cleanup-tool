import logging

class PluginBase:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def scan(self):
        """
        Scan for items (e.g., caches, temp files) and return a list of dictionaries.
        Each dictionary must contain: category, name, short_name, path, size.
        Subclasses must implement this method.
        """
        self.logger.error(f"scan() not implemented in {self.__class__.__name__}")
        raise NotImplementedError("Plugin must implement scan() method")