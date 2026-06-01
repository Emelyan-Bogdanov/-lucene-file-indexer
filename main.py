import argparse
import sys

from cli.commands import (
    cmd_index, cmd_search, cmd_info, cmd_clean, cmd_watch,
    cmd_config, cmd_open, cmd_preview, cmd_history,
    cmd_save_search, cmd_list_saved, cmd_delete_saved,
    cmd_export, cmd_faceted, cmd_autocomplete, cmd_reindex,
)


def main():
    parser = argparse.ArgumentParser(
        description="Lucene-style File Indexer - Full-text search engine for your files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s index --dirs ~/Documents ~/Downloads
  %(prog)s search "machine learning" --ext pdf
  %(prog)s search "hello~2" --fuzzy
  %(prog)s search "doc*" --wildcard
  %(prog)s search '"exact phrase"'
  %(prog)s search "python AND (django OR flask) NOT java"
  %(prog)s search "regex:\\\\d{4}-\\\\d{2}-\\\\d{2}"
  %(prog)s info
  %(prog)s watch --dirs ~/Documents
  %(prog)s preview ~/file.py
  %(prog)s history
  %(prog)s export "python" --format json --output results.json
  %(prog)s faceted --field extension
        """,
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    p_index = subparsers.add_parser("index", help="Index files from directories")
    p_index.add_argument("--dirs", nargs="+", help="Directories to scan")

    p_search = subparsers.add_parser("search", help="Search indexed files")
    p_search.add_argument("query", help="Search query (supports fuzzy~, wildcard*, regex, phrases, AND/OR/NOT)")
    p_search.add_argument("--ext", nargs="+", help="Filter by extension(s)")
    p_search.add_argument("--folder", help="Filter by folder")
    p_search.add_argument("--type", help="Filter by MIME type")
    p_search.add_argument("--sort", nargs="+", help="Sort fields (relevance, date, size, filename; prefix with - for desc)")
    p_search.add_argument("--page", type=int, default=1, help="Page number")
    p_search.add_argument("--per-page", type=int, help="Results per page")
    p_search.add_argument("--show-preview", action="store_true", help="Show file previews")

    p_info = subparsers.add_parser("info", help="Show index statistics")

    p_clean = subparsers.add_parser("clean", help="Remove deleted files from index")
    p_clean.add_argument("--dirs", nargs="+", help="Scan directories to check against")

    p_watch = subparsers.add_parser("watch", help="Watch directories and auto-update index")
    p_watch.add_argument("--dirs", nargs="+", help="Directories to watch")
    p_watch.add_argument("--interval", type=float, default=5.0, help="Poll interval in seconds")

    p_reindex = subparsers.add_parser("reindex", help="Re-index only changed files")
    p_reindex.add_argument("--dirs", nargs="+", help="Directories to scan")

    p_config = subparsers.add_parser("config", help="View or set configuration")
    p_config.add_argument("--show", action="store_true", help="Show current config")
    p_config.add_argument("--set", nargs="+", help="Set config values (key=value)")

    p_open = subparsers.add_parser("open", help="Open a file with system default application")
    p_open.add_argument("filepath", help="Path to file")

    p_preview = subparsers.add_parser("preview", help="Preview file contents in terminal")
    p_preview.add_argument("filepath", help="Path to file")
    p_preview.add_argument("--lines", type=int, default=30, help="Number of lines to show")

    p_history = subparsers.add_parser("history", help="Show search history")
    p_history.add_argument("--limit", type=int, default=20, help="Max entries")

    p_save = subparsers.add_parser("save-search", help="Save a search query")
    p_save.add_argument("name", help="Name for the saved search")
    p_save.add_argument("query", help="Search query")

    p_saved = subparsers.add_parser("saved-searches", help="List saved searches")

    p_delete = subparsers.add_parser("delete-saved", help="Delete a saved search")
    p_delete.add_argument("name", help="Name of saved search to delete")

    p_export = subparsers.add_parser("export", help="Export search results")
    p_export.add_argument("query", help="Search query")
    p_export.add_argument("--output", default="results.csv", help="Output file path")
    p_export.add_argument("--format", choices=["csv", "json"], default="csv", help="Export format")
    p_export.add_argument("--ext", nargs="+", help="Filter by extension(s)")
    p_export.add_argument("--folder", help="Filter by folder")

    p_faceted = subparsers.add_parser("faceted", help="Faceted search statistics")
    p_faceted.add_argument("--field", choices=["extension", "mime_type", "folder"], default="extension")
    p_faceted.add_argument("--top", type=int, default=20, help="Number of top values")

    p_ac = subparsers.add_parser("autocomplete", help="Get autocomplete suggestions")
    p_ac.add_argument("prefix", help="Prefix to complete")
    p_ac.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "index": cmd_index,
        "search": cmd_search,
        "info": cmd_info,
        "clean": cmd_clean,
        "watch": cmd_watch,
        "reindex": cmd_reindex,
        "config": cmd_config,
        "open": cmd_open,
        "preview": cmd_preview,
        "history": cmd_history,
        "save-search": cmd_save_search,
        "saved-searches": cmd_list_saved,
        "delete-saved": cmd_delete_saved,
        "export": cmd_export,
        "faceted": cmd_faceted,
        "autocomplete": cmd_autocomplete,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
