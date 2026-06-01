import customtkinter as ctk
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.search_tab import SearchTab
from gui.index_tab import IndexTab
from gui.browse_tab import BrowseTab
from gui.history_tab import HistoryTab
from utils.config import load_config, save_config

APP_VERSION = "1.0.0"


class FileIndexerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = load_config()

        self.title("Lucene File Indexer")
        self.geometry("1200x800")
        self.minsize(900, 600)

        ctk.set_appearance_mode("dark" if self.config.get("dark_mode") else "system")
        ctk.set_default_color_theme("blue")

        self._build_menu()
        self._build_main()
        self._build_statusbar()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_menu(self):
        self.menu_frame = ctk.CTkFrame(self, height=56, corner_radius=0)
        self.menu_frame.pack(fill="x", padx=0, pady=0)
        self.menu_frame.pack_propagate(False)

        title_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=6)

        ctk.CTkLabel(
            title_frame,
            text="File Indexer",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text=f"v{APP_VERSION}  |  Full-text desktop search",
            font=ctk.CTkFont(size=10),
            text_color=("gray40", "gray60"),
        ).pack(anchor="w")

        right_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=10)

        ctk.CTkLabel(
            right_frame,
            text="Ctrl+Enter  Search  |  Ctrl+E  Export",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50"),
        ).pack(side="left", padx=(0, 10))

        self.theme_btn = ctk.CTkButton(
            right_frame,
            text="Dark" if self.config.get("dark_mode") else "Light",
            width=80,
            height=30,
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side="left", padx=5)

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        new = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new)
        self.config["dark_mode"] = new == "Dark"
        save_config(self.config)
        self.theme_btn.configure(text=new)

    def _build_main(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(5, 0))

        self.search_tab = SearchTab(self.tabview, self.config)
        self.index_tab = IndexTab(self.tabview, self.config)
        self.browse_tab = BrowseTab(self.tabview, self.config)
        self.history_tab = HistoryTab(self.tabview, self.config, on_search=self._history_search)

        self.tabview.add("Search")
        self.tabview.add("Index")
        self.tabview.add("Browse")
        self.tabview.add("History")

        self.tabview.tab("Search").pack_forget()
        self.tabview.tab("Index").pack_forget()
        self.tabview.tab("Browse").pack_forget()
        self.tabview.tab("History").pack_forget()

        self.search_tab.build(self.tabview.tab("Search"))
        self.index_tab.build(self.tabview.tab("Index"))
        self.browse_tab.build(self.tabview.tab("Browse"))
        self.history_tab.build(self.tabview.tab("History"))

    def _history_search(self, query):
        self.tabview.set("Search")
        self.search_tab.search_var.set(query)
        self.search_tab._do_search()

    def _build_statusbar(self):
        self.status_frame = ctk.CTkFrame(self, height=28, corner_radius=0)
        self.status_frame.pack(fill="x", padx=0, pady=0, side="bottom")
        self.status_frame.pack_propagate(False)

        self.main_status = ctk.CTkLabel(
            self.status_frame, text="Ready", anchor="w",
            font=ctk.CTkFont(size=10), padx=10,
        )
        self.main_status.pack(side="left", fill="x", expand=True)

        self.version_status = ctk.CTkLabel(
            self.status_frame, text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=10), padx=10,
            text_color=("gray40", "gray60"),
        )
        self.version_status.pack(side="right")

    def _on_close(self):
        self.quit()
        self.destroy()


def run():
    app = FileIndexerGUI()
    app.mainloop()
