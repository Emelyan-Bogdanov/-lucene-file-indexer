"""Lucene File Indexer — fast desktop file search with PyLucene and Tika."""

import lucene

__version__ = "1.0.0"


def init_jvm():
    if not lucene.getVMEnv():
        lucene.initVM()
