import json
from pathlib import Path

DEFAULT_CONFIG_DIR = Path.home() / ".fileindexer"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.json"
DEFAULT_INDEX_PATH = DEFAULT_CONFIG_DIR / "index"

DEFAULT_CONFIG = {
    "indexed_directories": [],
    "index_path": str(DEFAULT_INDEX_PATH),
    "auto_index": True,
    "max_file_size_mb": 100,
    "exclude_patterns": ["*.tmp", "*.log", "*.bak", "*~"],
    "exclude_dirs": ["__pycache__", ".git", ".svn", "node_modules", ".mvn"],
}


class AppConfig:
    def __init__(self, config_path=None):
        self.config_path = Path(config_path or DEFAULT_CONFIG_PATH)
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                self.data.update(json.load(f))

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.data, f, indent=2)

    @property
    def indexed_directories(self):
        return self.data["indexed_directories"]

    @indexed_directories.setter
    def indexed_directories(self, val):
        self.data["indexed_directories"] = list(val)
        self.save()

    @property
    def index_path(self):
        return Path(self.data["index_path"])

    @property
    def auto_index(self):
        return self.data["auto_index"]

    @property
    def max_file_size(self):
        return self.data["max_file_size_mb"] * 1024 * 1024

    @property
    def exclude_patterns(self):
        return self.data["exclude_patterns"]

    @property
    def exclude_dirs(self):
        return self.data["exclude_dirs"]
