import os
import threading
import time

from indexer.engine import FileIndexer
from utils.config import load_config


class FileWatcher:
    def __init__(self, indexer, scan_dirs, interval=5.0):
        self.indexer = indexer
        self.scan_dirs = scan_dirs
        self.interval = interval
        self._running = False
        self._thread = None
        self._known_files = set()

    def start(self):
        self._build_known_set()
        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _build_known_set(self):
        reader = self.indexer.ix.reader()
        try:
            for stored in reader.all_stored_fields():
                self._known_files.add(stored.get("path", ""))
        finally:
            reader.close()

    def _watch_loop(self):
        while self._running:
            current_files = set()
            for sd in self.scan_dirs:
                if os.path.isdir(sd):
                    for root, _, files in os.walk(sd):
                        for f in files:
                            current_files.add(os.path.join(root, f))

            new_files = current_files - self._known_files
            removed_files = self._known_files - current_files

            for fpath in new_files:
                if os.path.isfile(fpath):
                    self.indexer.index_file(fpath)
                    self._known_files.add(fpath)

            for fpath in removed_files:
                self.indexer.remove_file(fpath)
                self._known_files.discard(fpath)

            self._known_files = self._known_files & current_files
            time.sleep(self.interval)
