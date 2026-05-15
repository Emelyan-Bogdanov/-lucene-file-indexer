package com.fileindexer.ui;

import com.fileindexer.config.AppConfig;
import com.fileindexer.indexing.FileIndexer;
import com.fileindexer.indexing.IndexManager;
import com.fileindexer.search.SearchEngine;
import javafx.scene.Parent;
import javafx.application.Platform;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;

public class MainWindow {
    private static final Logger logger = LoggerFactory.getLogger(MainWindow.class);

    private final AppConfig appConfig;
    private final IndexManager indexManager;
    private final SearchEngine searchEngine;
    private final FileIndexer fileIndexer;
    private final ResultsDisplay resultsDisplay;
    private SearchController searchController;

    private final TextField queryInput = new TextField();
    private final Button searchButton = new Button("Search");
    private final Label statusLabel = new Label("Ready");
    private final Label resultCountLabel = new Label("");
    private final Label searchTimeLabel = new Label("");

    public MainWindow(AppConfig appConfig) {
        this.appConfig = appConfig;
        this.indexManager = new IndexManager(appConfig.getIndexPath());
        this.searchEngine = new SearchEngine(indexManager);
        this.fileIndexer = new FileIndexer(
            indexManager,
            new com.fileindexer.indexing.DocumentParser(appConfig.getMaxFileSize()),
            appConfig
        );
        this.resultsDisplay = new ResultsDisplay();
    }

    public Parent createMainScene() {
        logger.info("Creating main window scene");

        BorderPane root = new BorderPane();

        VBox topPanel = new VBox(5);
        topPanel.setStyle("-fx-padding: 10px;");

        HBox searchBox = new HBox(5);
        queryInput.setPromptText("Enter search query...");
        queryInput.getStyleClass().add("search-bar");
        queryInput.setPrefHeight(35);
        queryInput.setPrefWidth(600);
        searchButton.getStyleClass().add("search-button");
        searchBox.getChildren().addAll(queryInput, searchButton);

        Button indexButton = new Button("Index Directories");
        indexButton.setOnAction(e -> indexDirectories());
        searchBox.getChildren().add(indexButton);

        topPanel.getChildren().add(searchBox);

        root.setTop(topPanel);

        resultsDisplay.getTableView().setPrefHeight(500);
        root.setCenter(resultsDisplay.getTableView());

        HBox statusBar = new HBox(15);
        statusBar.getStyleClass().add("status-bar");
        statusBar.getChildren().addAll(statusLabel, resultCountLabel, searchTimeLabel);
        root.setBottom(statusBar);

        this.searchController = new SearchController(
            searchEngine, resultsDisplay, queryInput,
            statusLabel, resultCountLabel, searchTimeLabel
        );

        searchButton.setOnAction(e -> searchController.onSearchButtonClicked());
        queryInput.setOnKeyPressed(e -> searchController.onSearchKeyPressed(e));

        logger.info("Main window scene created");
        return root;
    }

    private void indexDirectories() {
        logger.info("Index directories triggered");
        statusLabel.setText("Indexing...");
        resultCountLabel.setText("");
        searchTimeLabel.setText("");

        new Thread(() -> {
            try {
                indexManager.createIndex();
                for (String dir : appConfig.getIndexedDirectories()) {
                    fileIndexer.indexDirectory(dir);
                }
                indexManager.optimizeIndex();
                indexManager.closeIndex();

                Platform.runLater(() -> {
                    statusLabel.setText("Ready");
                    resultCountLabel.setText("Indexed: " + fileIndexer.getFilesIndexed()
                        + ", Skipped: " + fileIndexer.getFilesSkipped());
                    logger.info("Indexing complete. Indexed: {}, Skipped: {}",
                        fileIndexer.getFilesIndexed(), fileIndexer.getFilesSkipped());
                });
            } catch (IOException e) {
                logger.error("Indexing failed", e);
                Platform.runLater(() -> {
                    statusLabel.setText("Indexing failed");
                    resultCountLabel.setText("Error: " + e.getMessage());
                });
            }
        }).start();
    }

    public void shutdown() {
        logger.info("Shutting down application");
        try {
            indexManager.closeIndex();
            searchEngine.close();
        } catch (IOException e) {
            logger.error("Error during shutdown", e);
        }
    }
}
