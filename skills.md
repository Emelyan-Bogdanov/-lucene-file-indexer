# Skills & Coding Guidelines for Lucene File Indexer

This document outlines the skills, best practices, and constraints the AI agent should follow when generating code for the Lucene File Indexer project.

## Core Principles

1. **Minimal & Working First** - Build the simplest version that works before adding features
2. **No Over-Engineering** - Avoid patterns, frameworks, or abstractions unless explicitly needed
3. **Clean & Readable Code** - Write code that is easy to understand and maintain
4. **Follow Java Conventions** - Use standard Java naming, structure, and idioms
5. **Explicit Over Implicit** - Code should be clear about what it does

## Technology Constraints

### Allowed Dependencies
- Apache Lucene (9.10.0)
- Apache Tika (2.9.1)
- JavaFX (21.0.2)
- Gson (2.10.1)
- SLF4J + Logback (logging)
- JUnit 5 + Mockito (testing only)

### Prohibited
- ❌ No Spring Framework (even Spring Boot, Spring Data)
- ❌ No Hibernate or ORM frameworks
- ❌ No additional GUI frameworks beyond JavaFX
- ❌ No reactive frameworks (RxJava, Project Reactor)
- ❌ No complex dependency injection unless explicitly needed
- ❌ No Lombok annotations
- ❌ Only add new dependencies if explicitly approved

## Logging Requirements

### Mandatory Logging Setup
1. **Use SLF4J API** - All logging must go through SLF4J, not System.out
2. **Include logback.xml** - Configure Logback in `src/main/resources/logback.xml`
3. **Logger in Every Class** - Each class should have:
   ```java
   private static final Logger logger = LoggerFactory.getLogger(ClassName.class);
   ```
4. **Log Levels**:
   - **DEBUG** - Detailed information for debugging (e.g., index operations, parsed documents)
   - **INFO** - General informational messages (e.g., "Indexing started", "Search completed")
   - **WARN** - Warning messages (e.g., "File could not be parsed", "Index corrupted, rebuilding")
   - **ERROR** - Error messages (e.g., "IOException during indexing", "Lucene error")

5. **What to Log**:
   - Method entry/exit for critical operations
   - File processing events (found, indexed, skipped, failed)
   - Index operations (created, opened, closed, optimized)
   - Search operations (query submitted, results returned, time taken)
   - Configuration loading and errors
   - Warnings for unsupported formats or large files

## Code Style Guidelines

### Class Structure
```java
public class ExampleClass {
    private static final Logger logger = LoggerFactory.getLogger(ExampleClass.class);
    
    // Constants at the top
    private static final String CONSTANT = "value";
    
    // Fields
    private SomeField field;
    
    // Constructor
    public ExampleClass() {
        logger.debug("Initializing ExampleClass");
    }
    
    // Public methods
    public void publicMethod() {
        logger.info("Public method called");
    }
    
    // Private methods
    private void privateMethod() {
    }
}
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `FileIndexer`, `SearchEngine`)
- **Methods/Variables**: camelCase (e.g., `indexFiles()`, `searchResults`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `INDEX_PATH`, `MAX_FILE_SIZE`)
- **Booleans**: Start with `is`, `has`, `can` (e.g., `isIndexed`, `hasResults`)

### Method Guidelines
- Keep methods small and focused (10-20 lines ideally)
- One responsibility per method
- Use descriptive names that explain what the method does
- Include JavaDoc for public methods
- Handle exceptions properly (don't swallow them silently)

## JavaFX Guidelines

### UI Development
1. **Separate Concerns** - Keep UI logic separate from business logic
2. **Use Task/Service** - For long-running operations (indexing, searching) use `javafx.concurrent.Task`
3. **Thread Safety** - Always update UI from JavaFX thread using `Platform.runLater()`
4. **FXML vs Code** - For minimal version, use Java code (not FXML) to keep it simple
5. **Styling** - Use CSS in `src/main/resources/styles.css`, not inline styling
6. **No Complex Layouts** - Start with simple VBox/HBox layouts, add complexity only if needed

### Example Pattern for Background Tasks
```java
Task<SearchResults> searchTask = new Task<SearchResults>() {
    @Override
    protected SearchResults call() throws Exception {
        logger.debug("Starting search task");
        return searchEngine.search(query);
    }
};

searchTask.setOnSucceeded(event -> {
    logger.info("Search completed successfully");
    displayResults(searchTask.getValue());
});

searchTask.setOnFailed(event -> {
    logger.error("Search failed", searchTask.getException());
    showError("Search failed");
});

