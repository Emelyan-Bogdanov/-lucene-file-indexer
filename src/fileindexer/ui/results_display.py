import tkinter as tk
from tkinter import ttk
from datetime import datetime


class ResultsDisplay(ttk.PanedWindow):
    def __init__(self, parent, on_open_file, **kwargs):
        super().__init__(parent, orient=tk.VERTICAL, **kwargs)
        self.on_open_file = on_open_file
        self._build_ui()

    def _build_ui(self):
        top_frame = ttk.Frame(self)
        self.add(top_frame, weight=2)

        columns = ("score", "filename", "path", "type", "size", "modified")
        self.tree = ttk.Treeview(
            top_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("score", text="Score")
        self.tree.heading("filename", text="Name")
        self.tree.heading("path", text="Path")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        self.tree.heading("modified", text="Modified")

        self.tree.column("score", width=70, anchor="e")
        self.tree.column("filename", width=200)
        self.tree.column("path", width=350)
        self.tree.column("type", width=60)
        self.tree.column("size", width=80, anchor="e")
        self.tree.column("modified", width=150)

        vsb = ttk.Scrollbar(top_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        top_frame.columnconfigure(0, weight=1)
        top_frame.rowconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._on_open())

        bottom_frame = ttk.Frame(self)
        self.add(bottom_frame, weight=1)

        preview_label = ttk.Label(bottom_frame, text="Preview:", font=("", 10, "bold"))
        preview_label.pack(anchor="w", padx=4, pady=(4, 0))

        preview_container = ttk.Frame(bottom_frame)
        preview_container.pack(fill="both", expand=True, padx=4, pady=4)
        preview_container.columnconfigure(0, weight=1)
        preview_container.rowconfigure(0, weight=1)

        self.preview_text = tk.Text(
            preview_container,
            wrap="word",
            font=("Segoe UI", 10),
            state="disabled",
            relief="sunken",
            borderwidth=2,
        )
        self.preview_text.grid(row=0, column=0, sticky="nsew")

        preview_scroll = ttk.Scrollbar(
            preview_container, orient="vertical", command=self.preview_text.yview
        )
        self.preview_text.configure(yscrollcommand=preview_scroll.set)
        preview_scroll.grid(row=0, column=1, sticky="ns")

        self.preview_text.tag_config("highlight", background="yellow", foreground="black")

        self._results = []

    def display_results(self, results):
        self._results = results
        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in results:
            size_str = self._format_size(r.document.size)
            mod_str = self._format_timestamp(r.document.last_modified)
            self.tree.insert(
                "",
                "end",
                values=(
                    f"{r.score:.2f}",
                    r.document.filename,
                    r.document.path,
                    r.document.extension or "(folder)",
                    size_str,
                    mod_str,
                ),
            )

        if results:
            self.tree.selection_set(self.tree.get_children()[0])

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel or not self._results:
            return
        idx = self.tree.index(sel[0])
        if idx >= len(self._results):
            return
        result = self._results[idx]
        self._show_preview(result)

    def _show_preview(self, result):
        doc = result.document
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", "end")

        header = f"File: {doc.filename}\nPath: {doc.path}\n"
        header += f"Size: {self._format_size(doc.size)}  |  "
        header += f"Modified: {self._format_timestamp(doc.last_modified)}\n"
        header += f"Score: {result.score:.2f}\n"
        header += "-" * 80 + "\n"

        self.preview_text.insert("end", header)

        if result.snippets:
            self.preview_text.insert("end", "\nMatching snippets:\n", "highlight")
            for i, snip in enumerate(result.snippets, 1):
                self._insert_snippet(snip)

            self.preview_text.insert("end", "\n\nFull content preview (first 3000 chars):\n\n")

        content_preview = doc.content[:3000] if doc.content else "(no content extracted)"
        self.preview_text.insert("end", content_preview)

        self.preview_text.config(state="disabled")

    def _insert_snippet(self, snippet):
        import re
        parts = re.split(r"(<mark>|</mark>)", snippet)
        for part in parts:
            if part == "<mark>":
                self.preview_text.insert("end", "", "")
                self.preview_text.mark_set("mark_start", "end-1c")
                continue
            elif part == "</mark>":
                try:
                    start = self.preview_text.index("mark_start")
                    end = self.preview_text.index("end-1c")
                    self.preview_text.tag_add("highlight", start, end)
                except Exception:
                    pass
                continue
            self.preview_text.insert("end", part)

    def _on_open(self):
        sel = self.tree.selection()
        if sel and self._results:
            idx = self.tree.index(sel[0])
            if idx < len(self._results):
                self.on_open_file(self._results[idx].document.path)

    @staticmethod
    def _format_size(size):
        try:
            s = int(size)
            for unit in ("B", "KB", "MB", "GB"):
                if s < 1024:
                    return f"{s:.1f} {unit}"
                s /= 1024
            return f"{s:.1f} TB"
        except (ValueError, TypeError):
            return "0 B"

    @staticmethod
    def _format_timestamp(ts_ms):
        try:
            return datetime.fromtimestamp(int(ts_ms) / 1000).strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError):
            return "unknown"
