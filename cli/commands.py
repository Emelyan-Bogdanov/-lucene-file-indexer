import argparse
import os
import sys
import subprocess
import webbrowser

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.text import Text

from indexer.engine import FileIndexer
from indexer.document_parser import extract_text
from indexer.watcher import FileWatcher
from search.query import QueryEngine
from search.suggest import Suggester
from utils.config import load_config, save_config
from utils.history import (
    add_to_history, load_search_history, load_saved_searches,
    save_search, delete_saved_search,
)

console = Console(legacy_windows=True)
config = load_config()


def cmd_index(args):
    scan_dirs = args.dirs or config.get("scan_dirs", [])
    if not scan_dirs:
        console.print("[red]No directories specified. Use --dirs or set scan_dirs in config.[/red]")
        return

    indexer = FileIndexer(config["index_dir"], config)
    total = len(scan_dirs)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Indexing files...", total=total)
        for sd in scan_dirs:
            if os.path.isdir(sd):
                result = indexer.scan_directory(sd, parallel=config.get("parallel_indexing", True))
                console.print(f"  [green]+[/green] {sd}: {result['indexed']} indexed, {result['skipped']} skipped, {result['errors']} errors")
            else:
                console.print(f"  [yellow]![/yellow] {sd}: directory not found")
            progress.advance(task)

    stats = indexer.index_stats()
    console.print(f"\n[bold green]Index complete![/bold green]")
    console.print(f"  Total documents: {stats['total_docs']}")
    console.print(f"  Index size: {stats['index_size_mb']} MB")
    indexer.close()


