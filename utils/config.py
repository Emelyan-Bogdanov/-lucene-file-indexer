import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "index_dir": os.path.join(str(Path.home()), ".file_indexer", "index"),
    "scan_dirs": [],
    "exclude_dirs": ["__pycache__", ".git", "node_modules", ".venv", "venv", ".svn", ".hg", ".idea", ".vscode"],
    "exclude_extensions": [".exe", ".dll", ".so", ".dylib", ".bin", ".dat", ".obj", ".o", ".a", ".lib"],
    "exclude_hidden": True,
    "exclude_system": True,
    "max_file_size_mb": 100,
    "parallel_indexing": True,
    "watch_changes": False,
    "shard_size_gb": 10,
    "enable_compression": True,
    "results_per_page": 20,
    "dark_mode": False,
    "recent_searches_max": 50,
    "highlight_matches": True,
    "extension_colors": {
        ".pdf": "#FF6B6B",
        ".docx": "#4ECDC4",
        ".xlsx": "#45B7D1",
        ".pptx": "#96CEB4",
        ".txt": "#FFEAA7",
        ".py": "#DDA0DD",
        ".js": "#F0E68C",
        ".html": "#FFA07A",
        ".css": "#87CEEB",
        ".json": "#98FB98",
        ".xml": "#D3D3D3",
        ".csv": "#F5DEB3",
        ".md": "#E6E6FA",
    },
    "synonyms": {
        "fast": ["quick", "swift", "rapid"],
        "big": ["large", "huge", "enormous"],
        "small": ["tiny", "little", "miniature"],
        "good": ["great", "excellent", "fine"],
        "bad": ["poor", "terrible", "awful"],
    },
}

CONFIG_FILE = os.path.join(str(Path.home()), ".file_indexer", "config.json")


def load_config():
    config_dir = os.path.dirname(CONFIG_FILE)
    os.makedirs(config_dir, exist_ok=True)
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            merged = DEFAULT_CONFIG.copy()
            merged.update(json.load(f))
            return merged
    return DEFAULT_CONFIG.copy()


def save_config(config):
    config_dir = os.path.dirname(CONFIG_FILE)
    os.makedirs(config_dir, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
