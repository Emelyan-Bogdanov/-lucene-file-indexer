import json
import os
from datetime import datetime
from pathlib import Path

HISTORY_FILE = os.path.join(str(Path.home()), ".file_indexer", "search_history.json")
SAVED_FILE = os.path.join(str(Path.home()), ".file_indexer", "saved_searches.json")


def load_search_history():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_search_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def add_to_history(query, max_items=50):
    history = load_search_history()
    entry = {"query": query, "timestamp": datetime.now().isoformat()}
    history = [h for h in history if h["query"] != query]
    history.insert(0, entry)
    history = history[:max_items]
    save_search_history(history)


def load_saved_searches():
    os.makedirs(os.path.dirname(SAVED_FILE), exist_ok=True)
    if os.path.exists(SAVED_FILE):
        with open(SAVED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_saved_searches(saved):
    os.makedirs(os.path.dirname(SAVED_FILE), exist_ok=True)
    with open(SAVED_FILE, "w", encoding="utf-8") as f:
        json.dump(saved, f, indent=2, ensure_ascii=False)


def save_search(name, query, filters=None):
    saved = load_saved_searches()
    saved[name] = {
        "query": query,
        "filters": filters or {},
        "timestamp": datetime.now().isoformat(),
    }
    save_saved_searches(saved)


def delete_saved_search(name):
    saved = load_saved_searches()
    saved.pop(name, None)
    save_saved_searches(saved)
