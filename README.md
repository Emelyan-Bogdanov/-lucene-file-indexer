# Lucene File Indexer

A fast desktop file search application that indexes and searches your files instantly using **PyLucene** and **Apache Tika** for full-text indexing across 100+ file formats.

## Features

- ⚡ **Fast Full-Text Search** — Powered by Apache Lucene via PyLucene
- 📄 **Multi-Format Support** — PDFs, Word, Excel, PowerPoint, Images, and 100+ more (via Tika)
- 🖥️ **Desktop GUI** — Built with Python tkinter (no extra GUI framework needed)
- ⚙️ **Configurable** — JSON-based configuration in `~/.fileindexer/config.json`
- 🔄 **Index Management** — Create, rebuild, and inspect your search index
- 🎯 **Relevance Ranking** — Results sorted by Lucene relevance score
- 📊 **Search Snippets** — Context preview with highlighted matches

## Prerequisites

| Dependency | Version |
|-----------|---------|
| Python | 3.10+ |
| Java JDK | 11+ (for Tika & PyLucene) |
| PyLucene | 9.x |
| Apache Tika | 2.x (auto‑managed via tika-python) |

> **Note:** Apache Tika requires Java. The `tika-python` library starts a Tika REST server in the background on first use.

## Installation

### 1. Install Java

Download and install Java JDK 11 or later from [adoptium.net](https://adoptium.net/) and ensure `java` is on your PATH.

```bash
java -version
```

### 2. Install PyLucene

**Windows:**
```bash
pip install pylucene
```

**Linux / macOS:**
See the [PyLucene installation guide](https://lucene.apache.org/pylucene/install.html). You may need to build from source on some platforms. Conda users can try:
```bash
conda install -c conda-forge pylucene
```

### 3. Install the application

```bash
# Clone the repo
git clone https://github.com/yourusername/lucene-file-indexer.git
cd lucene-file-indexer

# Install the package and dependencies
pip install -e .
```

## Usage

```bash
# Run the GUI application
python -m fileindexer
```

Or after installing:
```bash
file-indexer
```

### First-time setup

1. Launch the application
2. Click **File → Add Directory** to add folders you want to index
3. Click **Start Indexing** to build the search index
4. Type a query in the search bar and press **Enter** or click **Search**

### Configuration

Configuration is stored in `~/.fileindexer/config.json`:

```json
{
  "indexed_directories": ["C:/Users/me/Documents", "C:/Users/me/Downloads"],
  "index_path": "C:/Users/me/.fileindexer/index",
  "auto_index": true,
  "max_file_size_mb": 100,
  "exclude_patterns": ["*.tmp", "*.log", "*.bak", "*~"],
  "exclude_dirs": ["__pycache__", ".git", ".svn", "node_modules"]
}
```

## Project Structure

```
lucene-file-indexer/
├── src/fileindexer/
│   ├── __init__.py          # JVM initialisation
│   ├── __main__.py          # `python -m fileindexer` entry point
│   ├── app.py               # Application entry point & AppContext
│   ├── config.py            # JSON-based configuration
│   ├── models.py            # SearchResult & IndexedDocument
│   ├── parser.py            # Apache Tika document parsing
│   ├── indexer.py           # IndexManager & FileIndexer
│   ├── search_engine.py     # Lucene query execution & highlighting
│   └── ui/
│       ├── main_window.py   # Main tkinter window & menus
│       ├── search_controller.py  # Search bar & indexing controls
│       └── results_display.py    # Results table & preview pane
├── tests/
│   ├── test_indexer.py
│   └── test_search_engine.py
├── requirements.txt
├── setup.py
└── README.md
```

## Running Tests

```bash
pip install pytest
pytest tests/
```

## License

MIT
