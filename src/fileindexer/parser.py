from pathlib import Path

from tika import parser as tika_parser


class DocumentParser:
    """Parse documents using Apache Tika."""

    def extract_text(self, file_path: str) -> str:
        try:
            parsed = tika_parser.from_file(file_path)
            content = parsed.get("content", "") or ""
            return content.strip()
        except Exception:
            return ""

    def extract_metadata(self, file_path: str) -> dict:
        try:
            parsed = tika_parser.from_file(file_path)
            return parsed.get("metadata", {}) or {}
        except Exception:
            return {}
