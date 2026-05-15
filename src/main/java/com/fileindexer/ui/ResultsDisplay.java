package com.fileindexer.ui;

import com.fileindexer.model.SearchResult;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.scene.control.TableCell;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.input.MouseButton;
import javafx.scene.input.MouseEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.awt.Desktop;
import java.io.File;
import java.io.IOException;
import java.util.List;

public class ResultsDisplay {
    private static final Logger logger = LoggerFactory.getLogger(ResultsDisplay.class);

    private final TableView<SearchResult> tableView;
    private final ObservableList<SearchResult> data;

    public ResultsDisplay() {
        this.tableView = new TableView<>();
        this.data = FXCollections.observableArrayList();
        setupTable();
    }

    private void setupTable() {
        tableView.getStyleClass().add("results-table");

        TableColumn<SearchResult, String> nameCol = new TableColumn<>("File Name");
        nameCol.setCellValueFactory(new PropertyValueFactory<>("fileName"));
        nameCol.setPrefWidth(250);

        TableColumn<SearchResult, String> pathCol = new TableColumn<>("Path");
        pathCol.setCellValueFactory(new PropertyValueFactory<>("filePath"));
        pathCol.setPrefWidth(400);

        TableColumn<SearchResult, Number> scoreCol = new TableColumn<>("Relevance");
        scoreCol.setCellValueFactory(new PropertyValueFactory<>("scorePercentage"));
        scoreCol.setPrefWidth(100);
        scoreCol.setCellFactory(col -> new TableCell<>() {
            @Override
            protected void updateItem(Number item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setText(null);
                    setStyle("");
                } else {
                    setText(String.format("%.0f%%", item.floatValue()));
                    float val = item.floatValue();
                    if (val >= 80) {
                        setStyle("-fx-background-color: #c8e6c9;");
                    } else if (val >= 50) {
                        setStyle("-fx-background-color: #fff9c4;");
                    } else {
                        setStyle("");
                    }
                }
            }
        });

        tableView.getColumns().addAll(nameCol, pathCol, scoreCol);
        tableView.setItems(data);

        tableView.setOnMouseClicked(this::onResultClicked);
    }

    private void onResultClicked(MouseEvent event) {
        if (event.getButton() == MouseButton.PRIMARY && event.getClickCount() == 2) {
            SearchResult selected = tableView.getSelectionModel().getSelectedItem();
            if (selected != null) {
                openFile(selected.getFilePath());
            }
        }
    }

    private void openFile(String filePath) {
        try {
            if (Desktop.isDesktopSupported()) {
                Desktop.getDesktop().open(new File(filePath));
                logger.info("Opened file: {}", filePath);
            }
        } catch (IOException e) {
            logger.error("Failed to open file: {}", filePath, e);
        }
    }

    public void updateResults(List<SearchResult> results) {
        data.clear();
        data.addAll(results);
    }

    public void clearResults() {
        data.clear();
    }

    public TableView<SearchResult> getTableView() {
        return tableView;
    }
}
