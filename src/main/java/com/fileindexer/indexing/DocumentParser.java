package com.fileindexer.indexing;

import org.apache.tika.Tika;
import org.apache.tika.exception.TikaException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

public class DocumentParser {
    private static final Logger logger = LoggerFactory.getLogger(DocumentParser.class);

    private final Tika tika;
    private final long maxFileSize;

    public DocumentParser(long maxFileSize) {
        this.tika = new Tika();
        this.maxFileSize = maxFileSize;
    }

    public String parseFile(File file) {
        logger.debug("Parsing file: {}", file.getName());
        if (!file.exists() || !file.isFile()) {
            logger.warn("File does not exist or is not a file: {}", file.getPath());
            return "";
        }
        if (!file.canRead()) {
            logger.warn("File is not readable: {}", file.getPath());
            return "";
        }
        if (file.length() > maxFileSize) {
            logger.warn("File exceeds max size ({} > {}): {}", file.length(), maxFileSize, file.getName());
            return "";
        }
        try (InputStream stream = new FileInputStream(file)) {
            String content = tika.parseToString(stream);
            logger.debug("Successfully parsed file: {} ({} chars)", file.getName(), content.length());
            return content.trim();
        } catch (TikaException e) {
            logger.warn("Tika parsing error for file: {}", file.getName(), e);
            return "";
        } catch (IOException e) {
            logger.error("IO error parsing file: {}", file.getName(), e);
            return "";
        }
    }
}
