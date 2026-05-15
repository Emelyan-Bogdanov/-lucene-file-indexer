package com.fileindexer.search;

import com.fileindexer.indexing.IndexManager;
import com.fileindexer.model.SearchResult;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class SearchEngine {
    private static final Logger logger = LoggerFactory.getLogger(SearchEngine.class);

    private final IndexManager indexManager;
    private static final int DEFAULT_MAX_RESULTS = 100;

    public SearchEngine(IndexManager indexManager) {
        this.indexManager = indexManager;
    }

    public List<SearchResult> search(String queryString) {
        return search(queryString, DEFAULT_MAX_RESULTS);
    }

    public List<SearchResult> search(String queryString, int maxResults) {
        logger.info("Searching for: \"{}\" (max results: {})", queryString, maxResults);
        long startTime = System.currentTimeMillis();

        if (queryString == null || queryString.trim().isEmpty()) {
            logger.warn("Empty search query");
            return List.of();
        }

        List<SearchResult> results = new ArrayList<>();

        try {
            QueryParser parser = new QueryParser("content", indexManager.getAnalyzer());
            Query query = parser.parse(queryString);

            IndexReader reader = indexManager.getIndexReader();
            IndexSearcher searcher = new IndexSearcher(reader);

            TopDocs topDocs = searcher.search(query, maxResults);
            float maxScore = topDocs.getMaxScore();

            for (ScoreDoc scoreDoc : topDocs.scoreDocs) {
                Document doc = searcher.doc(scoreDoc.doc);
                SearchResult result = new SearchResult(
                    doc.get("path"),
                    doc.get("name"),
                    scoreDoc.score,
                    extractSnippet(doc.get("content"))
                );

                if (maxScore > 0) {
                    result.setScorePercentage((scoreDoc.score / maxScore) * 100);
                } else {
                    result.setScorePercentage(0);
                }

                String modifiedStr = doc.get("modified");
                if (modifiedStr != null) {
                    result.setLastModified(Long.parseLong(modifiedStr));
                }

                results.add(result);
            }

            reader.close();

            long elapsed = System.currentTimeMillis() - startTime;
            logger.info("Search completed in {}ms, found {} results", elapsed, results.size());

        } catch (ParseException e) {
            logger.error("Failed to parse query: {}", queryString, e);
        } catch (IOException e) {
            logger.error("IO error during search", e);
        }

        return results;
    }

    private String extractSnippet(String content) {
        if (content == null || content.isEmpty()) {
            return "";
        }
        int length = Math.min(content.length(), 200);
        return content.substring(0, length).replace('\n', ' ').replace('\r', ' ');
    }

    public void close() throws IOException {
        logger.debug("Closing SearchEngine");
    }
}
