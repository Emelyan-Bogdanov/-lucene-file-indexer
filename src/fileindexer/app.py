"""Application entry point."""

import sys

from fileindexer import init_jvm
from fileindexer.config import AppConfig
from fileindexer.parser import DocumentParser
from fileindexer.indexer import IndexManager, FileIndexer
from fileindexer.search_engine import SearchEngine
from fileindexer.ui.main_window import MainWindow


class AppContext:
    def __init__(self, config_path=None):
        init_jvm()
        self.config = AppConfig(config_path)
        self.parser = DocumentParser()
        self.index_manager = IndexManager(str(self.config.index_path))
        self.file_indexer = FileIndexer(self.index_manager, self.parser, self.config)
        self.search_engine = SearchEngine(self.index_manager)


def main():
    context = AppContext()
    window = MainWindow(context)
    window.run()


if __name__ == "__main__":
    main()
