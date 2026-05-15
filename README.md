# Lucene File Indexer

A fast desktop file search application that indexes and searches your files instantly using Apache Lucene and Tika for full-text indexing across multiple file formats.

## Overview

Lucene File Indexer is a JavaFX-based desktop application that enables rapid full-text search across your file collections. It supports 100+ file formats including PDFs, Word documents, spreadsheets, images with OCR, and more. Built with Apache Lucene for powerful indexing and Apache Tika for document parsing.

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Java | 21 LTS |
| **Build Tool** | Maven | 3.8+ |
| **Search Engine** | Apache Lucene | 9.10.0 |
| **Document Parser** | Apache Tika | 2.9.1 |
| **GUI Framework** | JavaFX | 21.0.2 |
| **JSON I/O** | Gson | 2.10.1 |
| **Logging** | SLF4J + Logback | 2.0.11 / 1.4.14 |
| **Testing** | JUnit 5 + Mockito | 5.10.1 / 5.7.1 |

## Project Structure

```
lucene-file-indexer/
├── src/
│   ├── main/
│   │   ├── java/com/fileindexer/
│   │   │   ├── App.java                 # Application entry point
│   │   │   ├── config/
│   │   │   │   └── AppConfig.java       # Configuration management
│   │   │   ├── indexing/
│   │   │   │   ├── IndexManager.java    # Index lifecycle management
│   │   │   │   ├── FileIndexer.java     # File processing and indexing
│   │   │   │   └── DocumentParser.java  # Tika document parsing
│   │   │   ├── search/
│   │   │   │   └── SearchEngine.java    # Lucene query execution
│   │   │   ├── ui/
│   │   │   │   ├── MainWindow.java      # Main JavaFX window
│   │   │   │   ├── SearchController.java # Search UI logic
│   │   │   │   └── ResultsDisplay.java  # Results presentation
│   │   │   └── model/
│   │   │       ├── SearchResult.java    # Search result data model
│   │   │       └── IndexedDocument.java # Document metadata
│   │   └── resources/
│   │       ├── styles.css               # JavaFX styling
│   │       └── logback.xml              # Logging configuration
│   └── test/
│       └── java/com/fileindexer/
│           ├── indexing/
│           │   └── FileIndexerTest.java
│           └── search/
│               └── SearchEngineTest.java
├── pom.xml                              # Maven configuration
├── README.md                            # Project documentation
├── .gitignore                           # Git ignore rules
└── LICENSE                              # Project license
```

## Setup & Installation

### Prerequisites

- **Java 21 LTS** or higher
  ```bash
  java -version
  ```
- **Maven 3.8+**
  ```bash
  mvn -version
  ```

### Clone the Repository

```bash
git clone https://github.com/yourusername/lucene-file-indexer.git
cd lucene-file-indexer
```

### Build the Project

```bash
mvn clean install
```

This will:
- Download all dependencies
- Compile the source code
- Run tests
- Package the application

### Run the Application

**Option 1: Run with Maven**
```bash
mvn javafx:run
```

**Option 2: Run the JAR file**
```bash
mvn package
java -jar target/file-indexer.jar
```

### Development Setup

```bash
# Install dependencies
mvn install

# Run tests
mvn test

# Run with IDE
# Open the project in IntelliJ IDEA, Eclipse, or VS Code with Maven support
```

## Key Features

- ⚡ **Fast Full-Text Search** - Powered by Apache Lucene
- 📄 **Multi-Format Support** - PDFs, Word, Excel, PowerPoint, Images, and 100+ more
- 🖥️ **Modern GUI** - Built with JavaFX
- ⚙️ **Configurable** - JSON-based configuration for indexed directories
- 🔄 **Auto-Indexing** - File watcher for automatic re-indexing
- 🎯 **Relevance Ranking** - Results sorted by relevance score
- 📊 **Search Snippets** - Context preview of matches

## Configuration

Configuration is stored in `~/.fileindexer/config.json`:

```json
{
  "indexedDirectories": ["/home/user/Documents", "/home/user/Downloads"],
  "indexPath": "~/.fileindexer/index",
  "autoIndex": true,
  "maxFileSize": 104857600,
  "excludePatterns": ["*.tmp", "*.log"]
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.