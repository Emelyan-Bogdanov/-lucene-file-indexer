import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from fileindexer.ui.search_controller import SearchController
from fileindexer.ui.results_display import ResultsDisplay


class MainWindow:
    def __init__(self, context):
        self.ctx = context
        self.root = tk.Tk()
        self.root.title("Lucene File Indexer")
        self.root.geometry("1100x700")
        self.root.minsize(800, 500)

        self._build_menu()
        self._build_ui()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Add Directory...", command=self._add_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        index_menu = tk.Menu(menubar, tearoff=0)
        index_menu.add_command(label="Start Indexing", command=self._start_indexing)
        index_menu.add_command(label="Recreate Index", command=self._recreate_index)
        index_menu.add_separator()
        index_menu.add_command(label="Index Stats", command=self._show_stats)
        menubar.add_cascade(label="Index", menu=index_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=6)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        self.search_ctrl = SearchController(
            main,
            on_search=self._on_search,
            on_add_directory=self._add_directory,
            on_start_index=self._start_indexing,
        )
        self.search_ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.results_display = ResultsDisplay(main, on_open_file=self._open_file)
        self.results_display.grid(row=1, column=0, sticky="nsew")

        status_frame = ttk.Frame(main)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        self.status_bar = ttk.Label(status_frame, text="Ready", relief="sunken", anchor="w")
        self.status_bar.pack(fill="x")

        self._refresh_dir_label()

    def _on_search(self, query_text):
        if not query_text:
            self.results_display.display_results([])
            self.status_bar.config(text="Ready")
            return
        try:
            results = self.ctx.search_engine.search(query_text)
            self.results_display.display_results(results)
            self.status_bar.config(text=f"Found {len(results)} result(s) for: {query_text}")
        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    def _add_directory(self):
        d = filedialog.askdirectory(title="Select a directory to index")
        if d:
            dirs = self.ctx.config.indexed_directories
            if d not in dirs:
                dirs.append(d)
                self.ctx.config.indexed_directories = dirs
                self._refresh_dir_label()

    def _refresh_dir_label(self):
        self.search_ctrl.update_dirs(self.ctx.config.indexed_directories)

    def _start_indexing(self):
        if not self.ctx.config.indexed_directories:
            messagebox.showwarning("No Directories", "Add at least one directory first.")
            return
        self.search_ctrl.index_btn.config(state="disabled")
        self.search_ctrl.reset_progress()

        def worker():
            try:
                self.ctx.file_indexer.index_directories(
                    progress_callback=lambda c, t, f: self.search_ctrl.after(
                        0, self.search_ctrl.set_progress, c, t, f
                    )
                )
                self.search_ctrl.after(0, self._on_index_complete)
            except Exception as e:
                self.search_ctrl.after(0, messagebox.showerror, "Index Error", str(e))
                self.search_ctrl.after(0, self._on_index_complete)

        self.status_bar.config(text="Indexing...")
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _on_index_complete(self):
        self.search_ctrl.index_btn.config(state="normal")
        self.search_ctrl.reset_progress()
        nd = self.ctx.index_manager.num_docs
        self.status_bar.config(text=f"Indexing complete — {nd} document(s) indexed")

    def _recreate_index(self):
        confirm = messagebox.askyesno(
            "Recreate Index",
            "This will rebuild the entire index. Continue?",
        )
        if not confirm:
            return
        self.search_ctrl.index_btn.config(state="disabled")
        self.search_ctrl.reset_progress()

        def worker():
            try:
                self.ctx.index_manager.close()
                import shutil
                idx_path = self.ctx.config.index_path
                if idx_path.exists():
                    shutil.rmtree(idx_path)
                self.ctx.index_manager = type(self.ctx.index_manager)(str(idx_path))
                self.ctx.file_indexer.index_manager = self.ctx.index_manager
                self.ctx.search_engine.index_manager = self.ctx.index_manager
                self.ctx.file_indexer.index_directories(
                    progress_callback=lambda c, t, f: self.search_ctrl.after(
                        0, self.search_ctrl.set_progress, c, t, f
                    )
                )
                self.search_ctrl.after(0, self._on_index_complete)
            except Exception as e:
                self.search_ctrl.after(0, messagebox.showerror, "Index Error", str(e))
                self.search_ctrl.after(0, self._on_index_complete)

        self.status_bar.config(text="Recreating index...")
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _show_stats(self):
        nd = self.ctx.index_manager.num_docs
        dirs = self.ctx.config.indexed_directories
        msg = f"Documents indexed: {nd}\n\nIndexed directories:\n"
        msg += "\n".join(f"  • {d}" for d in dirs) if dirs else "  (none)"
        messagebox.showinfo("Index Stats", msg)

    def _open_file(self, path):
        try:
            os.startfile(path)
        except Exception:
            try:
                import subprocess
                subprocess.Popen(["open" if os.name == "posix" else "start", path], shell=True)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file:\n{e}")

    def _show_about(self):
        messagebox.showinfo(
            "About Lucene File Indexer",
            "Lucene File Indexer v1.0.0\n\n"
            "A fast desktop file search application using\n"
            "PyLucene for indexing and Apache Tika for parsing.",
        )

    def _on_close(self):
        self.ctx.index_manager.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
