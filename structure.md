# Project Structure & File Descriptions

This document provides a detailed breakdown of the Lucene File Indexer project structure and explains the purpose and responsibility of each file.

## Directory Tree

```
lucene-file-indexer/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── fileindexer/
│   │   │           ├── App.java
│   │   │           ├── config/
│   │   │           │   └── AppConfig.java
│   │   │           ├── indexing/
│   │   │           │   ├── IndexManager.java
│   │   │           │   ├── FileIndexer.java
│   │   │           │   └── DocumentParser.java
│   │   │           ├── search/
│   │   │           │   └── SearchEngine.java
│   │   │           ├── ui/
│   │   │           │   ├── MainWindow.java
│   │   │           │   ├── SearchController.java
│   │   │           │   └── ResultsDisplay.java
│   │   │           └── model/
│   │   │               ├── SearchResult.java
│   │   │               └── IndexedDocument.java
│   │   └── resources/
│   │       ├── styles.css
│   │       └── logback.xml
│   └── test/
│       └── java/
│           └── com/
│               └── fileindexer/
│                   ├── indexing/
│                   │   └── FileIndexerTest.java
│                   └── search/
│                       └── SearchEngineTest.java
├── pom.xml
├── README.md
├── SKILLS.md
├── STRUCTURE.md
├── .gitignore
└── LICENSE
```

---

## File Descriptions

### Root Level

#### `pom.xml`
- **Purpose**: Maven build configuration file
- **Responsibilities**:
  - Declares all project dependencies (Lucene, Tika, JavaFX, Gson, SLF4J)
  - Defines build plugins (compiler, shade plugin, JavaFX plugin)
  - Configures Maven build properties (source/target Java version, encoding)
  - Specifies test framework configuration
- **Key Sections**:
  - `<properties>` - Version management for easy updates
  - `<dependencies>` - All runtime and test dependencies
  - `<build><plugins>` - Build and execution configuration

#### `README.md`
- **Purpose**: Project documentation for users and developers
- **Contains**:
  - Project overview and description
  - Tech stack table
  - Project structure overview
  - Setup and installation instructions
  - Build and run commands
  - Configuration information

#### `SKILLS.md`
- **Purpose**: Coding guidelines for AI agents generating code
- **Contains**:
  - Core principles and constraints
  - Technology allowlist/blocklist
  - Logging requirements and patterns
  - Code style guidelines
  - JavaFX development patterns
  - Error handling approaches
  - Testing guidelines
  - Documentation standards

#### `STRUCTURE.md` (This File)
- **Purpose**: Detailed documentation of project structure and file responsibilities
- **Contains**:
  - Directory tree
  - File-by-file descriptions
  - Class responsibilities and interactions
  - MVP (Minimal Viable Product) scope

#### `.gitignore`
- **Purpose**: Specifies files/directories Git should ignore
- **Includes**:
  - Maven target directory
  - IDE configuration files (.idea, .classpath, etc.)
  - OS-specific files (.DS_Store)
  - Local configuration directory (.fileindexer/)

#### `LICENSE`
- **Purpose**: Project license file (MIT recommended)
- **Content**: Standard MIT license text

---

## Source Code Structure

### 1. Entry Point: `App.java`

**Location**: `src/main/java/com/fileindexer/App.java`

**Purpose**: Application entry point and main window launcher

**Responsibilities**:
- `main(String[] args)` - Entry point, calls Application.launch()
- Extends `javafx.application.Application`
- `start(Stage primaryStage)` - Initializes and displays the main window
- Loads configuration on startup
- Creates and passes MainWindow to primary stage
- Handles application shutdown

**Dependencies**:
- `MainWindow`
- `AppConfig`
- SLF4J Logger

**Key Methods**:
```java
public static void main(String[] args)
public void start(Stage primaryStage)
```

**Example Behavior**:
1. Logs application startup
2. Loads AppConfig from disk
3. Creates MainWindow instance
4. Sets up window scene and shows it
5. Logs application ready

---

### 2. Configuration Management

