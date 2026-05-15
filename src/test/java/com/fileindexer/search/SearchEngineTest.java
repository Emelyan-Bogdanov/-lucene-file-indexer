package com.fileindexer.search;

import com.fileindexer.indexing.DocumentParser;
import com.fileindexer.indexing.FileIndexer;
import com.fileindexer.indexing.IndexManager;
import com.fileindexer.config.AppConfig;
import com.fileindexer.model.SearchResult;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class SearchEngineTest {
    private Path tempIndexDir;
    private Path tempFileDir;
    private IndexManager indexManager;
    private SearchEngine searchEngine;

    @BeforeEach
    void setUp() throws Exception {
        tempIndexDir = Files.createTempDirectory("lucene-test-search-index");
        tempFileDir = Files.createTempDirectory("lucene-test-search-files");

        AppConfig appConfig = new AppConfig();
        indexManager = new IndexManager(tempIndexDir.toString());
        DocumentParser documentParser = new DocumentParser(104857600);
        FileIndexer fileIndexer = new FileIndexer(indexManager, documentParser, appConfig);

        Files.writeString(tempFileDir.resolve("doc1.txt"), "The quick brown fox jumps over the lazy dog");
        Files.writeString(tempFileDir.resolve("doc2.txt"), "Apache Lucene is a powerful search engine library");
        Files.writeString(tempFileDir.resolve("doc3.txt"), "Java is a programming language");

        indexManager.createIndex();
        fileIndexer.indexDirectory(tempFileDir.toString());
        indexManager.optimizeIndex();

        searchEngine = new SearchEngine(indexManager);
    }

    @AfterEach
    void tearDown() throws IOException {
        indexManager.closeIndex();
        deleteDirectory(tempIndexDir);
        deleteDirectory(tempFileDir);
    }

    @Test
    void testSimpleSearch() {
        List<SearchResult> results = searchEngine.search("lucene");
        assertFalse(results.isEmpty(), "Should find results for 'lucene'");
    }

    @Test
    void testSearchNoResults() {
        List<SearchResult> results = searchEngine.search("nonexistenttermxyz123");
        assertTrue(results.isEmpty(), "Should return empty list for non-existent term");
    }

    @Test
    void testSearchResultRelevanceRanking() {
        List<SearchResult> results = searchEngine.search("search");
        assertFalse(results.isEmpty(), "Should find results for 'search'");
        if (results.size() >= 2) {
            assertTrue(results.get(0).getScore() >= results.get(1).getScore(),
                "Results should be ranked by relevance");
        }
    }

    @Test
    void testEmptyQuery() {
        List<SearchResult> results = searchEngine.search("");
        assertTrue(results.isEmpty(), "Should return empty list for empty query");
    }

    @Test
    void testSearchResultHasFilePath() {
        List<SearchResult> results = searchEngine.search("lucene");
        assertFalse(results.isEmpty());
        SearchResult result = results.get(0);
        assertNotNull(result.getFilePath(), "Result should have a file path");
        assertTrue(result.getFilePath().contains("doc2"), "Should point to the correct document");
    }

    private void deleteDirectory(Path path) throws IOException {
        if (Files.exists(path)) {
            try (var files = Files.walk(path)) {
                files.sorted(java.util.Comparator.reverseOrder())
                     .forEach(p -> {
                         try { Files.deleteIfExists(p); }
                         catch (IOException e) { /* ignore cleanup errors */ }
                     });
            }
        }
    }
}
