import customtkinter as ctk
from tkinter import colorchooser
from utils.config import load_config, save_config


class SettingsTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.extension_rows = []

    def build(self, tab):
        self.tab = tab
        self._build_highlight_toggle(tab)
        self._build_extension_colors(tab)

    def _build_highlight_toggle(self, tab):
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(frame, text="Search Settings", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=5, pady=5)

        self.highlight_var = ctk.BooleanVar(value=self.config.get("highlight_matches", True))
        ctk.CTkCheckBox(
            frame, text="Highlight matching terms in file preview",
            variable=self.highlight_var, command=self._save_setting,
        ).pack(anchor="w", padx=15, pady=5)

    def _build_extension_colors(self, tab):
        frame = ctk.CTkFrame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(header, text="Extension Colors", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkLabel(
            header, text="  Colors are shown in the results table rows",
            font=ctk.CTkFont(size=10), text_color=("gray40", "gray60"),
        ).pack(side="left", padx=10)

        scroll = ctk.CTkScrollableFrame(frame)
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(scroll, text="Extension", font=ctk.CTkFont(size=12, weight="bold"), width=100).grid(row=0, column=0, padx=5, pady=2)
        ctk.CTkLabel(scroll, text="Color", font=ctk.CTkFont(size=12, weight="bold"), width=80).grid(row=0, column=1, padx=5, pady=2)
        ctk.CTkLabel(scroll, text="Preview", font=ctk.CTkFont(size=12, weight="bold"), width=60).grid(row=0, column=2, padx=5, pady=2)
        ctk.CTkLabel(scroll, text="", width=60).grid(row=0, column=3)

        colors = self.config.get("extension_colors", {})
        self.extension_rows = []
        for i, (ext, color) in enumerate(sorted(colors.items())):
            self._add_extension_row(scroll, i + 1, ext, color)

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Add Extension", width=100, command=lambda: self._add_extension_row(scroll, len(self.extension_rows) + 1, "", "#FFFFFF")).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save Colors", width=100, command=self._save_colors).pack(side="left", padx=5)

    def _add_extension_row(self, parent, row, ext, color):
        ext_var = ctk.StringVar(value=ext)
        ext_entry = ctk.CTkEntry(parent, textvariable=ext_var, width=100)
        ext_entry.grid(row=row, column=0, padx=5, pady=2)

        swatch = ctk.CTkFrame(parent, width=40, height=28, corner_radius=4, fg_color=color)
        swatch.grid(row=row, column=2, padx=5, pady=2)

        color_label = ctk.CTkLabel(parent, text=color, width=70, font=ctk.CTkFont(size=10))
        color_label.grid(row=row, column=1, padx=5, pady=2)

        def pick_color(s=swatch, l=color_label):
            _, c = colorchooser.askcolor(title="Pick color", initialcolor=l.cget("text"))
            if c:
                s.configure(fg_color=c)
                l.configure(text=c)

        ctk.CTkButton(parent, text="Pick", width=50, command=pick_color).grid(row=row, column=3, padx=5, pady=2)

        self.extension_rows.append((ext_var, color_label, swatch))

    def _save_setting(self):
        self.config["highlight_matches"] = self.highlight_var.get()
        save_config(self.config)

    def _save_colors(self):
        colors = {}
        for ext_var, color_label, _ in self.extension_rows:
            ext = ext_var.get().strip()
            if ext:
                if not ext.startswith("."):
                    ext = f".{ext}"
                colors[ext] = color_label.cget("text")
        self.config["extension_colors"] = colors
        save_config(self.config)