def cmd_search(args):
    if not args.query:
        console.print("[red]Query required.[/red]")
        return

    indexer = FileIndexer(config["index_dir"], config)
    qe = QueryEngine(indexer.ix)

    filters = {}
    if args.ext:
        filters["extension"] = [e if e.startswith(".") else f".{e}" for e in args.ext]
    if args.folder:
        filters["folder"] = args.folder
    if args.type:
        filters["mime_type"] = args.type

    sort_by = args.sort if args.sort else None

    page = args.page or 1
    per_page = args.per_page or config.get("results_per_page", 20)

    results, total, raw_results = qe.search(args.query, filters=filters, sort_by=sort_by, page=page, per_page=per_page)

    add_to_history(args.query)

    if not results:
        suggester = Suggester(indexer.ix)
        suggestions = suggester.suggest(args.query)
        console.print("[yellow]No results found.[/yellow]")
        if suggestions:
            console.print(f"Did you mean: {', '.join(suggestions[:5])}?")
        indexer.close()
        return

    table = Table(title=f"Search Results for '{args.query}' ({total} total)")
    table.add_column("#", style="dim", width=4)
    table.add_column("Filename", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Size", justify="right")
    table.add_column("Modified")
    table.add_column("Score", justify="right")

    for i, r in enumerate(results, 1):
        size_str = format_size(r["size"])
        mod_str = r["modified"][:10] if r["modified"] else ""
        table.add_row(
            str((page - 1) * per_page + i),
            r["filename"],
            r["folder"],
            size_str,
            mod_str,
            f"{r['score']:.2f}",
        )

    console.print(table)

    if args.show_preview and results:
        for r in results:
            text = extract_text(r["path"])
            preview = text[:500] + "..." if len(text) > 500 else text
            console.print(Panel(preview, title=f"Preview: {r['filename']}"))

    indexer.close()


def cmd_info(args):
    indexer = FileIndexer(config["index_dir"], config)
    stats = indexer.index_stats()

    reader = indexer.ix.reader()
    field_names = list(reader.schema._fields.keys())

    console.print(f"[bold]Index Statistics[/bold]")
    console.print(f"  Index directory: {config['index_dir']}")
    console.print(f"  Total documents: {stats['total_docs']}")
    console.print(f"  Index size: {stats['index_size_mb']} MB")
    console.print(f"  Fields: {', '.join(field_names)}")

    ext_counts = {}
    for stored in reader.all_stored_fields():
        ext = stored.get("extension", "")
        ext_counts[ext] = ext_counts.get(ext, 0) + 1

    if ext_counts:
        console.print(f"\n[bold]Documents by type:[/bold]")
        for ext, count in sorted(ext_counts.items(), key=lambda x: -x[1]):
            console.print(f"  {ext or '(unknown)'}: {count}")

    indexer.close()


def cmd_clean(args):
    indexer = FileIndexer(config["index_dir"], config)
    scan_dirs = args.dirs or config.get("scan_dirs", [])
    if not scan_dirs:
        console.print("[yellow]No scan directories configured. Specify with --dirs[/yellow]")
        return

    removed = indexer.cleanup_removed_files(scan_dirs)
    console.print(f"[green]Removed {removed} stale entries from index.[/green]")
    indexer.close()


def cmd_watch(args):
    scan_dirs = args.dirs or config.get("scan_dirs", [])
    if not scan_dirs:
        console.print("[red]No directories to watch.[/red]")
        return

    indexer = FileIndexer(config["index_dir"], config)
    watcher = FileWatcher(indexer, scan_dirs, interval=args.interval or 5)

    console.print(f"[green]Watching {len(scan_dirs)} directories for changes...[/green]")
    console.print("Press Ctrl+C to stop.")
    watcher.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping watcher...[/yellow]")
        watcher.stop()
        indexer.close()
        console.print("[green]Watcher stopped.[/green]")


def cmd_config(args):
    global config
    if args.show:
        console.print("[bold]Current Configuration:[/bold]")
        for key, value in config.items():
            console.print(f"  {key}: {value}")
        return

    if args.set:
        for kv in args.set:
            if "=" not in kv:
                console.print(f"[red]Invalid format: {kv}. Use key=value[/red]")
                continue
            key, value = kv.split("=", 1)
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            try:
                config[key] = value
            except Exception as e:
                console.print(f"[red]Error setting {key}: {e}[/red]")
        save_config(config)
        console.print("[green]Configuration saved.[/green]")


def cmd_open(args):
    filepath = args.filepath
    if not os.path.exists(filepath):
        console.print(f"[red]File not found: {filepath}[/red]")
        return
    try:
        if sys.platform == "win32":
            os.startfile(filepath)
        elif sys.platform == "darwin":
            subprocess.run(["open", filepath])
        else:
            subprocess.run(["xdg-open", filepath])
    except Exception as e:
        console.print(f"[red]Cannot open file: {e}[/red]")


def cmd_preview(args):
    if not os.path.isfile(args.filepath):
        console.print(f"[red]File not found: {args.filepath}[/red]")
        return
    text = extract_text(args.filepath)
    if not text:
        console.print("[yellow]No text content could be extracted.[/yellow]")
        return

    preview = text[:args.lines * 80] if args.lines else text[:2000]
    ext = os.path.splitext(args.filepath)[1].lower()

    if ext in (".py", ".js", ".ts", ".java", ".c", ".cpp", ".rs", ".go"):
        syntax = Syntax(preview, ext.lstrip("."), theme="monokai", line_numbers=True)
        console.print(syntax)
    else:
        console.print(Panel(preview, title=f"Preview: {os.path.basename(args.filepath)}"))


def cmd_history(args):
    history = load_search_history()
    if not history:
        console.print("[yellow]No search history.[/yellow]")
        return
    table = Table(title="Recent Searches")
    table.add_column("#", style="dim", width=4)
    table.add_column("Query", style="cyan")
    table.add_column("Timestamp")
    for i, entry in enumerate(history[:args.limit], 1):
        table.add_row(str(i), entry["query"], entry["timestamp"][:19])
    console.print(table)


def cmd_save_search(args):
    save_search(args.name, args.query)
    console.print(f"[green]Search saved as '{args.name}'.[/green]")


def cmd_list_saved(args):
    saved = load_saved_searches()
    if not saved:
        console.print("[yellow]No saved searches.[/yellow]")
        return
    table = Table(title="Saved Searches")
    table.add_column("Name", style="cyan")
    table.add_column("Query")
    table.add_column("Saved")
    for name, data in saved.items():
        table.add_row(name, data["query"], data["timestamp"][:19])
    console.print(table)


def cmd_delete_saved(args):
    delete_saved_search(args.name)
    console.print(f"[green]Deleted saved search '{args.name}'.[/green]")


def cmd_export(args):
    indexer = FileIndexer(config["index_dir"], config)
    qe = QueryEngine(indexer.ix)

    filters = {}
    if args.ext:
        filters["extension"] = [e if e.startswith(".") else f".{e}" for e in args.ext]
    if args.folder:
        filters["folder"] = args.folder

    results, total, _ = qe.search(args.query, filters=filters)
    fmt = args.format or "csv"

    if fmt == "csv":
        import csv
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["filename", "path", "extension", "size", "modified", "score"])
            writer.writeheader()
            for r in results:
                writer.writerow({
                    "filename": r["filename"],
                    "path": r["path"],
                    "extension": r["extension"],
                    "size": r["size"],
                    "modified": r["modified"],
                    "score": r["score"],
                })
    elif fmt == "json":
        import json
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    console.print(f"[green]Exported {len(results)} results to {args.output}[/green]")
    indexer.close()


