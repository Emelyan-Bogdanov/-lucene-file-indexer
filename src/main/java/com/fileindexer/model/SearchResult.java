package com.fileindexer.model;

public class SearchResult {
    private String filePath;
    private String fileName;
    private float score;
    private float scorePercentage;
    private String snippet;
    private long lastModified;

    public SearchResult(String filePath, String fileName, float score, String snippet) {
        this.filePath = filePath;
        this.fileName = fileName;
        this.score = score;
        this.snippet = snippet;
    }

    public String getFilePath() {
        return filePath;
    }

    public String getFileName() {
        return fileName;
    }

    public float getScore() {
        return score;
    }

    public float getScorePercentage() {
        return scorePercentage;
    }

    public void setScorePercentage(float scorePercentage) {
        this.scorePercentage = scorePercentage;
    }

    public String getSnippet() {
        return snippet;
    }

    public long getLastModified() {
        return lastModified;
    }

    public void setLastModified(long lastModified) {
        this.lastModified = lastModified;
    }
}
