import os
import threading

import customtkinter as ctk

from indexer.engine import FileIndexer
from indexer.watcher import FileWatcher
from utils.config import save_config


class IndexTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.watcher = None
        self.watcher_running = False

    def build(self, tab):
        self.tab = tab
        self._build_scan_dirs(tab)
        self._build_controls(tab)
        self._build_stats(tab)
        self._build_log(tab)

    def _build_scan_dirs(self, tab):
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Scan Directories", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=5, pady=5)

        self.dirs_text = ctk.CTkTextbox(frame, height=80)
        self.dirs_text.pack(fill="x", padx=5, pady=5)
        self.dirs_text.insert("1.0", "\n".join(self.config.get("scan_dirs", [])))

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(btn_frame, text="Add Directory", width=120, command=self._add_directory).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save Directories", width=120, command=self._save_dirs).pack(side="left", padx=5)

    def _add_directory(self):
        from tkinter import filedialog
        d = filedialog.askdirectory(title="Select directory to index")
        if d:
            current = self.dirs_text.get("1.0", "end").strip()
            if current:
                self.dirs_text.insert("end", f"\n{d}")
            else:
                self.dirs_text.insert("1.0", d)

    def _save_dirs(self):
        dirs = [d.strip() for d in self.dirs_text.get("1.0", "end").strip().split("\n") if d.strip()]
        self.config["scan_dirs"] = dirs
        save_config(self.config)
        self._log("Directories saved.")

    def _build_controls(self, tab):
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame, text="Index Management", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=5, pady=5)

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", padx=5, pady=5)

        self.index_btn = ctk.CTkButton(btn_frame, text="Index Now", width=100, command=self._do_index)
        self.index_btn.pack(side="left", padx=5)

        self.reindex_btn = ctk.CTkButton(btn_frame, text="Re-index Changed", width=120, command=self._do_reindex)
        self.reindex_btn.pack(side="left", padx=5)

        self.clean_btn = ctk.CTkButton(btn_frame, text="Clean Removed", width=120, command=self._do_clean)
        self.clean_btn.pack(side="left", padx=5)

        self.watch_btn = ctk.CTkButton(btn_frame, text="Start Watching", width=130, command=self._toggle_watch, fg_color="green")
        self.watch_btn.pack(side="left", padx=5)

        progress_frame = ctk.CTkFrame(frame)
        progress_frame.pack(fill="x", padx=5, pady=5)

        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(side="left", fill="x", expand=True)
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(progress_frame, text="0%", width=40, font=ctk.CTkFont(size=11))
        self.progress_label.pack(side="left", padx=(8, 0))

    def _build_stats(self, tab):
        self.stats_frame = ctk.CTkFrame(tab)
        self.stats_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.stats_frame, text="Index Statistics", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=5, pady=5)

        self.stats_text = ctk.CTkLabel(self.stats_frame, text="No index yet.", anchor="w", justify="left")
        self.stats_text.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(self.stats_frame, text="Refresh Stats", width=100, command=self._refresh_stats).pack(anchor="w", padx=5, pady=5)

    def _build_log(self, tab):
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(frame, text="Log", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=5, pady=5)

        self.log_text = ctk.CTkTextbox(frame, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def _log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{msg}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _do_index(self):
        dirs = self.config.get("scan_dirs", [])
        if not dirs:
            self._log("No directories configured.")
            return

        self._log("Starting index...")
        self.index_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")

        def task():
            try:
                indexer = FileIndexer(self.config["index_dir"], self.config)
                total_dirs = len(dirs)
                for i, sd in enumerate(dirs):
                    if os.path.isdir(sd):
                        result = indexer.scan_directory(sd, parallel=self.config.get("parallel_indexing", True))
                        self.tab.after(0, lambda d=sd, r=result: self._log(f"  {d}: {r['indexed']} indexed, {r['skipped']} skipped"))
                    else:
                        self.tab.after(0, lambda d=sd: self._log(f"  {d}: directory not found"))
                    pct = (i + 1) / total_dirs
                    self.tab.after(0, lambda v=pct: self.progress_bar.set(v))
                    self.tab.after(0, lambda v=pct: self.progress_label.configure(text=f"{int(v * 100)}%"))

                stats = indexer.index_stats()
                self.tab.after(0, lambda: self._log(f"Index complete! {stats['total_docs']} documents, {stats['index_size_mb']} MB"))
                self.tab.after(0, self._refresh_stats)
                indexer.close()
            except Exception as e:
                self.tab.after(0, lambda: self._log(f"Error: {e}"))
            finally:
                self.tab.after(0, lambda: self.index_btn.configure(state="normal"))
                self.tab.after(0, lambda: self.progress_bar.set(1))
                self.tab.after(0, lambda: self.progress_label.configure(text="100%"))

        threading.Thread(target=task, daemon=True).start()

    def _do_reindex(self):
        dirs = self.config.get("scan_dirs", [])
        if not dirs:
            self._log("No directories configured.")
            return

        self._log("Checking for changed files...")
        self.reindex_btn.configure(state="disabled")

        def task():
            try:
                indexer = FileIndexer(self.config["index_dir"], self.config)
                reader = indexer.ix.reader()
                indexed_paths = {}
                for stored in reader.all_stored_fields():
                    indexed_paths[stored["path"]] = stored.get("modified", "")
                reader.close()

                changed = []
                for sd in dirs:
                    if os.path.isdir(sd):
                        for root, _, files in os.walk(sd):
                            for f in files:
                                fpath = os.path.join(root, f)
                                if fpath in indexed_paths:
                                    try:
                                        import datetime
                                        current_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat()
                                        if current_mtime != indexed_paths[fpath]:
                                            changed.append(fpath)
                                    except OSError:
                                        pass

                if not changed:
                    self.tab.after(0, lambda: self._log("All files up to date."))
                else:
                    for fpath in changed:
                        indexer.index_file(fpath)
                    self.tab.after(0, lambda: self._log(f"Re-indexed {len(changed)} changed files."))

                indexer.close()
            except Exception as e:
                self.tab.after(0, lambda: self._log(f"Error: {e}"))
            finally:
                self.tab.after(0, lambda: self.reindex_btn.configure(state="normal"))

        threading.Thread(target=task, daemon=True).start()

    def _do_clean(self):
        dirs = self.config.get("scan_dirs", [])
        if not dirs:
            self._log("No directories configured.")
            return

        self._log("Cleaning removed files...")
        self.clean_btn.configure(state="disabled")

        def task():
            try:
                indexer = FileIndexer(self.config["index_dir"], self.config)
                removed = indexer.cleanup_removed_files(dirs)
                self.tab.after(0, lambda: self._log(f"Removed {removed} stale entries."))
                indexer.close()
            except Exception as e:
                self.tab.after(0, lambda: self._log(f"Error: {e}"))
            finally:
                self.tab.after(0, lambda: self.clean_btn.configure(state="normal"))

        threading.Thread(target=task, daemon=True).start()

    def _toggle_watch(self):
        if self.watcher_running:
            if self.watcher:
                self.watcher.stop()
                self.watcher = None
            self.watcher_running = False
            self.watch_btn.configure(text="Start Watching", fg_color="green")
            self._log("Watcher stopped.")
        else:
            dirs = self.config.get("scan_dirs", [])
            if not dirs:
                self._log("No directories to watch.")
                return
            try:
                indexer = FileIndexer(self.config["index_dir"], self.config)
                self.watcher = FileWatcher(indexer, dirs)
                self.watcher.start()
                self.watcher_running = True
                self.watch_btn.configure(text="Stop Watching", fg_color="red")
                self._log("Watcher started. Monitoring for changes...")
            except Exception as e:
                self._log(f"Error starting watcher: {e}")

    def _refresh_stats(self):
        try:
            indexer = FileIndexer(self.config["index_dir"], self.config)
            stats = indexer.index_stats()
            reader = indexer.ix.reader()

            ext_counts = {}
            for stored in reader.all_stored_fields():
                ext = stored.get("extension", "")
                ext_counts[ext] = ext_counts.get(ext, 0) + 1

            extensions = ", ".join(f"{k}: {v}" for k, v in sorted(ext_counts.items(), key=lambda x: -x[1])[:10])

            self.stats_text.configure(
                text=f"Total documents: {stats['total_docs']}\n"
                     f"Index size: {stats['index_size_mb']} MB\n"
                     f"Index directory: {self.config['index_dir']}\n"
                     f"Top extensions: {extensions}"
            )
            indexer.close()
        except Exception as e:
            self.stats_text.configure(text=f"Error: {e}")
