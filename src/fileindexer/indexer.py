import fnmatch
import os
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, StringField, TextField, LongField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader, Term
from org.apache.lucene.store import FSDirectory

from .models import IndexedDocument
from .parser import DocumentParser


class IndexManager:
    def __init__(self, index_path: str):
        self.index_path = Path(index_path)
        self.analyzer = StandardAnalyzer()
        self._directory = None
        self._writer = None
        self._reader = None

    def _ensure_dir(self):
        self.index_path.mkdir(parents=True, exist_ok=True)

    @property
    def directory(self):
        if self._directory is None:
            self._ensure_dir()
            self._directory = FSDirectory.open(Paths.get(str(self.index_path)))
        return self._directory

    def get_writer(self, create=False):
        if self._writer is None or not self._writer.isOpen():
            config = IndexWriterConfig(self.analyzer)
            if create:
                config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
            else:
                config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
            self._writer = IndexWriter(self.directory, config)
        return self._writer

    def get_reader(self):
        if self._reader is None:
            self._reader = DirectoryReader.open(self.directory)
        else:
            new_reader = DirectoryReader.openIfChanged(self._reader)
            if new_reader is not None:
                self._reader.close()
                self._reader = new_reader
        return self._reader

    @property
    def num_docs(self):
        try:
            reader = self.get_reader()
            return reader.numDocs()
        except Exception:
            return 0

    def close_writer(self):
        if self._writer is not None:
            try:
                self._writer.close()
            except Exception:
                pass
            self._writer = None

    def close_reader(self):
        if self._reader is not None:
            try:
                self._reader.close()
            except Exception:
                pass
            self._reader = None

    def close(self):
        self.close_writer()
        self.close_reader()
        if self._directory is not None:
            try:
                self._directory.close()
            except Exception:
                pass
            self._directory = None


class FileIndexer:
    def __init__(self, index_manager: IndexManager, parser: DocumentParser, config):
        self.index_manager = index_manager
        self.parser = parser
        self.config = config

    def _should_exclude(self, file_path: Path) -> bool:
        name = file_path.name
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
        for part in file_path.parts:
            if part in self.config.exclude_dirs:
                return True
        return False

    def _create_lucene_document(self, doc: IndexedDocument) -> Document:
        ld = Document()
        ld.add(StringField("path", doc.path, Field.Store.YES))
        ld.add(TextField("filename", doc.filename, Field.Store.YES))
        ld.add(StringField("extension", doc.extension, Field.Store.YES))
        ld.add(LongField("size", doc.size, Field.Store.YES))
        ld.add(LongField("last_modified", doc.last_modified, Field.Store.YES))
        if doc.content:
            ld.add(TextField("content", doc.content, Field.Store.YES))
        return ld

    def _index_single_file(self, file_path: Path) -> IndexedDocument:
        try:
            stat = file_path.stat()
            content = self.parser.extract_text(str(file_path))
            return IndexedDocument(
                path=str(file_path),
                filename=file_path.name,
                extension=file_path.suffix.lower(),
                size=stat.st_size,
                last_modified=int(stat.st_mtime * 1000),
                content=content,
            )
        except Exception:
            return None

    def index_directories(self, progress_callback=None):
        writer = self.index_manager.get_writer()
        all_files = []

        for dir_path_str in self.config.indexed_directories:
            dir_path = Path(dir_path_str)
            if not dir_path.is_dir():
                continue
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if d not in self.config.exclude_dirs]
                for fname in files:
                    fp = Path(root) / fname
                    if self._should_exclude(fp):
                        continue
                    try:
                        if fp.stat().st_size > self.config.max_file_size:
                            continue
                    except OSError:
                        continue
                    all_files.append(fp)

        total = len(all_files)
        for i, fp in enumerate(all_files):
            if progress_callback:
                progress_callback(i + 1, total, str(fp))
            try:
                indexed = self._index_single_file(fp)
                if indexed is not None:
                    ld = self._create_lucene_document(indexed)
                    writer.updateDocument(Term("path", indexed.path), ld)
            except Exception:
                continue

        writer.commit()
        self.index_manager.close_writer()
        self.index_manager.close_reader()