def cmd_faceted(args):
    indexer = FileIndexer(config["index_dir"], config)
    reader = indexer.ix.reader()

    if args.field == "extension":
        counts = {}
        for stored in reader.all_stored_fields():
            ext = stored.get("extension", "(unknown)")
            counts[ext] = counts.get(ext, 0) + 1
    elif args.field == "mime_type":
        counts = {}
        for stored in reader.all_stored_fields():
            mt = stored.get("mime_type", "unknown")
            counts[mt] = counts.get(mt, 0) + 1
    elif args.field == "folder":
        counts = {}
        for stored in reader.all_stored_fields():
            folder = stored.get("folder", "/")
            counts[folder] = counts.get(folder, 0) + 1
    else:
        console.print(f"[red]Unknown facet field: {args.field}[/red]")
        indexer.close()
        return

    table = Table(title=f"Faceted by {args.field}")
    table.add_column("Value", style="cyan")
    table.add_column("Count", justify="right")
    for value, count in sorted(counts.items(), key=lambda x: -x[1])[:args.top]:
        table.add_row(str(value), str(count))
    console.print(table)
    indexer.close()


def cmd_autocomplete(args):
    indexer = FileIndexer(config["index_dir"], config)
    qe = QueryEngine(indexer.ix)
    suggestions = qe.get_suggestions(args.prefix, limit=args.limit or 10)
    if suggestions:
        console.print("Suggestions:")
        for s in suggestions:
            console.print(f"  [cyan]{s}[/cyan]")
    else:
        console.print("[yellow]No suggestions.[/yellow]")
    indexer.close()


def cmd_reindex(args):
    indexer = FileIndexer(config["index_dir"], config)

    if not args.dirs and not config.get("scan_dirs"):
        console.print("[red]No directories specified.[/red]")
        indexer.close()
        return

    scan_dirs = args.dirs or config["scan_dirs"]
    reader = indexer.ix.reader()
    indexed_paths = {}
    for stored in reader.all_stored_fields():
        indexed_paths[stored["path"]] = stored.get("modified", "")

    changed = []
    for sd in scan_dirs:
        for root, _, files in os.walk(sd):
            for f in files:
                fpath = os.path.join(root, f)
                if fpath in indexed_paths:
                    try:
                        current_mtime = str(os.path.getmtime(fpath))
                        if current_mtime != indexed_paths[fpath]:
                            changed.append(fpath)
                    except OSError:
                        pass

    if not changed:
        console.print("[green]All files up to date.[/green]")
        indexer.close()
        return

    with Progress(console=console) as progress:
        task = progress.add_task(f"[cyan]Re-indexing {len(changed)} changed files...", total=len(changed))
        for fpath in changed:
            indexer.index_file(fpath)
            progress.advance(task)

    console.print(f"[green]Re-indexed {len(changed)} files.[/green]")
    indexer.close()


def format_size(size):
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


import time
