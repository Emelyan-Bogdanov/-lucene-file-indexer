package com.fileindexer.config;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonSyntaxException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class AppConfig {
    private static final Logger logger = LoggerFactory.getLogger(AppConfig.class);
    private static final String CONFIG_DIR = System.getProperty("user.home") + "/.fileindexer";
    private static final String CONFIG_PATH = CONFIG_DIR + "/config.json";

    private List<String> indexedDirectories = new ArrayList<>();
    private String indexPath = CONFIG_DIR + "/index";
    private boolean autoIndex = true;
    private long maxFileSize = 104857600;
    private List<String> excludePatterns = new ArrayList<>();

    public static AppConfig loadConfig() {
        logger.info("Loading configuration from: {}", CONFIG_PATH);
        Path configDir = Paths.get(CONFIG_DIR);
        try {
            if (!Files.exists(configDir)) {
                Files.createDirectories(configDir);
                logger.info("Created config directory: {}", CONFIG_DIR);
            }

            Path configFile = Paths.get(CONFIG_PATH);
            if (!Files.exists(configFile)) {
                logger.info("Config file not found, creating default configuration");
                AppConfig defaultConfig = createDefault();
                defaultConfig.saveConfig();
                return defaultConfig;
            }

            Gson gson = new Gson();
            try (FileReader reader = new FileReader(configFile.toFile())) {
                AppConfig config = gson.fromJson(reader, AppConfig.class);
                logger.info("Configuration loaded successfully");
                return config;
            } catch (JsonSyntaxException e) {
                logger.error("Invalid JSON in config file, using defaults", e);
                AppConfig defaultConfig = createDefault();
                defaultConfig.saveConfig();
                return defaultConfig;
            }
        } catch (IOException e) {
            logger.error("Failed to load configuration", e);
            return createDefault();
        }
    }

    public void saveConfig() throws IOException {
        logger.info("Saving configuration to: {}", CONFIG_PATH);
        Path configDir = Paths.get(CONFIG_DIR);
        if (!Files.exists(configDir)) {
            Files.createDirectories(configDir);
        }

        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        try (FileWriter writer = new FileWriter(CONFIG_PATH)) {
            gson.toJson(this, writer);
        }
        logger.info("Configuration saved successfully");
    }

    private static AppConfig createDefault() {
        AppConfig config = new AppConfig();
        config.indexedDirectories.add(System.getProperty("user.home") + "/Documents");
        config.indexPath = CONFIG_DIR + "/index";
        config.autoIndex = true;
        config.maxFileSize = 104857600;
        config.excludePatterns.add("*.tmp");
        config.excludePatterns.add("*.log");
        return config;
    }

    public List<String> getIndexedDirectories() {
        return indexedDirectories;
    }

    public String getIndexPath() {
        return indexPath;
    }

    public boolean isAutoIndexEnabled() {
        return autoIndex;
    }

    public long getMaxFileSize() {
        return maxFileSize;
    }

    public List<String> getExcludePatterns() {
        return excludePatterns;
    }
}
