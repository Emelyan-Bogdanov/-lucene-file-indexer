from typing import List

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader, Term
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher, BooleanQuery, BooleanClause, TermQuery, TopDocs
from org.apache.lucene.search.highlight import (
    Highlighter,
    QueryScorer,
    SimpleHTMLFormatter,
    SimpleFragmenter,
    TokenSources,
)
from org.apache.lucene.store import FSDirectory
from java.nio.file import Paths

from .indexer import IndexManager
from .models import SearchResult, IndexedDocument

HIGHLIGHT_PRE = "<mark>"
HIGHLIGHT_POST = "</mark>"
MAX_SNIPPETS = 3
FRAGMENT_SIZE = 120


class SearchEngine:
    def __init__(self, index_manager: IndexManager):
        self.index_manager = index_manager
        self.analyzer = StandardAnalyzer()

    def _get_searcher(self):
        reader = self.index_manager.get_reader()
        return IndexSearcher(reader), reader

    def _highlight(self, query, field_name: str, field_text: str) -> List[str]:
        try:
            scorer = QueryScorer(query)
            formatter = SimpleHTMLFormatter(HIGHLIGHT_PRE, HIGHLIGHT_POST)
            highlighter = Highlighter(formatter, scorer)
            highlighter.setTextFragmenter(SimpleFragmenter(FRAGMENT_SIZE))
            fragments = highlighter.getBestTextFragments(
                field_text, False, MAX_SNIPPETS
            )
            return [str(frag) for frag in fragments if frag is not None and frag.getScore() > 0]
        except Exception:
            return []

    def _build_query(self, query_text: str) -> BooleanQuery:
        boolean_builder = BooleanQuery.Builder()

        parser_content = QueryParser("content", self.analyzer)
        parser_content.setDefaultOperator(QueryParser.Operator.OR)
        content_query = parser_content.parse(query_text)
        boolean_builder.add(content_query, BooleanClause.Occur.SHOULD)

        parser_name = QueryParser("filename", self.analyzer)
        parser_name.setDefaultOperator(QueryParser.Operator.OR)
        name_query = parser_name.parse(query_text)
        boolean_builder.add(name_query, BooleanClause.Occur.SHOULD)

        return boolean_builder.build()

    def search(self, query_text: str, max_results: int = 100) -> List[SearchResult]:
        query = self._build_query(query_text)
        searcher, reader = self._get_searcher()
        top_docs = searcher.search(query, max_results)

        results = []
        for score_doc in top_docs.scoreDocs:
            doc_id = score_doc.doc
            lucene_doc = searcher.doc(doc_id)
            score = score_doc.score

            content = lucene_doc.get("content") or ""

            snippets = self._highlight(query, "content", content) if content else []
            if not snippets and lucene_doc.get("filename"):
                snippets = self._highlight(
                    query, "filename", lucene_doc.get("filename")
                )

            indexed_doc = IndexedDocument(
                path=lucene_doc.get("path"),
                filename=lucene_doc.get("filename"),
                extension=lucene_doc.get("extension"),
                size=lucene_doc.get("size") or 0,
                last_modified=lucene_doc.get("last_modified") or 0,
                content=content,
            )
            results.append(SearchResult(document=indexed_doc, score=score, snippets=snippets))

        results.sort(key=lambda r: r.score, reverse=True)
        return results