#### `config/AppConfig.java`

**Location**: `src/main/java/com/fileindexer/config/AppConfig.java`

**Purpose**: Manages application configuration (load/save from JSON)

**Responsibilities**:
- Load configuration from `~/.fileindexer/config.json`
- Save configuration back to JSON
- Provide default configuration if file doesn't exist
- Validate configuration values
- Provide getter methods for all configuration options

**Key Fields**:
- `indexedDirectories` - List of directories to index
- `indexPath` - Location where Lucene index is stored
- `autoIndex` - Whether to automatically re-index
- `maxFileSize` - Maximum file size to process (e.g., 100MB)
- `excludePatterns` - File patterns to skip during indexing

**Key Methods**:
```java
public static AppConfig loadConfig() throws IOException
public void saveConfig() throws IOException
public List<String> getIndexedDirectories()
public String getIndexPath()
public long getMaxFileSize()
public boolean isAutoIndexEnabled()
```

**JSON Structure Example**:
```json
{
  "indexedDirectories": ["/home/user/Documents"],
  "indexPath": "~/.fileindexer/index",
  "autoIndex": true,
  "maxFileSize": 104857600,
  "excludePatterns": ["*.tmp", "*.log"]
}
```

**Error Handling**:
- Catches `FileNotFoundException` - creates default config
- Catches `JsonSyntaxException` - logs error and uses defaults
- Always creates `.fileindexer/` directory if it doesn't exist

---

### 3. Indexing Module

#### `indexing/IndexManager.java`

**Location**: `src/main/java/com/fileindexer/indexing/IndexManager.java`

**Purpose**: Manages Lucene index lifecycle (creation, opening, closing, optimization)

**Responsibilities**:
- Create a new Lucene index
- Open existing index for reading/writing
- Close index properly
- Optimize index after bulk indexing
- Manage IndexWriter and IndexReader instances
- Handle index corruption/recovery

**Key Fields**:
- `indexPath` - Directory path where index is stored
- `indexWriter` - Lucene IndexWriter instance
- `indexDirectory` - Lucene Directory instance
- `analyzer` - Text analyzer (StandardAnalyzer)

**Key Methods**:
```java
public void createIndex(String indexPath) throws IOException
public void openIndex() throws IOException
public void closeIndex() throws IOException
public IndexWriter getIndexWriter() throws IOException
public void optimizeIndex() throws IOException
public boolean indexExists()
```

**Example Lifecycle**:
1. `createIndex()` - Initialize new FSDirectory and IndexWriter
2. Other classes use `getIndexWriter()` to add documents
3. `optimizeIndex()` - Consolidate index segments
4. `closeIndex()` - Release resources

**Error Handling**:
- Throws IOException for all operations
- Logs all index operations at DEBUG level
- Ensures IndexWriter is closed even if exceptions occur

---

#### `indexing/FileIndexer.java`

**Location**: `src/main/java/com/fileindexer/indexing/FileIndexer.java`

**Purpose**: Walks file system and indexes files using Tika and Lucene

**Responsibilities**:
- Recursively find files in specified directories
- Filter files by extension/size/patterns
- Parse documents using DocumentParser (Tika)
- Create Lucene Document objects
- Add documents to index via IndexManager
- Track indexing progress and statistics
- Handle indexing errors gracefully

**Key Fields**:
- `indexManager` - Reference to IndexManager
- `documentParser` - Reference to DocumentParser
- `appConfig` - Reference to AppConfig
- `filesIndexed` - Counter for statistics
- `filesSkipped` - Counter for skipped files

**Key Methods**:
```java
public void indexDirectory(String dirPath) throws IOException
public void indexDirectory(String dirPath, ProgressCallback callback) throws IOException
private void indexFile(File file) throws Exception
private boolean shouldIndex(File file)
private void createLuceneDocument(File file, String content)
public IndexingStats getStatistics()
```

