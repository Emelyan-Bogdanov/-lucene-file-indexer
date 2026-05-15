package com.fileindexer.indexing;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class IndexManager {
    private static final Logger logger = LoggerFactory.getLogger(IndexManager.class);

    private final Path indexPath;
    private final Analyzer analyzer;
    private IndexWriter indexWriter;
    private Directory indexDirectory;

    public IndexManager(String indexPath) {
        this.indexPath = Paths.get(indexPath);
        this.analyzer = new StandardAnalyzer();
    }

    public void createIndex() throws IOException {
        logger.info("Creating index at: {}", indexPath);
        if (!Files.exists(indexPath)) {
            Files.createDirectories(indexPath);
            logger.debug("Created index directory: {}", indexPath);
        }
        indexDirectory = FSDirectory.open(indexPath);
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND);
        indexWriter = new IndexWriter(indexDirectory, config);
        logger.debug("Index created successfully");
    }

    public void openIndex() throws IOException {
        logger.info("Opening index at: {}", indexPath);
        if (!indexExists()) {
            logger.warn("Index does not exist, creating new index");
            createIndex();
            return;
        }
        indexDirectory = FSDirectory.open(indexPath);
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND);
        indexWriter = new IndexWriter(indexDirectory, config);
        logger.debug("Index opened successfully");
    }

    public void closeIndex() throws IOException {
        logger.debug("Closing index");
        if (indexWriter != null) {
            indexWriter.close();
            indexWriter = null;
        }
        if (indexDirectory != null) {
            indexDirectory.close();
            indexDirectory = null;
        }
        logger.debug("Index closed");
    }

    public IndexWriter getIndexWriter() {
        return indexWriter;
    }

    public Directory getIndexDirectory() {
        return indexDirectory;
    }

    public Analyzer getAnalyzer() {
        return analyzer;
    }

    public void optimizeIndex() throws IOException {
        logger.info("Optimizing index");
        if (indexWriter != null) {
            indexWriter.commit();
        }
        logger.debug("Index optimization complete");
    }

    public boolean indexExists() {
        return Files.exists(indexPath) && indexPath.toFile().listFiles().length > 0;
    }

    public IndexReader getIndexReader() throws IOException {
        if (indexDirectory == null) {
            indexDirectory = FSDirectory.open(indexPath);
        }
        return DirectoryReader.open(indexDirectory);
    }
}
