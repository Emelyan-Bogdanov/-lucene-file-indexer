import csv
import os
import threading

import customtkinter as ctk
from CTkTable import CTkTable

from indexer.engine import FileIndexer
from indexer.document_parser import extract_text
from search.query import QueryEngine
from search.highlighter import highlight_text
from utils.history import add_to_history, save_search


class SearchTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.indexer = None
        self.qe = None
        self.current_results = []
        self.current_query = ""
        self.current_page = 1
        self.per_page = config.get("results_per_page", 20)
        self.preview_visible = True
        self._open_indexer()

    def _open_indexer(self):
        try:
            if self.indexer:
                self.indexer.close()
            self.indexer = FileIndexer(self.config["index_dir"], self.config)
            self.qe = QueryEngine(self.indexer.ix)
        except Exception:
            self.indexer = None
            self.qe = None

    def build(self, tab):
        self.tab = tab
        self._build_search_bar(tab)
        self._build_filters(tab)
        self._build_results(tab)
        self._build_preview(tab)
        self._build_status(tab)
        self._bind_global_hotkeys()

    def _bind_global_hotkeys(self):
        root = self.tab.winfo_toplevel()
        root.bind("<Control-Return>", lambda e: self._do_search())
        root.bind("<Control-e>", lambda e: self._export_csv())

    def _build_search_bar(self, tab):
        top = ctk.CTkFrame(tab)
        top.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(top, text="Search:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            top, textvariable=self.search_var,
            placeholder_text='Search...  (fuzzy~ wildcard* AND/OR/NOT "phrase" regex:)',
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<Return>", lambda e: self._do_search())
        self.search_entry.bind("<KeyRelease>", self._on_key_release)

        self.search_btn = ctk.CTkButton(top, text="Search", width=90, command=self._do_search)
        self.search_btn.pack(side="left", padx=(5, 2))

        self.clear_btn = ctk.CTkButton(
            top, text="Clear", width=60,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray20"),
            command=self._clear_search,
        )
        self.clear_btn.pack(side="left", padx=2)

        self.suggest_dropdown = None

    def _clear_search(self):
        self.search_var.set("")
        self.ext_var.set("")
        self.folder_var.set("")
        self.sort_var.set("relevance")
        self.current_results = []
        self.current_page = 1
        header = [["Filename", "Extension", "Size", "Modified", "Path", "Score"]]
        self.result_table.destroy()
        self.result_table = CTkTable(
            self.result_scroll,
            row=1, column=6, values=header,
            header_color=("gray75", "gray25"),
            hover_color=("gray85", "gray30"),
            font=("", 11), wraplength=300,
            padx=4, pady=2, corner_radius=4,
        )
        self.result_table.pack(fill="x", padx=5, pady=3)
        self.result_table.bind("<ButtonRelease-1>", self._on_result_click)
        self.result_table.bind("<Double-1>", self._on_result_double_click)
        self.page_label.configure(text="Page 1")
        self.total_label.configure(text="")
        self.prev_btn.configure(state="disabled")
        self.next_btn.configure(state="disabled")
        self.status_bar.configure(text="Ready")
        self._hide_preview()
        self.search_entry.focus()

    def _on_key_release(self, event):
        text = self.search_var.get()
        if event.keysym in ("Up", "Down", "Left", "Right", "Return", "Escape"):
            return
        if len(text) >= 2 and self.qe:
            def fetch():
                try:
                    suggestions = self.qe.get_suggestions(text, limit=10)
                    if suggestions:
                        self.tab.after(0, lambda: self._show_suggestions(suggestions))
                    else:
                        self.tab.after(0, self._hide_suggestions)
                except Exception:
                    self.tab.after(0, self._hide_suggestions)
            threading.Thread(target=fetch, daemon=True).start()
        else:
            self._hide_suggestions()

    def _show_suggestions(self, suggestions):
        self._hide_suggestions()
        toplevel = self.search_entry.winfo_toplevel()
        self.suggest_dropdown = ctk.CTkFrame(toplevel, corner_radius=6, border_width=1, width=self.search_entry.winfo_width())
        x = self.search_entry.winfo_rootx()
        y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height()
        self.suggest_dropdown.place(x=x, y=y)

        canvas = ctk.CTkScrollableFrame(self.suggest_dropdown, fg_color="transparent", height=min(len(suggestions) * 32, 200))
        canvas.pack(fill="both", expand=True)

        for s in suggestions:
            btn = ctk.CTkButton(
                canvas, text=s, anchor="w", height=28,
                fg_color="transparent", hover_color=("gray85", "gray25"),
                command=lambda v=s: self._select_suggestion(v),
            )
            btn.pack(fill="x")

    def _hide_suggestions(self):
        if self.suggest_dropdown:
            self.suggest_dropdown.destroy()
            self.suggest_dropdown = None

    def _select_suggestion(self, value):
        self.search_var.set(value)
        self._hide_suggestions()
        self.search_entry.focus()
        self._do_search()

    def _build_filters(self, tab):
        filter_frame = ctk.CTkFrame(tab, height=36)
        filter_frame.pack(fill="x", padx=10, pady=3)
        filter_frame.pack_propagate(False)

        ctk.CTkLabel(filter_frame, text="Ext:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(5, 2))
        self.ext_var = ctk.StringVar()
        ext_entry = ctk.CTkEntry(filter_frame, textvariable=self.ext_var, placeholder_text=".pdf,.docx", width=120)
        ext_entry.pack(side="left", padx=3)

        ctk.CTkLabel(filter_frame, text="Folder:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(5, 2))
        self.folder_var = ctk.StringVar()
        folder_entry = ctk.CTkEntry(filter_frame, textvariable=self.folder_var, placeholder_text="subfolder", width=160)
        folder_entry.pack(side="left", padx=3)

        ctk.CTkLabel(filter_frame, text="Sort:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(5, 2))
        self.sort_var = ctk.StringVar(value="relevance")
        sort_menu = ctk.CTkOptionMenu(
            filter_frame, variable=self.sort_var,
            values=["relevance", "date", "size", "filename", "-date", "-size"],
            width=100,
        )
        sort_menu.pack(side="left", padx=3)

        ctk.CTkButton(filter_frame, text="Apply", width=60, command=self._do_search).pack(side="left", padx=3)

    def _build_results(self, tab):
        result_frame = ctk.CTkFrame(tab)
        result_frame.pack(fill="both", expand=True, padx=10, pady=3)

        self.result_scroll = ctk.CTkScrollableFrame(result_frame)
        self.result_scroll.pack(fill="both", expand=True, padx=0, pady=0)

        self.result_table = CTkTable(
            self.result_scroll,
            row=1,
            column=6,
            values=[["Filename", "Extension", "Size", "Modified", "Path", "Score"]],
            header_color=("gray75", "gray25"),
            hover_color=("gray85", "gray30"),
            font=("", 11),
            wraplength=300,
            padx=4,
            pady=2,
            corner_radius=4,
        )
        self.result_table.pack(fill="x", padx=5, pady=3)
        self.result_table.bind("<ButtonRelease-1>", self._on_result_click)
        self.result_table.bind("<Double-1>", self._on_result_double_click)

        nav_frame = ctk.CTkFrame(result_frame, height=36)
        nav_frame.pack(fill="x", pady=(0, 3))
        nav_frame.pack_propagate(False)

        self.prev_btn = ctk.CTkButton(nav_frame, text="< Prev", width=70, command=self._prev_page, state="disabled")
        self.prev_btn.pack(side="left", padx=5)

        self.page_label = ctk.CTkLabel(nav_frame, text="Page 1", font=ctk.CTkFont(size=12))
        self.page_label.pack(side="left", padx=5)

        self.next_btn = ctk.CTkButton(nav_frame, text="Next >", width=70, command=self._next_page, state="disabled")
        self.next_btn.pack(side="left", padx=5)

        self.total_label = ctk.CTkLabel(nav_frame, text="", font=ctk.CTkFont(size=11, weight="bold"))
        self.total_label.pack(side="left", padx=10)

        ctk.CTkButton(nav_frame, text="Save Search", width=90, command=self._save_search).pack(side="right", padx=5)
        self.export_btn = ctk.CTkButton(nav_frame, text="Export CSV", width=90, command=self._export_csv)
        self.export_btn.pack(side="right", padx=5)

        self.preview_toggle_btn = ctk.CTkButton(
            nav_frame, text="Hide Preview" if self.preview_visible else "Show Preview",
            width=100, command=self._toggle_preview,
        )
        self.preview_toggle_btn.pack(side="right", padx=5)

    def _build_preview(self, tab):
        self.preview_frame = ctk.CTkFrame(tab, height=180)
        self.preview_frame.pack(fill="x", padx=10, pady=(0, 3))
        self.preview_frame.pack_propagate(False)

        header = ctk.CTkFrame(self.preview_frame, height=28)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Preview", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5)
        self.preview_filename = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=10))
        self.preview_filename.pack(side="left", padx=10)
        ctk.CTkButton(header, text="Show in Folder", width=100, command=self._reveal_selected_in_folder).pack(side="right", padx=5)

        self.preview_text = ctk.CTkTextbox(self.preview_frame, wrap="word", font=ctk.CTkFont(size=11))
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=3)
        self.preview_text.configure(state="disabled")

    def _toggle_preview(self):
        self.preview_visible = not self.preview_visible
        if self.preview_visible:
            self.preview_frame.pack(fill="x", padx=10, pady=(0, 3))
            self.preview_toggle_btn.configure(text="Hide Preview")
        else:
            self.preview_frame.pack_forget()
            self.preview_toggle_btn.configure(text="Show Preview")

    def _hide_preview(self):
        self.preview_filename.configure(text="")
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.configure(state="disabled")

    def _build_status(self, tab):
        self.status_bar = ctk.CTkLabel(tab, text="Ready", anchor="w", font=ctk.CTkFont(size=11))
        self.status_bar.pack(fill="x", padx=10, pady=(0, 5))

    def _do_search(self):
        query = self.search_var.get().strip()
        if not query:
            return
        self.current_page = 1
        self._execute_search()

    def _execute_search(self):
        query = self.search_var.get().strip()
        if not query:
            return

        self._open_indexer()
        if not self.qe:
            self.status_bar.configure(text="Index not found. Go to Index tab first.")
            return

        self.status_bar.configure(text="Searching...")
        self.search_btn.configure(state="disabled")

        def search_thread():
            try:
                filters = {}
                ext = self.ext_var.get().strip()
                if ext:
                    filters["extension"] = [e.strip() if e.startswith(".") else f".{e.strip()}" for e in ext.split(",") if e.strip()]

                folder = self.folder_var.get().strip()
                if folder:
                    filters["folder"] = folder

                sort_by_str = self.sort_var.get()
                sort_by = [sort_by_str] if sort_by_str != "relevance" else None

                results, total, _ = self.qe.search(
                    query, filters=filters, sort_by=sort_by,
                    page=self.current_page, per_page=self.per_page,
                )

                add_to_history(query)
                self.current_results = results
                self.current_query = query
                self.tab.after(0, lambda t=total: self._display_results(t))

                self.tab.after(0, lambda: self.status_bar.configure(text=f"Found {total} results for '{query}'"))
            except Exception as e:
                self.tab.after(0, lambda: self.status_bar.configure(text=f"Error: {e}"))
            finally:
                self.tab.after(0, lambda: self.search_btn.configure(state="normal"))

        threading.Thread(target=search_thread, daemon=True).start()

    def _display_results(self, total):
        data = [["Filename", "Extension", "Size", "Modified", "Path", "Score"]]
        for r in self.current_results:
            size_str = self._format_size(r["size"])
            mod_str = r.get("modified", "")[:10] if r.get("modified") else ""
            data.append([
                r["filename"], r.get("extension", ""), size_str,
                mod_str, r.get("folder", ""), f"{r['score']:.2f}",
            ])

        self.result_table.destroy()
        self.result_table = CTkTable(
            self.result_scroll,
            row=len(data),
            column=6,
            values=data,
            header_color=("gray75", "gray25"),
            hover_color=("gray85", "gray30"),
            font=("", 11),
            wraplength=300,
            padx=4,
            pady=2,
            corner_radius=4,
        )
        self.result_table.pack(fill="x", padx=5, pady=3)
        self.result_table.bind("<ButtonRelease-1>", self._on_result_click)
        self.result_table.bind("<Double-1>", self._on_result_double_click)

        ext_colors = self.config.get("extension_colors", {})
        for i, r in enumerate(self.current_results):
            ext = r.get("extension", "")
            color = ext_colors.get(ext)
            if color:
                cell = self.result_table.frame.get((i + 1, 1))
                if cell:
                    try:
                        cell.configure(fg_color=color)
                    except Exception:
                        pass

        total_pages = max(1, (total + self.per_page - 1) // self.per_page)
        self.page_label.configure(text=f"Page {self.current_page}/{total_pages}")
        self.total_label.configure(text=f"({total} total)")
        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < total_pages else "disabled")

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._execute_search()

    def _next_page(self):
        self.current_page += 1
        self._execute_search()

    def _on_result_click(self, event=None):
        sel = self.result_table.get_selected_row()
        row_index = sel["row_index"]
        if row_index is not None and row_index > 0 and row_index - 1 < len(self.current_results):
            result = self.current_results[row_index - 1]
            self._show_preview(result)

    def _on_result_double_click(self, event=None):
        sel = self.result_table.get_selected_row()
        row_index = sel["row_index"]
        if row_index is not None and row_index > 0 and row_index - 1 < len(self.current_results):
            result = self.current_results[row_index - 1]
            self._reveal_in_explorer(result["path"])

    def _reveal_in_explorer(self, filepath):
        if not filepath or not os.path.exists(filepath):
            self.status_bar.configure(text="File not found.")
            return
        import subprocess
        import sys
        try:
            if sys.platform == "win32":
                subprocess.run(["explorer", f"/select,{os.path.normpath(filepath)}"])
            elif sys.platform == "darwin":
                subprocess.run(["open", "-R", filepath])
            else:
                subprocess.run(["xdg-open", os.path.dirname(filepath)])
        except Exception as e:
            self.status_bar.configure(text=f"Error opening folder: {e}")

    def _show_preview(self, result):
        filepath = result["path"]
        self.preview_filename.configure(text=filepath)
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")

        text = extract_text(filepath)
        if text:
            if self.config.get("highlight_matches", True) and self.current_query:
                query_terms = self.current_query.split()
                highlighted = highlight_text(text[:5000], query_terms, context_chars=120)
                if highlighted:
                    self.preview_text.insert("1.0", highlighted[:3000])
                else:
                    self.preview_text.insert("1.0", text[:2000])
            else:
                self.preview_text.insert("1.0", text[:2000])
        else:
            self.preview_text.insert("1.0", "(No preview available)")

        self.preview_text.configure(state="disabled")

        if not self.preview_visible:
            self._toggle_preview()

    def _open_selected_file(self):
        filepath = self.preview_filename.cget("text")
        if filepath and os.path.exists(filepath):
            import subprocess
            import sys
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                subprocess.run(["open", filepath])
            else:
                subprocess.run(["xdg-open", filepath])

    def _reveal_selected_in_folder(self):
        filepath = self.preview_filename.cget("text")
        self._reveal_in_explorer(filepath)

    def _save_search(self):
        query = self.search_var.get().strip()
        if not query:
            self.status_bar.configure(text="Nothing to save - enter a query first.")
            return

        dialog = ctk.CTkInputDialog(
            title="Save Search",
            text=f"Save current search as:\n\nQuery: {query}",
        )
        name = dialog.get_input()
        if name and name.strip():
            filters = {}
            ext = self.ext_var.get().strip()
            if ext:
                filters["extension"] = ext
            folder = self.folder_var.get().strip()
            if folder:
                filters["folder"] = folder
            save_search(name.strip(), query, filters)
            self.status_bar.configure(text=f"Search saved as '{name.strip()}'")

    def _export_csv(self):
        if not self.current_results:
            self.status_bar.configure(text="No results to export.")
            return

        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        def do_export():
            try:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Filename", "Extension", "Size", "Modified", "Folder", "Path", "Score"])
                    for r in self.current_results:
                        writer.writerow([
                            r["filename"], r.get("extension", ""),
                            r["size"], r.get("modified", ""),
                            r.get("folder", ""), r["path"],
                            f"{r['score']:.2f}",
                        ])
                self.tab.after(0, lambda: self.status_bar.configure(text=f"Exported {len(self.current_results)} results to {path}"))
            except Exception as e:
                self.tab.after(0, lambda: self.status_bar.configure(text=f"Export error: {e}"))

        threading.Thread(target=do_export, daemon=True).start()

    def _format_size(self, size):
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
