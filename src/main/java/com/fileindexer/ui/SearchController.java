package com.fileindexer.ui;

import com.fileindexer.model.SearchResult;
import com.fileindexer.search.SearchEngine;
import javafx.application.Platform;
import javafx.concurrent.Task;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

public class SearchController {
    private static final Logger logger = LoggerFactory.getLogger(SearchController.class);

    private final SearchEngine searchEngine;
    private final ResultsDisplay resultsDisplay;
    private final TextField queryInput;
    private final Label statusLabel;
    private final Label resultCountLabel;
    private final Label searchTimeLabel;

    public SearchController(SearchEngine searchEngine, ResultsDisplay resultsDisplay,
                            TextField queryInput, Label statusLabel,
                            Label resultCountLabel, Label searchTimeLabel) {
        this.searchEngine = searchEngine;
        this.resultsDisplay = resultsDisplay;
        this.queryInput = queryInput;
        this.statusLabel = statusLabel;
        this.resultCountLabel = resultCountLabel;
        this.searchTimeLabel = searchTimeLabel;
    }

    public void onSearchButtonClicked() {
        String query = queryInput.getText().trim();
        if (!query.isEmpty()) {
            executeSearch(query);
        }
    }

    public void onSearchKeyPressed(javafx.scene.input.KeyEvent event) {
        if (event.getCode() == javafx.scene.input.KeyCode.ENTER) {
            String query = queryInput.getText().trim();
            if (!query.isEmpty()) {
                executeSearch(query);
            }
        }
    }

    private void executeSearch(String query) {
        logger.info("Search triggered for query: \"{}\"", query);
        statusLabel.setText("Searching...");
        resultCountLabel.setText("");
        searchTimeLabel.setText("");

        Task<List<SearchResult>> searchTask = new Task<>() {
            @Override
            protected List<SearchResult> call() {
                logger.debug("Starting search task for: \"{}\"", query);
                return searchEngine.search(query);
            }
        };

        searchTask.setOnSucceeded(event -> {
            List<SearchResult> results = searchTask.getValue();
            logger.info("Search completed with {} results", results.size());
            resultsDisplay.updateResults(results);
            statusLabel.setText("Ready");
            resultCountLabel.setText(results.size() + " results found");
            searchTimeLabel.setText("");
        });

        searchTask.setOnFailed(event -> {
            logger.error("Search failed", searchTask.getException());
            statusLabel.setText("Search failed");
            resultCountLabel.setText("Error occurred");
            searchTimeLabel.setText("");
        });

        new Thread(searchTask).start();
    }
}
