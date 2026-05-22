from dataclasses import dataclass, field
from typing import List


@dataclass
class IndexedDocument:
    path: str
    filename: str
    extension: str
    size: int
    last_modified: int
    content: str = ""


@dataclass
class SearchResult:
    document: IndexedDocument
    score: float
    snippets: List[str] = field(default_factory=list)
