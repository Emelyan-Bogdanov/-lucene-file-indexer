from whoosh import qparser, scoring, sorting
from whoosh.query import (
    And, Or, Not, Term, FuzzyTerm, Wildcard, Regex,
    Phrase, Prefix,
)
from whoosh.analysis import StemmingAnalyzer

from utils.config import load_config


class QueryEngine:
    def __init__(self, ix):
        self.ix = ix
        self.config = load_config()
        self.synonyms = self.config.get("synonyms", {})

    def _expand_synonyms(self, word):
        results = [word]
        for key, syns in self.synonyms.items():
            if word.lower() == key.lower():
                results.extend(syns)
            elif word.lower() in [s.lower() for s in syns]:
                results.append(key)
        return list(set(results))

    def _all_search_fields(self):
        all_fields = ["content", "filename", "extension", "folder", "mime_type", "tags"]
        existing = list(self.ix.schema.names())
        return [f for f in all_fields if f in existing]

    def build_query(self, query_str, search_fields=None):
        if search_fields is None:
            search_fields = self._all_search_fields()

        og = qparser.OrGroup
        parser = qparser.MultifieldParser(search_fields, schema=self.ix.schema, group=og)
        parser.add_plugin(qparser.FuzzyTermPlugin())
        parser.add_plugin(qparser.WildcardPlugin())
        parser.add_plugin(qparser.RegexPlugin())
        parser.add_plugin(qparser.PhrasePlugin())
        parser.add_plugin(qparser.BoostPlugin())
        parser.add_plugin(qparser.GtLtPlugin())
        parser.add_plugin(qparser.RangePlugin())
        parser.add_plugin(qparser.FieldsPlugin())
        parser.add_plugin(qparser.OperatorsPlugin())

        query = parser.parse(query_str)
        return query

    def search(self, query_str, filters=None, sort_by=None, page=1, per_page=20):
        searcher = self.ix.searcher(weighting=scoring.BM25F)
        try:
            query = self.build_query(query_str)

            if filters:
                filter_parts = []
                for key, values in filters.items():
                    if isinstance(values, list):
                        for v in values:
                            filter_parts.append(Term(key, str(v)))
                    else:
                        filter_parts.append(Term(key, str(values)))
                if filter_parts:
                    query = And([query] + filter_parts)

            if sort_by:
                sort_fields = []
                for s in sort_by:
                    reverse = False
                    field = s
                    if s.startswith("-"):
                        field = s[1:]
                        reverse = True
                    if field == "relevance":
                        sort_fields.append(sorting.ScoreFacet(reverse=not reverse))
                    elif field == "date":
                        sort_fields.append(sorting.FieldFacet("modified", reverse=reverse))
                    elif field == "size":
                        sort_fields.append(sorting.FieldFacet("size", reverse=reverse))
                    elif field == "filename":
                        sort_fields.append(sorting.FieldFacet("filename", reverse=reverse))
                    else:
                        sort_fields.append(sorting.FieldFacet(field, reverse=reverse))
                sorter = sorting.MultiFacet(sort_fields)
                results = searcher.search(query, limit=None, sortedby=sorter)
            else:
                results = searcher.search(query, limit=None)

            total = len(results)
            start = (page - 1) * per_page
            end = start + per_page
            page_results = results[start:end]

            output = []
            for hit in page_results:
                output.append({
                    "path": hit["path"],
                    "filename": hit["filename"],
                    "extension": hit["extension"],
                    "size": hit["size"],
                    "created": hit["created"],
                    "modified": hit["modified"],
                    "mime_type": hit["mime_type"],
                    "folder": hit["folder"],
                    "score": hit.score,
                    "highlights": "",
                })

            return output, total, results
        finally:
            searcher.close()

    def get_suggestions(self, prefix, limit=10):
        searcher = self.ix.searcher()
        try:
            reader = self.ix.reader()
            words = []
            fieldnames = self._all_search_fields()
            for fn in fieldnames:
                for word in reader.lexicon(fn):
                    w = word.decode("utf-8") if isinstance(word, bytes) else str(word)
                    if w.lower().startswith(prefix.lower()):
                        words.append(w)
                        if len(words) >= limit:
                            break
                if len(words) >= limit:
                    break
            return words[:limit]
        finally:
            searcher.close()