**Example Flow**:
1. `indexDirectory("/home/user/Documents")`
2. Walks file tree recursively
3. For each file, checks `shouldIndex()`
4. Calls `DocumentParser.parse(file)` to extract text
5. Creates Lucene Document with fields:
   - `path` - full file path
   - `name` - file name
   - `content` - extracted text content
   - `modified` - last modified timestamp
6. Adds to index via `IndexManager.getIndexWriter().addDocument()`
7. Logs progress and skipped files

**Progress Callback**:
- Optional callback for UI progress updates
- Called after each file indexed
- Provides file name and current count

**Filtering Logic**:
- Skip directories in excludePatterns
- Skip files larger than maxFileSize
- Skip unsupported file types (return empty content from parser)
- Skip hidden files by default

---

#### `indexing/DocumentParser.java`

**Location**: `src/main/java/com/fileindexer/indexing/DocumentParser.java`

**Purpose**: Extracts text content from files using Apache Tika

**Responsibilities**:
- Accept a file, extract its text content
- Handle 100+ file formats (PDF, Word, Excel, etc.)
- Return empty string for unsupported formats (don't throw)
- Handle parsing errors gracefully
- Respect file size limits during parsing
- Log parsing results (success, errors, unsupported types)

**Key Fields**:
- Tika `Parser` instance
- Max file size limit

**Key Methods**:
```java
public String parseFile(File file) throws IOException, TikaException
private String extractTextWithTika(File file) throws IOException, TikaException
public boolean isSupportedFormat(File file)
```

**Example Implementation Logic**:
1. Check file exists and is readable
2. Check file size <= maxFileSize
3. Use Tika AutoDetectParser to parse file
4. Extract content as text string
5. Clean up whitespace
6. Return content
7. Catch TikaException - log warning and return empty string

**Supported Formats** (via Tika):
- Documents: PDF, Word (.docx, .doc), Excel, PowerPoint
- Text: .txt, .csv, .xml, .json
- Archives: ZIP, TAR, GZIP (extracts and indexes contents)
- Images: With OCR capability (optional, for MVP just extract metadata)
- Web: HTML, XML

**Error Handling**:
- TikaException - log warning, return empty string
- IOException - log error, rethrow (file permission issue)
- UnsupportedOperationException - log debug, return empty string

---

### 4. Search Module

#### `search/SearchEngine.java`

**Location**: `src/main/java/com/fileindexer/search/SearchEngine.java`

**Purpose**: Executes searches against Lucene index and returns results

**Responsibilities**:
- Accept search queries (strings)
- Parse query syntax (e.g., "filename AND content")
- Execute search against Lucene index
- Score and rank results by relevance
- Return SearchResult objects with metadata
- Handle query errors gracefully
- Close searcher/reader properly

**Key Fields**:
- `indexManager` - Reference to IndexManager
- `searcher` - Lucene IndexSearcher instance
- `analyzer` - Text analyzer for query parsing

**Key Methods**:
```java
public List<SearchResult> search(String queryString) throws Exception
public List<SearchResult> search(String queryString, int maxResults) throws Exception
private Query parseQuery(String queryString) throws ParseException
private SearchResult createResultFromDocument(Document doc, ScoreDoc scoreDoc)
public void close() throws IOException
```

**Example Flow**:
1. `search("file management")`
2. Parses query string using QueryParser
3. Creates default query across "content" field
4. Executes search with TopScoreDocCollector
5. Iterates through results, creates SearchResult objects:
   - File path
   - File name
   - Relevance score
   - Score percentage (0-100)
   - Content snippet (first 200 chars)
6. Returns sorted list by relevance

**Query Syntax Support** (MVP):
- Simple keyword search (default to "content" field)
- Optional: Support for `filename:report` syntax
- Optional: Boolean operators (AND, OR, NOT)

**Result Ranking**:
- Lucene provides relevance score
- Convert to percentage (score / maxScore * 100)
- Higher scores = more relevant
- Display top 100 results by default

**Error Handling**:
- ParseException from QueryParser - log error, show user message
- IOException from searcher - log error, attempt recovery
- Return empty list instead of throwing (graceful degradation)

---

### 5. UI Module

#### `ui/MainWindow.java`

**Location**: `src/main/java/com/fileindexer/ui/MainWindow.java`

**Purpose**: Creates the main JavaFX window and layout

**Responsibilities**:
- Build the main window UI structure
- Create layout with search bar, results area, status bar
- Initialize SearchController
- Handle window events (close, resize)
- Update status/progress information
- Wire together UI components

**Key Layout**:
- Top: Search bar (TextField) + Search button
- Center: Results table/list
- Bottom: Status bar showing index info, search time, result count

**Key Methods**:
```java
public Parent createMainScene()
public void updateStatus(String message)
public void displayResults(List<SearchResult> results)
```

**JavaFX Structure**:
```
BorderPane (root)
├── Top: VBox (search controls)
│   ├── HBox
│   │   ├── TextField (queryInput)
│   │   ├── Button (searchButton)
│   │   └── Button (configButton)
├── Center: TableView<SearchResult> (resultsTable)
└── Bottom: HBox (statusBar)
    ├── Label (statusText)
    ├── Label (resultCountLabel)
    └── Label (searchTimeLabel)
```

**Key Components**:
- `TextField queryInput` - Input field for search query
- `Button searchButton` - Triggers search
- `Button configButton` - Opens configuration dialog (future)
- `TableView resultsTable` - Displays search results
- `Label statusText` - Shows status messages
- `Label resultCountLabel` - Shows "X results found"
- `Label searchTimeLabel` - Shows "Search took XXms"

---

#### `ui/SearchController.java`

**Location**: `src/main/java/com/fileindexer/ui/SearchController.java`

**Purpose**: Handles search UI logic and events

**Responsibilities**:
- Listen to search button clicks
- Get query from input field
- Call SearchEngine to execute search
- Run search in background thread (not blocking UI)
- Update results display on completion
- Show error messages if search fails
- Update status and timing information

**Key Fields**:
- `searchEngine` - Reference to SearchEngine
- `mainWindow` - Reference to MainWindow
- `lastSearchTime` - Track search performance

**Key Methods**:
```java
public void onSearchButtonClicked()
public void onSearchKeyPressed(KeyEvent event)
private void executeSearch(String query)
private void displayResults(List<SearchResult> results)
private void showError(String message, Exception e)
```

**Search Execution Pattern** (Using JavaFX Task):
1. Get query text from input field
2. Create `Task<List<SearchResult>>` to run search in background
3. Set `onSucceeded` callback to update UI with results
4. Set `onFailed` callback to show error message
5. Start task on new thread: `new Thread(searchTask).start()`
6. Show loading indicator while searching
7. Update status with search time and result count

**Error Handling**:
- Catch all exceptions in task
- Log errors
- Show user-friendly error message
- Don't crash on bad queries

**Performance**:
- Measure and log search time
- Display search time to user ("Search took 125ms")
- Show result count clearly

---

#### `ui/ResultsDisplay.java`

**Location**: `src/main/java/com/fileindexer/ui/ResultsDisplay.java`

**Purpose**: Formats and displays search results in UI

**Responsibilities**:
- Create table columns for results (name, path, score, relevance)
- Format SearchResult objects for display
- Handle result selection/clicks
- Show file preview on double-click (open file)
- Update display with new results
- Style result rows based on relevance score

**Key Methods**:
```java
public void updateResults(List<SearchResult> results)
public void clearResults()
private TableColumn<SearchResult, ?> createNameColumn()
private TableColumn<SearchResult, ?> createPathColumn()
private TableColumn<SearchResult, ?> createScoreColumn()
private void onResultDoubleClicked(SearchResult result)
```

**Table Columns**:
1. **File Name** - Result file name (clickable/sortable)
2. **Path** - Full file path (truncated in display)
3. **Relevance** - Score as percentage (0-100)
4. **Modified** - Last modified date (optional for MVP)

**Result Row Styling**:
- Color code background by relevance:
  - 80-100: Green (very relevant)
  - 50-80: Yellow (relevant)
  - 0-50: Default (less relevant)

**Interactions**:
- Single click: Select/highlight result
- Double click: Open file in default application
- Right click: Context menu (copy path, open folder) - optional for MVP

---

### 6. Data Models

#### `model/SearchResult.java`

**Location**: `src/main/java/com/fileindexer/model/SearchResult.java`

**Purpose**: Data class representing a single search result

**Responsibilities**:
- Hold search result information
- Calculate and store relevance percentage
- Provide getters for UI display

**Key Fields**:
```java
private String filePath;           // Full path to file
private String fileName;           // Just the filename
private float score;               // Lucene relevance score
private float scorePercentage;     // Score as 0-100
private String snippet;            // Preview of matching content
private long lastModified;         // File modification time
```

**Key Methods**:
```java
public SearchResult(String filePath, String fileName, float score, String snippet)
public String getFilePath()
public String getFileName()
public float getScore()
public float getScorePercentage()
public String getSnippet()
public long getLastModified()
```

**Example Usage**:
```java
SearchResult result = new SearchResult(
    "/home/user/Documents/report.pdf",
    "report.pdf",
    42.5f,
    "This is a snippet of matching content..."
);
```

**No Business Logic** - Just a data container (POJO)

---

#### `model/IndexedDocument.java`

**Location**: `src/main/java/com/fileindexer/model/IndexedDocument.java`

**Purpose**: Data class representing a document in the index

**Responsibilities**:
- Hold metadata about an indexed document
- Provide structure for creating Lucene documents
- Store extraction metadata

**Key Fields**:
```java
private String filePath;       // Full file path
private String fileName;       // File name only
private String content;        // Extracted text content
private long lastModified;     // Modification timestamp
private long fileSize;         // File size in bytes
private String mimeType;       // MIME type (from Tika)
```

**Key Methods**:
```java
public IndexedDocument(String filePath, String content, String fileName)
public org.apache.lucene.document.Document toLuceneDocument()
// Getters for all fields
```

**toLuceneDocument() Method**:
- Converts to Lucene Document object
- Creates fields:
  - `path` - Stored, not analyzed (full path)
  - `name` - Stored, analyzed (file name)
  - `content` - Stored + analyzed (text content)
  - `modified` - Stored as long (modification time)
  - `size` - Stored as long (file size)

**No Business Logic** - Primarily a data container with conversion utility

---

### 7. Resources

#### `resources/logback.xml`

**Location**: `src/main/resources/logback.xml`

**Purpose**: Configure SLF4J/Logback logging

**Configuration Includes**:
- Log format (timestamp, level, logger name, message)
- File output location (`~/.fileindexer/logs/app.log`)
- Console output for development
- Log levels per package:
  - `DEBUG` for com.fileindexer (development)
  - `INFO` for org.apache.lucene (libraries)
  - `WARN` for org.apache.tika (libraries)

**Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%-5level] %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <appender name="FILE" class="ch.qos.logback.core.FileAppender">
        <file>${user.home}/.fileindexer/logs/app.log</file>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%-5level] %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <root level="DEBUG">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
    </root>
    
    <logger name="org.apache.lucene" level="INFO"/>
    <logger name="org.apache.tika" level="WARN"/>
