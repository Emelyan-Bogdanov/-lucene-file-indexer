import tempfile
from pathlib import Path

import pytest

from fileindexer import init_jvm
from fileindexer.config import AppConfig
from fileindexer.indexer import IndexManager
from fileindexer.models import IndexedDocument


@pytest.fixture(scope="session", autouse=True)
def jvm():
    init_jvm()


@pytest.fixture
def temp_index():
    with tempfile.TemporaryDirectory() as d:
        yield d


class TestIndexManager:
    def test_open_and_close(self, temp_index):
        mgr = IndexManager(temp_index)
        assert mgr.index_path.exists()
        mgr.close()

    def test_writer_and_reader(self, temp_index):
        mgr = IndexManager(temp_index)
        writer = mgr.get_writer()
        assert writer is not None
        writer.commit()
        reader = mgr.get_reader()
        assert reader is not None
        assert reader.numDocs() == 0
        mgr.close()

    def test_add_document(self, temp_index):
        from org.apache.lucene.document import Document, Field, StringField, TextField
        from org.apache.lucene.index import Term

        mgr = IndexManager(temp_index)
        writer = mgr.get_writer()

        ld = Document()
        ld.add(StringField("path", "/test/doc.txt", Field.Store.YES))
        ld.add(TextField("content", "hello world", Field.Store.YES))
        writer.addDocument(ld)
        writer.commit()
        mgr.close_writer()

        assert mgr.num_docs == 1
        mgr.close()

    def test_num_docs_empty(self, temp_index):
        mgr = IndexManager(temp_index)
        assert mgr.num_docs == 0
        mgr.close()
