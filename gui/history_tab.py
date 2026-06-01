import customtkinter as ctk

from indexer.engine import FileIndexer
from utils.history import load_search_history, load_saved_searches, delete_saved_search


class HistoryTab:
    def __init__(self, parent, config, on_search=None):
        self.parent = parent
        self.config = config
        self.on_search = on_search
        self._history_entries = []
        self._saved_entries = {}

    def build(self, tab):
        self.tab = tab
        self._build_search_history(tab)
        self._build_saved_searches(tab)
        self.refresh()

    def _build_search_history(self, tab):
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(header_frame, text="Recent Searches", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkLabel(
            header_frame, text="(double-click to re-run)",
            font=ctk.CTkFont(size=10), text_color=("gray40", "gray60"),
        ).pack(side="left", padx=10)

        self.history_text = ctk.CTkTextbox(frame, font=ctk.CTkFont(size=12))
        self.history_text.pack(fill="both", expand=True, padx=5, pady=3)
        self.history_text.configure(state="disabled")
        self.history_text.bind("<Double-1>", self._on_history_click)

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkButton(btn_frame, text="Refresh History", width=120, command=self.refresh).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Clear History", width=100, command=self._clear_history, fg_color="darkred").pack(side="left", padx=5)

    def _build_saved_searches(self, tab):
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(header_frame, text="Saved Searches", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkLabel(
            header_frame, text="(double-click to run)",
            font=ctk.CTkFont(size=10), text_color=("gray40", "gray60"),
        ).pack(side="left", padx=10)

        self.saved_text = ctk.CTkTextbox(frame, font=ctk.CTkFont(size=12))
        self.saved_text.pack(fill="both", expand=True, padx=5, pady=3)
        self.saved_text.configure(state="disabled")
        self.saved_text.bind("<Double-1>", self._on_saved_click)

    def _on_history_click(self, event=None):
        if not self._history_entries:
            return
        try:
            idx = int(self.history_text.index(f"@{event.x},{event.y}").split(".")[0]) - 1
            if 0 <= idx < len(self._history_entries):
                query = self._history_entries[idx]
                if self.on_search:
                    self.on_search(query)
        except (ValueError, IndexError, AttributeError):
            pass

    def _on_saved_click(self, event=None):
        if not self._saved_entries:
            return
        try:
            idx = int(self.saved_text.index(f"@{event.x},{event.y}").split(".")[0]) - 1
            keys = list(self._saved_entries.keys())
            if 0 <= idx < len(keys):
                name = keys[idx]
                query = self._saved_entries[name].get("query", "")
                if self.on_search and query:
                    self.on_search(query)
        except (ValueError, IndexError, AttributeError):
            pass

    def refresh(self):
        history = load_search_history()
        self._history_entries = []
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        if history:
            for i, entry in enumerate(history[:30], 1):
                ts = entry.get("timestamp", "")[:19] if entry.get("timestamp") else ""
                self.history_text.insert("end", f"{i:2d}. [{ts}] {entry['query']}\n")
                self._history_entries.append(entry["query"])
        else:
            self.history_text.insert("1.0", "(No search history)")
        self.history_text.configure(state="disabled")

        saved = load_saved_searches()
        self._saved_entries = saved
        self.saved_text.configure(state="normal")
        self.saved_text.delete("1.0", "end")
        if saved:
            for name, data in saved.items():
                self.saved_text.insert("end", f"[{name}]: {data['query']}  (saved: {data.get('timestamp', '')[:19]})\n")
        else:
            self.saved_text.insert("1.0", "(No saved searches)")
        self.saved_text.configure(state="disabled")

    def _clear_history(self):
        from utils.history import save_search_history
        save_search_history([])
        self.refresh()
