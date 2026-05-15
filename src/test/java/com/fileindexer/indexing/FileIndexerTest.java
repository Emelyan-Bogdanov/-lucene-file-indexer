package com.fileindexer.indexing;

import com.fileindexer.config.AppConfig;
import com.fileindexer.model.IndexedDocument;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.Term;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.TermQuery;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

public class FileIndexerTest {
    private Path tempIndexDir;
    private Path tempFileDir;
    private IndexManager indexManager;
    private DocumentParser documentParser;
    private FileIndexer fileIndexer;
    private AppConfig appConfig;

    @BeforeEach
    void setUp() throws IOException {
        tempIndexDir = Files.createTempDirectory("lucene-test-index");
        tempFileDir = Files.createTempDirectory("lucene-test-files");

        appConfig = new AppConfig();
        indexManager = new IndexManager(tempIndexDir.toString());
        documentParser = new DocumentParser(104857600);
        fileIndexer = new FileIndexer(indexManager, documentParser, appConfig);
    }

    @AfterEach
    void tearDown() throws IOException {
        deleteDirectory(tempIndexDir);
        deleteDirectory(tempFileDir);
    }

    @Test
    void testIndexTextFile() throws Exception {
        Path testFile = tempFileDir.resolve("test.txt");
        Files.writeString(testFile, "Hello world, this is a test document for indexing.");

        indexManager.createIndex();
        fileIndexer.indexDirectory(tempFileDir.toString());
        indexManager.closeIndex();

        try (Directory dir = FSDirectory.open(tempIndexDir);
             IndexReader reader = DirectoryReader.open(dir)) {
            assertEquals(1, reader.numDocs(), "Should have indexed one file");
        }
    }

    @Test
    void testIndexMultipleFiles() throws Exception {
        Files.writeString(tempFileDir.resolve("file1.txt"), "Content of file one");
        Files.writeString(tempFileDir.resolve("file2.txt"), "Content of file two");
        Files.writeString(tempFileDir.resolve("file3.txt"), "Content of file three");

        indexManager.createIndex();
        fileIndexer.indexDirectory(tempFileDir.toString());
        indexManager.closeIndex();

        try (Directory dir = FSDirectory.open(tempIndexDir);
             IndexReader reader = DirectoryReader.open(dir)) {
            assertEquals(3, reader.numDocs(), "Should have indexed three files");
        }
    }

    @Test
    void testSkipUnsupportedFormat() throws Exception {
        Files.writeString(tempFileDir.resolve("test.txt"), "Valid text file");
        Files.writeString(tempFileDir.resolve("test.xyz"), "Unsupported format");

        indexManager.createIndex();
        fileIndexer.indexDirectory(tempFileDir.toString());
        indexManager.closeIndex();

        try (Directory dir = FSDirectory.open(tempIndexDir);
             IndexReader reader = DirectoryReader.open(dir)) {
            assertTrue(reader.numDocs() >= 1, "Should index at least the text file");
        }
    }

    @Test
    void testIndexingProgressCallback() throws Exception {
        Files.writeString(tempFileDir.resolve("file1.txt"), "Content one");
        Files.writeString(tempFileDir.resolve("file2.txt"), "Content two");

        indexManager.createIndex();
        fileIndexer.indexDirectory(tempFileDir.toString());
        indexManager.closeIndex();

        assertEquals(2, fileIndexer.getFilesIndexed());
        assertEquals(0, fileIndexer.getFilesSkipped());
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