</configuration>
```

---

#### `resources/styles.css`

**Location**: `src/main/resources/styles.css`

**Purpose**: JavaFX CSS styling for the application

**Styling Includes**:
- Window background color
- Search bar styling
- Button styling
- Table view styling
- Status bar styling
- Result row highlighting based on relevance

**Example Classes**:
- `.search-bar` - Search input field
- `.search-button` - Search button
- `.results-table` - Results table
- `.result-row-high` - High relevance styling
- `.result-row-med` - Medium relevance styling
- `.status-bar` - Status bar styling

---

### 8. Testing

#### `test/java/com/fileindexer/indexing/FileIndexerTest.java`

**Location**: `src/test/java/com/fileindexer/indexing/FileIndexerTest.java`

**Purpose**: Unit tests for FileIndexer functionality

**Test Cases**:
- `testIndexTextFile()` - Index a simple text file and verify it's searchable
- `testIndexMultipleFiles()` - Index multiple files and count indexed documents
- `testSkipUnsupportedFormat()` - Verify unsupported files are skipped
- `testSkipLargeFile()` - Verify large files are skipped
- `testIndexingProgressCallback()` - Verify progress callback is called

**Setup/Teardown**:
- Create temporary index directory for each test
- Clean up temporary files after each test
- Use temporary file system to avoid side effects

---

#### `test/java/com/fileindexer/search/SearchEngineTest.java`

**Location**: `src/test/java/com/fileindexer/search/SearchEngineTest.java`

**Purpose**: Unit tests for SearchEngine functionality

**Test Cases**:
- `testSimpleSearch()` - Search for a keyword and verify results
- `testSearchNoResults()` - Search for non-existent term returns empty list
- `testSearchResultRelevanceRanking()` - Verify results are ranked by relevance
- `testSearchWithSpecialCharacters()` - Handle special characters in query
- `testEmptyQuery()` - Handle empty search gracefully

**Setup/Teardown**:
- Create index with test documents
- Clean up after each test
- Use in-memory or temporary index

---

## Module Dependencies & Interactions

### Startup Flow
```
App.main()
  ↓