new Thread(searchTask).start();
```

## Error Handling

### Approach
1. **Catch Specific Exceptions** - Not generic `Exception`
2. **Log the Error** - Always log exceptions with context
3. **Propagate or Handle** - Decide if you should rethrow or recover
4. **User Feedback** - Inform users of errors through UI when appropriate

### Example
```java
try {
    document = parser.parse(file);
    logger.debug("Successfully parsed file: {}", file.getName());
} catch (IOException e) {
    logger.warn("Failed to parse file: {}", file.getName(), e);
    // Handle gracefully, maybe skip this file and continue
} catch (TikaException e) {
    logger.error("Tika parsing error for file: {}", file.getName(), e);
}
```

## Testing Guidelines

### Unit Tests
1. **Test Business Logic Only** - Focus on indexing and search logic, not UI
2. **Use Mockito** - For mocking Tika or Lucene when needed
3. **Test File Names** - `ClassNameTest.java` in `src/test/java`
4. **Minimal Tests for MVP** - Write tests for critical operations only

### Example Test Structure
```java
public class FileIndexerTest {
    private FileIndexer fileIndexer;
    private Path tempIndexDir;
    
    @BeforeEach
    void setUp() throws IOException {
        tempIndexDir = Files.createTempDirectory("lucene-test");
        fileIndexer = new FileIndexer(tempIndexDir.toString());
    }
    
    @Test
    void testIndexFile() throws Exception {
        // Setup
        // Execute
        // Assert
    }
    
    @AfterEach
    void tearDown() throws IOException {
        // Cleanup
    }
}
```

## Configuration Management

### JSON Configuration
1. **Use Gson** for reading/writing JSON config
2. **Store in User Home** - `~/.fileindexer/config.json`
3. **Sensible Defaults** - Provide defaults if config file doesn't exist
4. **Log Configuration Loading** - Always log when config is loaded/saved

### Example Pattern
```java
public class AppConfig {
    private static final Logger logger = LoggerFactory.getLogger(AppConfig.class);
    private static final String CONFIG_PATH = System.getProperty("user.home") + "/.fileindexer/config.json";
    
    public static AppConfig loadConfig() {
        logger.info("Loading configuration from: {}", CONFIG_PATH);
        // Load JSON, handle errors, return config
    }
    
    public void save() {
        logger.info("Saving configuration");
        // Write JSON
    }
}
```

## Performance Considerations

1. **Indexing** - Log time taken for indexing operations
2. **Searching** - Keep search responsive, use background tasks
3. **Memory** - Close resources (IndexWriter, IndexReader, Directory) properly
4. **File Size Limits** - Add a max file size limit to avoid parsing huge files
5. **Progress Feedback** - Show progress when indexing many files

## Security & Safety

1. **Path Validation** - Validate file paths before processing
2. **Resource Cleanup** - Always close streams, readers, writers in finally blocks or try-with-resources
3. **Error Messages** - Don't leak sensitive paths in error messages shown to users
4. **File Permissions** - Handle permission errors gracefully

## Git & Version Control

### Commit Messages
- Use clear, descriptive messages
- Start with action verb: "Add", "Fix", "Refactor", "Update"
- Examples:
  - "Add FileIndexer class with basic indexing"
  - "Fix search query parsing issue"
  - "Update AppConfig to handle missing config file"

### .gitignore Include
```
target/
.idea/
*.iml
.DS_Store
.project
.classpath
.settings/
/.fileindexer/
```

## Documentation

### What to Document
1. **Public Classes** - JavaDoc explaining purpose and usage
2. **Complex Methods** - JavaDoc for non-obvious logic
3. **Config Files** - Comments in JSON explaining options
4. **Configuration Class** - Document all configuration options

### Example JavaDoc
```java
/**
 * Manages the Lucene index for file searching.
 * Handles creation, opening, and maintenance of the index.
 */
public class IndexManager {
    
    /**
     * Creates a new index at the specified location.
     * 
     * @param indexPath the path where the index will be stored
     * @throws IOException if index creation fails
     */
    public void createIndex(String indexPath) throws IOException {
        // Implementation
    }
}
```

## Summary of Do's and Don'ts

### DO ✅
- ✅ Write simple, readable code
- ✅ Use SLF4J for all logging
- ✅ Handle exceptions explicitly
- ✅ Close resources properly (try-with-resources)
- ✅ Use background tasks for UI-blocking operations
- ✅ Test critical business logic
- ✅ Document public APIs
- ✅ Log important events

### DON'T ❌
- ❌ Add frameworks unless explicitly approved
- ❌ Use System.out for logging
- ❌ Ignore exceptions
- ❌ Leak resources
- ❌ Block the JavaFX thread
- ❌ Over-complicate the design
- ❌ Use Lombok or annotation magic
- ❌ Assume files exist or are valid

## Minimal MVP Scope

For the first working version, focus on:
1. ✅ Index a directory of text files
2. ✅ Search indexed files with basic query
3. ✅ Display results in a simple UI
4. ✅ Save/load configuration
5. ✅ Proper logging throughout

**Don't include yet:**
- ❌ File watcher for auto-indexing
- ❌ Advanced search features
- ❌ OCR for images
- ❌ Complex UI features
- ❌ Performance optimizations

## Questions for the AI Agent

Before implementing a feature, ask:
1. Is this needed for the minimal working version?
2. Can it be done with existing dependencies?
3. Is the simplest approach good enough?
4. Have I logged the important operations?
5. Are resources properly cleaned up?
6. Will this be understandable to another developer?