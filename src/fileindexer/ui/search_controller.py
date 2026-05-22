import tkinter as tk
from tkinter import ttk


class SearchController(ttk.Frame):
    def __init__(self, parent, on_search, on_add_directory, on_start_index, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_search = on_search
        self.on_add_directory = on_add_directory
        self.on_start_index = on_start_index

        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(1, weight=1)

        row = 0
        ttk.Label(self, text="Search:").grid(row=row, column=0, padx=(0, 4), sticky="w")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self, textvariable=self.search_var)
        self.search_entry.grid(row=row, column=1, sticky="ew", padx=(0, 4))
        self.search_entry.bind("<Return>", lambda e: self._do_search())

        self.search_btn = ttk.Button(self, text="Search", command=self._do_search)
        self.search_btn.grid(row=row, column=2, padx=(0, 4))

        self.clear_btn = ttk.Button(self, text="Clear", command=self._clear)
        self.clear_btn.grid(row=row, column=3)

        row += 1
        ttk.Label(self, text="Index dirs:").grid(row=row, column=0, padx=(0, 4), sticky="w")
        self.dir_label = ttk.Label(self, text="(none)")
        self.dir_label.grid(row=row, column=1, sticky="w", padx=(0, 4))
        self.add_dir_btn = ttk.Button(
            self, text="Add Directory", command=self._add_dir
        )
        self.add_dir_btn.grid(row=row, column=2, padx=(0, 4))
        self.index_btn = ttk.Button(
            self, text="Start Indexing", command=self._start_index
        )
        self.index_btn.grid(row=row, column=3)

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.grid(row=row + 1, column=0, columnspan=4, sticky="ew", pady=(4, 0))

        self.status_label = ttk.Label(self, text="")
        self.status_label.grid(row=row + 2, column=0, columnspan=4, sticky="w")

    def _do_search(self):
        text = self.search_var.get().strip()
        if text:
            self.on_search(text)

    def _clear(self):
        self.search_var.set("")
        self.on_search("")

    def _add_dir(self):
        self.on_add_directory()

    def _start_index(self):
        self.on_start_index()

    def update_dirs(self, dirs):
        if dirs:
            self.dir_label.config(text="; ".join(dirs))
        else:
            self.dir_label.config(text="(none)")

    def set_progress(self, current, total, current_file=""):
        self.progress["maximum"] = total
        self.progress["value"] = current
        short = current_file[-60:] if len(current_file) > 60 else current_file
        self.status_label.config(text=f"[{current}/{total}] {short}")
        self.update_idletasks()

    def reset_progress(self):
        self.progress["value"] = 0
        self.progress["maximum"] = 100
        self.status_label.config(text="")
