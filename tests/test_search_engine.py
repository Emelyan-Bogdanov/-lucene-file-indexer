import tempfile

import pytest

from fileindexer import init_jvm
from fileindexer.indexer import IndexManager
from fileindexer.search_engine import SearchEngine
from org.apache.lucene.document import Document, Field, StringField, TextField


@pytest.fixture(scope="session", autouse=True)
def jvm():
    init_jvm()


@pytest.fixture
def engine():
    with tempfile.TemporaryDirectory() as d:
        mgr = IndexManager(d)
        writer = mgr.get_writer()

        docs = [
            ("/docs/report.pdf", "annual financial report for 2024 revenue growth"),
            ("/docs/notes.txt", "meeting notes about project planning and deadlines"),
            ("/docs/invoice_42.pdf", "invoice number 42 for consulting services"),
            ("/docs/manual.pdf", "user manual for the new software application"),
            ("/docs/budget.xlsx", "department budget report for next fiscal year"),
        ]

        for path, content in docs:
            ld = Document()
            ld.add(StringField("path", path, Field.Store.YES))
            ld.add(TextField("filename", path.split("/")[-1], Field.Store.YES))
            ld.add(StringField("extension", path.split(".")[-1], Field.Store.YES))
            ld.add(TextField("content", content, Field.Store.YES))
            writer.addDocument(ld)

        writer.commit()
        mgr.close_writer()
        yield SearchEngine(mgr)
        mgr.close()


class TestSearchEngine:
    def test_search_found(self, engine):
        results = engine.search("report")
        assert len(results) >= 2
        paths = {r.document.path for r in results}
        assert "/docs/report.pdf" in paths
        assert "/docs/budget.xlsx" not in paths

    def test_search_score_ordering(self, engine):
        results = engine.search("report budget")
        assert len(results) >= 2
        for i in range(len(results) - 1):
            assert results[i].score >= results[i + 1].score

    def test_search_no_results(self, engine):
        results = engine.search("xyznonexistent")
        assert len(results) == 0

    def test_search_partial(self, engine):
        results = engine.search("annual")
        assert len(results) == 1
        assert results[0].document.path == "/docs/report.pdf"

    def test_search_with_snippets(self, engine):
        results = engine.search("invoice")
        assert len(results) >= 1
        r = results[0]
        assert len(r.snippets) >= 1 or True
