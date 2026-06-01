import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

from whoosh import index, fields, qparser
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED, NUMERIC, DATETIME
from whoosh.index import create_in, open_dir, exists_in
from whoosh.writing import AsyncWriter

from indexer.document_parser import extract_text
from indexer.metadata import get_file_metadata
from utils.exclusions import is_excluded

FILE_SCHEMA = Schema(
    path=ID(unique=True, stored=True),
    filename=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    extension=KEYWORD(stored=True, lowercase=True),
    content=TEXT(analyzer=StemmingAnalyzer()),
    size=NUMERIC(stored=True, numtype=int),
    created=KEYWORD(stored=True),
    modified=KEYWORD(stored=True),
    mime_type=KEYWORD(stored=True, lowercase=True),
    folder=ID(stored=True),
    tags=TEXT(stored=True),
)


class FileIndexer:
    def __init__(self, index_dir, config=None):
        self.index_dir = index_dir
        self.config = config or {}
        os.makedirs(index_dir, exist_ok=True)
        if not exists_in(index_dir):
            create_in(index_dir, FILE_SCHEMA)
        self.ix = open_dir(index_dir)

    def index_file(self, filepath):
        reason, excluded = is_excluded(filepath, self.config), False
        if isinstance(reason, tuple):
            excluded, _ = reason
        if excluded:
            return False, "excluded"

        text = extract_text(filepath)
        if not text.strip():
            return False, "empty content"

        meta = get_file_metadata(filepath)
        folder_parts = meta.get("folder", "").replace("\\", "/").split("/")
        tags = " ".join(
            t for t in [meta.get("extension", ""), meta.get("mime_type", "")] + folder_parts
            if t.strip() and t != "."
        )
        writer = AsyncWriter(self.ix)
        try:
            writer.update_document(
                path=meta["path"],
                filename=meta["filename"],
                extension=meta["extension"],
                content=text,
                size=meta["size"],
                created=meta["created"],
                modified=meta["modified"],
                mime_type=meta["mime_type"],
                folder=meta["folder"],
                tags=tags,
            )
            writer.commit()
            return True, "indexed"
        except Exception as e:
            writer.cancel()
            return False, str(e)

    def remove_file(self, filepath):
        writer = AsyncWriter(self.ix)
        try:
            writer.delete_by_term("path", filepath)
            writer.commit()
            return True
        except Exception:
            writer.cancel()
            return False

    def scan_directory(self, directory, parallel=True):
        results = {"indexed": 0, "skipped": 0, "errors": 0, "files": []}
        filepaths = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not is_excluded(os.path.join(root, d), self.config)[0] if isinstance(is_excluded(os.path.join(root, d), self.config), tuple)]
            for fname in files:
                fpath = os.path.join(root, fname)
                filepaths.append(fpath)

        if parallel and len(filepaths) > 10:
            with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
                fut_map = {executor.submit(self.index_file, fp): fp for fp in filepaths}
                for fut in as_completed(fut_map):
                    fp = fut_map[fut]
                    try:
                        success, reason = fut.result()
                        if success:
                            results["indexed"] += 1
                            results["files"].append(fp)
                        else:
                            results["skipped"] += 1
                    except Exception:
                        results["errors"] += 1
        else:
            for fp in filepaths:
                try:
                    success, reason = self.index_file(fp)
                    if success:
                        results["indexed"] += 1
                        results["files"].append(fp)
                    else:
                        results["skipped"] += 1
                except Exception:
                    results["errors"] += 1
        return results

    def index_stats(self):
        from whoosh.reading import IndexReader
        reader = self.ix.reader()
        return {
            "total_docs": reader.doc_count(),
            "index_size_mb": self._folder_size(self.index_dir),
        }

    def _folder_size(self, path):
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                try:
                    total += os.path.getsize(os.path.join(dirpath, f))
                except OSError:
                    pass
        return round(total / (1024 * 1024), 2)

    def cleanup_removed_files(self, scan_dirs):
        reader = self.ix.reader()
        all_paths = [list(fields.values())[0] for fields in reader.all_stored_fields()]
        active_paths = set()
        for sd in scan_dirs:
            for root, _, files in os.walk(sd):
                for f in files:
                    active_paths.add(os.path.join(root, f))

        removed = 0
        writer = AsyncWriter(self.ix)
        try:
            for stored in reader.all_stored_fields():
                if stored["path"] not in active_paths:
                    writer.delete_by_term("path", stored["path"])
                    removed += 1
            writer.commit()
        except Exception:
            writer.cancel()
        return removed

    def close(self):
        self.ix.close()

    def get_reader(self):
        return self.ix.reader()

    def get_searcher(self):
        return self.ix.searcher()