App.start()
  ↓
AppConfig.loadConfig()
  ↓
MainWindow.createMainScene()
  ↓
SearchController initialized
  ↓
IndexManager.openIndex()
  ↓
SearchEngine initialized
  ↓
UI Ready
```

### Search Flow
```
User types query & presses Enter
  ↓
SearchController.onSearchKeyPressed()
  ↓
SearchController.executeSearch(query)
  ↓
Task.call() runs in background thread
  ↓
SearchEngine.search(query)
  ↓
Lucene Query Parser → IndexSearcher → results
  ↓
Task.onSucceeded()
  ↓
ResultsDisplay.updateResults()
  ↓
MainWindow.updateStatus()
```

### Indexing Flow
```
Manual: User clicks "Index Directory" (future)
  OR
App startup: Index loaded from disk
  ↓
IndexManager.openIndex()
  ↓
FileIndexer.indexDirectory(path)
  ↓
For each file:
  - DocumentParser.parseFile()
  - FileIndexer.createLuceneDocument()
  - IndexWriter.addDocument()
  ↓
IndexManager.optimizeIndex()
  ↓
IndexManager.closeIndex()
```

---

## MVP (Minimal Viable Product) Scope

**What's included in the first working version:**

✅ App.java - Entry point
✅ AppConfig - Load/save JSON config
✅ IndexManager - Create and manage Lucene index
✅ FileIndexer - Index text files in directory
✅ DocumentParser - Extract text with Tika
✅ SearchEngine - Execute searches on index
✅ MainWindow - Simple UI with search bar
✅ SearchController - Handle search events
✅ ResultsDisplay - Show results in table
✅ SearchResult - Result data class
✅ Logback - Logging throughout
✅ Unit tests - Basic test coverage

**NOT included in MVP (future enhancements):**

❌ File watcher for auto-indexing
❌ Configuration UI dialog
❌ Advanced search syntax (field queries)
❌ File preview/preview pane
❌ Export search results
❌ Saved searches
❌ Search history
❌ OCR for images
❌ Advanced filtering options
❌ Index optimization UI
❌ Batch operations

---

## File Statistics for MVP

| Category | Count | Purpose |
|----------|-------|---------|
| **Main Java Classes** | 10 | Core functionality |
| **Test Classes** | 2 | Unit test coverage |
| **Resource Files** | 2 | Configuration & styling |
| **Config Files** | 1 | Maven build |
| **Documentation** | 4 | README, SKILLS, STRUCTURE, .gitignore |

**Total Java Classes**: 12
**Total Lines of Code** (estimated for MVP): 2000-3000
**Test Coverage**: 40-50% (focus on business logic)