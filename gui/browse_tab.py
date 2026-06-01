import threading

import customtkinter as ctk

from indexer.engine import FileIndexer


class BrowseTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config

    def build(self, tab):
        self.tab = tab
        self._build_controls(tab)
        self._build_results(tab)
        self._refresh_thread()

    def _build_controls(self, tab):
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="x", padx=10, pady=10)

        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(header_frame, text="Faceted Browse", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        self.total_docs_label = ctk.CTkLabel(header_frame, text="", font=ctk.CTkFont(size=11))
        self.total_docs_label.pack(side="right")

        controls = ctk.CTkFrame(frame, fg_color="transparent")
        controls.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(controls, text="Group by:").pack(side="left", padx=(0, 3))
        self.field_var = ctk.StringVar(value="extension")
        field_menu = ctk.CTkOptionMenu(
            controls, variable=self.field_var,
            values=["extension", "mime_type", "folder"],
            command=lambda _: self._refresh(),
            width=110,
        )
        field_menu.pack(side="left", padx=3)

        ctk.CTkLabel(controls, text="Max:").pack(side="left", padx=(8, 3))
        self.top_var = ctk.StringVar(value="20")
        top_entry = ctk.CTkEntry(controls, textvariable=self.top_var, width=50)
        top_entry.pack(side="left", padx=3)
        top_entry.bind("<Return>", lambda e: self._refresh())

        ctk.CTkButton(controls, text="Refresh", width=70, command=self._refresh).pack(side="left", padx=3)

        self.loading_label = ctk.CTkLabel(controls, text="")
        self.loading_label.pack(side="right", padx=10)

    def _build_results(self, tab):
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.results_text = ctk.CTkTextbox(frame, font=ctk.CTkFont(size=12))
        self.results_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.results_text.configure(state="disabled")

    def _refresh_thread(self):
        self._refresh()

    def _refresh(self):
        self.loading_label.configure(text="Loading...")

        def task():
            try:
                indexer = FileIndexer(self.config["index_dir"], self.config)
                reader = indexer.ix.reader()

                field = self.field_var.get()
                top = int(self.top_var.get() or 20)

                counts = {}
                for stored in reader.all_stored_fields():
                    val = stored.get(field, "(unknown)")
                    if not val:
                        val = "(unknown)"
                    counts[val] = counts.get(val, 0) + 1

                grand_total = sum(counts.values())
                sorted_counts = sorted(counts.items(), key=lambda x: -x[1])[:top]

                lines = [f"{'Value':<40} {'Count':>8} {'%':>8}", "=" * 60]
                for val, count in sorted_counts:
                    pct = count / grand_total * 100 if grand_total else 0
                    display_val = val[:40] if len(str(val)) > 40 else val
                    lines.append(f"{display_val:<40} {count:>8} {pct:>7.1f}%")

                indexer.close()

                self.tab.after(0, lambda t=grand_total: self.total_docs_label.configure(text=f"Total documents: {t}"))
                self.tab.after(0, lambda: self._display("\n".join(lines)))
            except Exception as e:
                self.tab.after(0, lambda: self.total_docs_label.configure(text=""))
                self.tab.after(0, lambda: self._display(f"Error: {e}"))
            finally:
                self.tab.after(0, lambda: self.loading_label.configure(text=""))

        threading.Thread(target=task, daemon=True).start()

    def _display(self, text):
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", text)
        self.results_text.configure(state="disabled")
