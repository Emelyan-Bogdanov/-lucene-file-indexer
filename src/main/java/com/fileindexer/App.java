package com.fileindexer;

import com.fileindexer.config.AppConfig;
import com.fileindexer.ui.MainWindow;
import javafx.application.Application;
import javafx.scene.Scene;
import javafx.stage.Stage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App extends Application {
    private static final Logger logger = LoggerFactory.getLogger(App.class);

    private MainWindow mainWindow;

    public static void main(String[] args) {
        logger.info("Starting Lucene File Indexer");
        Application.launch(args);
    }

    @Override
    public void start(Stage primaryStage) {
        logger.info("Loading application configuration");

        AppConfig appConfig = AppConfig.loadConfig();

        logger.info("Initializing main window");
        mainWindow = new MainWindow(appConfig);

        Scene scene = new Scene(mainWindow.createMainScene(), 900, 600);
        scene.getStylesheets().add(getClass().getResource("/styles.css").toExternalForm());

        primaryStage.setTitle("Lucene File Indexer");
        primaryStage.setScene(scene);
        primaryStage.setMinWidth(600);
        primaryStage.setMinHeight(400);

        primaryStage.setOnCloseRequest(event -> {
            logger.info("Application closing");
            mainWindow.shutdown();
        });

        primaryStage.show();
        logger.info("Application ready");
    }
}
