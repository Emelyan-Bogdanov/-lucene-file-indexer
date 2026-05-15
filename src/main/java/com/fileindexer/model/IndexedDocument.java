package com.fileindexer.model;

import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.document.LongPoint;
import org.apache.lucene.document.StoredField;

public class IndexedDocument {
    private String filePath;
    private String fileName;
    private String content;
    private long lastModified;
    private long fileSize;
    private String mimeType;

    public IndexedDocument(String filePath, String content, String fileName) {
        this.filePath = filePath;
        this.content = content;
        this.fileName = fileName;
    }

    public Document toLuceneDocument() {
        Document doc = new Document();
        doc.add(new StringField("path", filePath, Field.Store.YES));
        doc.add(new TextField("name", fileName, Field.Store.YES));
        doc.add(new TextField("content", content, Field.Store.YES));
        doc.add(new LongPoint("modified", lastModified));
        doc.add(new StoredField("modified", lastModified));
        doc.add(new StoredField("size", fileSize));
        return doc;
    }

    public String getFilePath() {
        return filePath;
    }

    public String getFileName() {
        return fileName;
    }

    public String getContent() {
        return content;
    }

    public long getLastModified() {
        return lastModified;
    }

    public void setLastModified(long lastModified) {
        this.lastModified = lastModified;
    }

    public long getFileSize() {
        return fileSize;
    }

    public void setFileSize(long fileSize) {
        this.fileSize = fileSize;
    }

    public String getMimeType() {
        return mimeType;
    }

    public void setMimeType(String mimeType) {
        this.mimeType = mimeType;
    }
}
