package com.fileindexer.indexing;

import com.fileindexer.config.AppConfig;
import com.fileindexer.model.IndexedDocument;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Stream;

public class FileIndexer {
    private static final Logger logger = LoggerFactory.getLogger(FileIndexer.class);

    private final IndexManager indexManager;
    private final DocumentParser documentParser;
    private final AppConfig appConfig;
    private final AtomicInteger filesIndexed = new AtomicInteger(0);
    private final AtomicInteger filesSkipped = new AtomicInteger(0);

    public FileIndexer(IndexManager indexManager, DocumentParser documentParser, AppConfig appConfig) {
        this.indexManager = indexManager;
        this.documentParser = documentParser;
        this.appConfig = appConfig;
    }

    public int getFilesIndexed() {
        return filesIndexed.get();
    }

    public int getFilesSkipped() {
        return filesSkipped.get();
    }

    public void indexDirectory(String dirPath) throws IOException {
        logger.info("Indexing directory: {}", dirPath);
        filesIndexed.set(0);
        filesSkipped.set(0);

        Path dir = Paths.get(dirPath);
        if (!Files.exists(dir) || !Files.isDirectory(dir)) {
            logger.warn("Directory does not exist: {}", dirPath);
            return;
        }

        try (Stream<Path> fileStream = Files.walk(dir)) {
            List<Path> files = fileStream
                .filter(Files::isRegularFile)
                .filter(this::shouldIndex)
                .toList();

            for (Path filePath : files) {
                try {
                    indexFile(filePath.toFile());
                } catch (Exception e) {
                    logger.error("Failed to index file: {}", filePath, e);
                    filesSkipped.incrementAndGet();
                }
            }
        }

        logger.info("Indexing complete. Indexed: {}, Skipped: {}", filesIndexed.get(), filesSkipped.get());
    }

    private void indexFile(File file) throws IOException {
        logger.debug("Indexing file: {}", file.getPath());
        String content = documentParser.parseFile(file);

        if (content.isEmpty()) {
            logger.debug("Skipping file (empty content): {}", file.getName());
            filesSkipped.incrementAndGet();
            return;
        }

        IndexedDocument indexedDoc = new IndexedDocument(file.getAbsolutePath(), content, file.getName());
        indexedDoc.setLastModified(file.lastModified());
        indexedDoc.setFileSize(file.length());

        indexManager.getIndexWriter().addDocument(indexedDoc.toLuceneDocument());
        filesIndexed.incrementAndGet();
        logger.debug("Indexed file: {}", file.getName());
    }

    private boolean shouldIndex(Path filePath) {
        String fileName = filePath.getFileName().toString().toLowerCase();
        List<String> excludePatterns = appConfig.getExcludePatterns();

        for (String pattern : excludePatterns) {
            if (pattern.startsWith("*.")) {
                String ext = pattern.substring(1);
                if (fileName.endsWith(ext)) {
                    return false;
                }
            }
        }

        if (fileName.startsWith(".")) {
            return false;
        }

        long fileSize = filePath.toFile().length();
        if (fileSize > appConfig.getMaxFileSize()) {
            logger.debug("Skipping large file: {} ({} bytes)", fileName, fileSize);
            return false;
        }

        return true;
    }
}
