# macOS Cleanup Tool
# Copyright (c) 2025 Peter
# Licensed under the MIT License. See LICENSE for details.

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import threading
import queue
import shutil
import time
import logging

from scanner import scan_system, scan_folder, get_size, CRITICAL_SYSTEM_PATHS
import settings

try:
    import send2trash
except ImportError:
    send2trash = None

def size_to_bytes(size_str):
    size_str = size_str.strip()
    if size_str == "0B":
        return 0
    try:
        multipliers = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
        num = float(size_str[:-1])
        unit = size_str[-1]
        return int(num * multipliers.get(unit, 1))
    except (ValueError, KeyError):
        return 0

class CleanupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MacOS Cleanup Tool")
        self.root.geometry("1280x640")
        self.items = []
        self.display_items = []
        self.scan_queue = queue.Queue()
        self.is_scanning = False
        self.selected_item = None
        self.top_level_items = []
        self.status_var = tk.StringVar()
        self.deleted_paths = []
        self.app_settings = settings.load_settings()
        self.size_filter = tk.StringVar(value=self.app_settings.get("size_filter", "All"))
        self.custom_size = tk.StringVar(value="100")
        self.search_query = tk.StringVar(value="")
        self.current_folder = self.app_settings.get("last_scan_path", os.path.expanduser("~"))
        self.max_depth = tk.IntVar(value=self.app_settings.get("max_depth", 3))
        self.exclusions = tk.StringVar(value=self.app_settings.get("exclusions", ""))
        self.dark_mode = self.app_settings.get("dark_mode", "auto")
        self.sort_column = self.app_settings.get("sort_column", "size")
        self.sort_descending = self.app_settings.get("sort_descending", True)
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("cleanup.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Application started")
        self.create_ui()
        self.update_button_states()
        self.set_status(f"Viewing {self.current_folder}")
        self.root.after(100, self.start_scan)

    def save_settings(self):
        self.app_settings["last_scan_path"] = self.current_folder
        self.app_settings["size_filter"] = self.size_filter.get()
        self.app_settings["max_depth"] = self.max_depth.get()
        self.app_settings["exclusions"] = self.exclusions.get()
        self.app_settings["dark_mode"] = self.dark_mode
        self.app_settings["sort_column"] = self.sort_column
        self.app_settings["sort_descending"] = self.sort_descending
        self.app_settings["plugins"] = self.app_settings.get("plugins", {})
        settings.save_settings(self.app_settings)
        self.logger.info("Settings saved")

    def get_free_space(self):
        try:
            usage = shutil.disk_usage("/")
            free_gb = usage.free / (1024**3)
            return f"{free_gb:.1f}"
        except Exception as e:
            self.logger.error(f"Failed to get free space: {e}")
            return "Unknown"

    def detect_dark_mode(self):
        try:
            if self.dark_mode == "dark":
                return True
            elif self.dark_mode == "light":
                return False
            # Pass the root window to MacWindowStyle
            return self.root.tk.call('tk::unsupported::MacWindowStyle', 'isdark', self.root)
        except Exception as e:
            self.logger.warning(f"Dark mode detection failed: {e}")
            # Fallback to light mode
            return False

    def set_status(self, message):
        free_space = self.get_free_space()
        filter_info = ""
        thresholds = {
            "All": 0,
            "Small (100MB+)": 100,
            "Medium (500MB+)": 500,
            "Large (1GB+)": 1024,
        }
        custom_size_str = self.custom_size.get().strip()
        if custom_size_str:
            try:
                custom_mb = float(custom_size_str)
                if custom_mb >= 0:
                    filter_info = f"≥ {custom_mb} MB"
                else:
                    filter_info = f"≥ {thresholds[self.size_filter.get()]} MB"
            except ValueError:
                filter_info = f"≥ {thresholds[self.size_filter.get()]} MB"
        else:
            filter_info = f"≥ {thresholds[self.size_filter.get()]} MB"
        search_info = f"Search: {self.search_query.get()}" if self.search_query.get() else ""
        if not self.selected_item and not self.is_scanning:
            message = "Right-click an item for actions (Open, Trash, Clean)."
        self.status_var.set(f"Free Space: {free_space} GB | Filter: {filter_info} | {search_info} | {message}")

    def create_ui(self):
        self.logger.info("Creating UI")
        # Apply theme
        style = ttk.Style()
        style.theme_use('aqua')
        is_dark = self.detect_dark_mode()
        tree_bg = '#2d2d2d' if is_dark else '#ffffff'
        tree_fg = '#ffffff' if is_dark else '#000000'
        oddrow_bg = '#3c3c3c' if is_dark else '#f0f0f0'
        evenrow_bg = '#2d2d2d' if is_dark else '#ffffff'
        select_bg = '#4a90e2' if is_dark else '#0078d7'
        style.configure("Treeview", rowheight=25, font=('Helvetica', 10), background=tree_bg, foreground=tree_fg)
        style.configure("Treeview.Heading", font=('Helvetica', 11, 'bold'))
        style.map("Treeview", background=[('selected', select_bg)])
        style.configure("TButton", font=('Helvetica', 10))
        style.configure("TLabel", font=('Helvetica', 9))

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill="x", pady=(0, 10))

        # Navigation
        nav_frame = ttk.LabelFrame(toolbar, text="Navigation", padding=5)
        nav_frame.pack(side="left", padx=5)
        self.home_btn = ttk.Button(nav_frame, text="🏠 Home", command=self.go_home)
        self.home_btn.pack(side="left", padx=2)
        self.up_btn = ttk.Button(nav_frame, text="⬆ Go Up", command=self.go_up)
        self.up_btn.pack(side="left", padx=2)
        self.deep_btn = ttk.Button(nav_frame, text="🔍 Go Deep", command=self.go_deep)
        self.deep_btn.pack(side="left", padx=2)

        # Separator
        ttk.Separator(toolbar, orient="vertical").pack(side="left", padx=5, fill="y")

        # Actions
        actions_frame = ttk.LabelFrame(toolbar, text="Actions", padding=5)
        actions_frame.pack(side="left", padx=5)
        self.scan_btn = ttk.Button(actions_frame, text="Scan System", command=self.start_system_scan)
        self.scan_btn.pack(side="left", padx=2)
        self.actions_btn = ttk.Button(actions_frame, text="Actions", command=self.show_actions_menu)
        self.actions_btn.pack(side="left", padx=2)
        self.undo_btn = ttk.Button(actions_frame, text="🗑️ Undo", command=self.undo_last_delete)
        self.undo_btn.pack(side="left", padx=2)

        # Separator
        ttk.Separator(toolbar, orient="vertical").pack(side="left", padx=5, fill="y")

        # Filters
        filter_frame = ttk.LabelFrame(toolbar, text="Filters", padding=5)
        filter_frame.pack(side="right", padx=5)
        ttk.Label(filter_frame, text="Size:", font=('Helvetica', 9)).pack(side="left")
        self.filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.size_filter,
            values=["All", "Small (100MB+)", "Medium (500MB+)", "Large (1GB+)"],
            state="readonly",
            width=16
        )
        self.filter_combo.pack(side="left", padx=2)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.on_filter_change())
        ttk.Label(filter_frame, text="Custom (MB):", font=('Helvetica', 9)).pack(side="left", padx=(5, 2))
        self.size_entry = ttk.Entry(filter_frame, textvariable=self.custom_size, width=6)
        self.size_entry.pack(side="left")
        self.size_entry.bind("<FocusOut>", lambda e: self.on_filter_change())
        self.size_entry.bind("<Return>", lambda e: self.on_filter_change())
        ttk.Label(filter_frame, text="Search:", font=('Helvetica', 9)).pack(side="left", padx=(5, 2))
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_query, width=15)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self.on_search_change())
        self.clear_search_btn = ttk.Button(filter_frame, text="Clear", command=self.clear_search)
        self.clear_search_btn.pack(side="left", padx=2)

        # Hint label
        hint_label = ttk.Label(
            main_frame,
            text="Right-click a row or use toolbar for actions. Click column headers to sort.",
            font=('Helvetica', 10, 'italic'),
            foreground="#555555"
        )
        hint_label.pack(fill="x", pady=(0, 5))

        # Treeview
        columns = ("category", "name", "path", "size")
        column_headings = {
            "category": "Category",
            "name": "Name",
            "path": "Path",
            "size": "Size"
        }
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=column_headings[col], command=lambda c=col: self.sort_by_column(c, False))
            self.tree.column(col, width=160 if col != "size" else 100, stretch=True)
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure('oddrow', background=oddrow_bg)
        self.tree.tag_configure('evenrow', background=evenrow_bg)

        # Bottom frame
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", pady=5)

        # Settings
        settings_frame = ttk.LabelFrame(bottom_frame, text="Settings", padding=5)
        settings_frame.pack(side="left")
        ttk.Label(settings_frame, text="Depth:", font=('Helvetica', 9)).pack(side="left")
        self.depth_spin = tk.Spinbox(settings_frame, from_=1, to=10, width=3, textvariable=self.max_depth, command=self.on_depth_change)
        self.depth_spin.pack(side="left", padx=2)
        self.depth_spin.bind("<FocusOut>", lambda e: self.on_depth_change())
        self.depth_spin.bind("<Return>", lambda e: self.on_depth_change())
        ttk.Label(settings_frame, text="Excl:", font=('Helvetica', 9)).pack(side="left", padx=(5, 2))
        self.excl_entry = ttk.Entry(settings_frame, textvariable=self.exclusions, width=15)
        self.excl_entry.pack(side="left")
        self.excl_entry.bind("<FocusOut>", lambda e: self.on_exclusions_change())
        self.excl_entry.bind("<Return>", lambda e: self.on_exclusions_change())
        # Plugins button in Settings
        self.plugins_btn = ttk.Button(settings_frame, text="Plugins", command=self.show_plugins_menu)
        self.plugins_btn.pack(side="left", padx=8)

        # Separator
        ttk.Separator(bottom_frame, orient="vertical").pack(side="left", padx=5, fill="y")

        # Progress
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(bottom_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=5)
        status_label = ttk.Label(
            bottom_frame, textvariable=self.status_var, relief="sunken", anchor="w",
            font=('Helvetica', 10, 'bold'), background="#e0e0e0"
        )
        status_label.pack(fill="x")

        # Context and actions menus
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Open in Finder", command=self.open_in_finder, state="disabled", accelerator="Cmd+F")
        self.context_menu.add_command(label="Move to Trash", command=self.move_to_trash, state="disabled", accelerator="Cmd+T")
        self.context_menu.add_command(label="Clean Folder", command=self.clean_folder, state="disabled", accelerator="Cmd+E")
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Button-2>", self.show_context_menu)
        self.tree.bind("<Control-Button-1>", self.show_context_menu)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.open_in_finder)

        self.actions_menu = tk.Menu(self.root, tearoff=0)
        self.actions_menu.add_command(label="Open in Finder", command=self.open_in_finder, state="disabled")
        self.actions_menu.add_command(label="Move to Trash", command=self.move_to_trash, state="disabled")
        self.actions_menu.add_command(label="Clean Folder", command=self.clean_folder, state="disabled")

        # Plugins menu
        self.plugins_menu = tk.Menu(self.root, tearoff=0)
        self.update_plugins_menu()

        # Help menu
        menubar = tk.Menu(self.root)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_help)
        menubar.add_cascade(label="Help", menu=help_menu)
        menubar.add_cascade(label="Plugins", menu=self.plugins_menu)
        self.root.config(menu=menubar)

        self.root.bind("<Command-f>", lambda event: self.open_in_finder())
        self.root.bind("<Command-t>", lambda event: self.move_to_trash())
        self.root.bind("<Command-e>", lambda event: self.clean_folder())

    def update_plugins_menu(self):
        import glob
        import os
        import importlib.util
        self.plugins_menu.delete(0, tk.END)
        # Discover all plugins in the plugins folder using importlib and class inspection
        plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
        plugin_files = glob.glob(os.path.join(plugins_dir, "*.py"))
        plugin_names = []
        for f in plugin_files:
            base = os.path.basename(f)
            if base in ["__init__", "plugin_base"]:
                continue
            module_name = os.path.splitext(base)[0]
            spec = importlib.util.spec_from_file_location(module_name, f)
            if not spec or not spec.loader:
                continue
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except Exception:
                continue
            # Only include plugins that define a Plugin class subclassing PluginBase
            if hasattr(module, "Plugin"):
                plugin_class = getattr(module, "Plugin")
                from plugins.plugin_base import PluginBase
                if isinstance(plugin_class, type) and issubclass(plugin_class, PluginBase):
                    plugin_names.append(module_name)
        # Get enabled/disabled state from settings
        plugins_state = self.app_settings.get("plugins", {})
        self._plugin_vars = {}  # Store BooleanVars to keep them alive
        for plugin_name in sorted(plugin_names):
            enabled = plugins_state.get(plugin_name, True)
            var = tk.BooleanVar(value=enabled)
            self._plugin_vars[plugin_name] = var  # Prevent garbage collection
            self.plugins_menu.add_checkbutton(
                label=plugin_name.replace('_', ' ').capitalize(),
                command=lambda pn=plugin_name: self.toggle_plugin(pn),
                variable=var,
                onvalue=True,
                offvalue=False
            )
        self.logger.info("Updated plugins menu")

    def toggle_plugin(self, plugin_name):
        plugins = self.app_settings.get("plugins", {})
        current = plugins.get(plugin_name, True)
        plugins[plugin_name] = not current
        self.app_settings["plugins"] = plugins
        self.save_settings()
        self.update_plugins_menu()
        self.logger.info(f"Toggled plugin {plugin_name} to {plugins[plugin_name]}")

    def show_help(self):
        messagebox.showinfo(
            "Keyboard Shortcuts",
            "Cmd+F: Open in Finder\nCmd+T: Move to Trash\nCmd+E: Clean Folder"
        )

    def show_plugins_menu(self):
        x = self.plugins_btn.winfo_rootx()
        y = self.plugins_btn.winfo_rooty() + self.plugins_btn.winfo_height()
        self.plugins_menu.post(x, y)

    def on_depth_change(self):
        try:
            val = int(self.max_depth.get())
            if val < 1:
                val = 1
        except Exception as e:
            self.logger.error(f"Invalid depth value: {e}")
            val = 3
        self.max_depth.set(val)
        self.save_settings()
        self.logger.info(f"Depth changed to {val}")

    def on_exclusions_change(self):
        self.save_settings()
        self.logger.info("Exclusions updated")

    def on_filter_change(self):
        self.save_settings()
        self.apply_filter()
        self.logger.info(f"Size filter changed to {self.size_filter.get()}")

    def on_search_change(self):
        self.apply_filter()
        self.logger.info(f"Search query: {self.search_query.get()}")

    def clear_search(self):
        self.search_query.set("")
        self.apply_filter()
        self.logger.info("Search cleared")

    def show_context_menu(self, event):
        try:
            row_id = self.tree.identify_row(event.y)
            if row_id and self.items:
                self.tree.selection_set(row_id)
                self.on_tree_select(None)
                self.update_button_states()
                self.context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            self.logger.error(f"Error showing context menu: {e}")

    def show_actions_menu(self):
        if self.selected_item:
            x = self.actions_btn.winfo_rootx()
            y = self.actions_btn.winfo_rooty() + self.actions_btn.winfo_height()
            self.actions_menu.post(x, y)

    def start_system_scan(self):
        self.current_folder = None
        self.save_settings()
        self.start_scan()
        self.logger.info("Started system scan")

    def start_scan(self):
        if self.is_scanning:
            self.logger.warning("Scan already in progress")
            return
        self.is_scanning = True
        self.update_button_states()
        self.progress_var.set(0)
        if self.current_folder:
            self.set_status(f"Scanning {self.current_folder} (max depth {self.max_depth.get()})...")
        else:
            self.set_status("Scanning system temps...")
        self.root.update()
        self.scan_thread = threading.Thread(target=self.scan_in_background)
        self.scan_thread.daemon = True
        self.scan_thread.start()
        self.check_queue()
        self.logger.info("Scan thread started")

    def scan_in_background(self):
        def progress_callback(category, progress):
            self.scan_queue.put(("progress", category, progress))
        exclusions = [e.strip() for e in self.exclusions.get().split(",") if e.strip()]
        if self.current_folder:
            items = scan_folder(
                self.current_folder,
                "Home Folder" if self.current_folder == os.path.expanduser("~") else "Subfolder",
                progress_callback,
                max_depth=self.max_depth.get(),
                exclusions=exclusions
            )
        else:
            items = scan_system(progress_callback, max_depth=self.max_depth.get(), exclusions=exclusions)
        self.top_level_items = items
        self.scan_queue.put(("complete", items))

    def check_queue(self):
        try:
            while True:
                msg = self.scan_queue.get_nowait()
                if msg[0] == "progress":
                    _, category, progress = msg
                    self.progress_var.set(progress)
                    self.set_status(f"Scanning: {category} ({progress:.1f}%)")
                    self.root.update_idletasks()  # Force GUI refresh
                    self.logger.debug(f"Progress updated: {category} ({progress:.1f}%)")
                elif msg[0] == "complete":
                    _, items = msg
                    self.items = sorted(items, key=lambda x: size_to_bytes(x["size"]), reverse=True)
                    self.apply_filter()
                    self.progress_var.set(100)
                    self.set_status(f"Viewing {self.current_folder or 'system temps'}")
                    self.root.update_idletasks()  # Force GUI refresh
                    self.is_scanning = False
                    self.update_button_states()
                    self.logger.info("Scan completed")
                    return
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def apply_filter(self):
        thresholds = {
            "All": 0,
            "Small (100MB+)": 100 * 1024**2,
            "Medium (500MB+)": 500 * 1024**2,
            "Large (1GB+)": 1024**3,
        }
        custom_size_str = self.custom_size.get().strip()
        if custom_size_str:
            try:
                custom_mb = float(custom_size_str)
                if custom_mb >= 0:
                    threshold = int(custom_mb * 1024**2)
                else:
                    threshold = thresholds[self.size_filter.get()]
            except ValueError:
                threshold = thresholds[self.size_filter.get()]
        else:
            threshold = thresholds[self.size_filter.get()]
        search_query = self.search_query.get().strip().lower()
        self.display_items = [
            item for item in self.items
            if size_to_bytes(item["size"]) >= threshold and
            (not search_query or any(
                search_query in field.lower()
                for field in [item["category"], item["short_name"], item["path"]]
            ))
        ]
        self.populate_tree()

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Sort display_items based on stored sort_column and sort_descending
        if self.sort_column == "size":
            sorted_items = sorted(
                self.display_items,
                key=lambda x: size_to_bytes(x["size"]),
                reverse=self.sort_descending
            )
        else:
            sorted_items = sorted(
                self.display_items,
                key=lambda x: x[self.sort_column],
                reverse=self.sort_descending
            )
        for idx, item in enumerate(sorted_items):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree.insert(
                "", "end", values=(item["category"], item["short_name"], item["path"], item["size"]),
                tags=(tag,)
            )

    def update_button_states(self):
        is_folder = (
            self.selected_item
            and os.path.isdir(os.path.expanduser(self.selected_item["path"]))
        )
        has_selection = bool(self.selected_item)
        has_results = bool(self.items)
        at_top_level = self.current_folder is None or self.current_folder == os.path.expanduser("~")
        self.home_btn.config(
            state="disabled" if self.is_scanning or self.current_folder == os.path.expanduser("~") else "normal"
        )
        self.scan_btn.config(state="disabled" if self.is_scanning else "normal")
        self.deep_btn.config(
            state="normal" if has_results and is_folder and not self.is_scanning else "disabled"
        )
        self.up_btn.config(
            state="normal" if has_results and not at_top_level and not self.is_scanning else "disabled"
        )
        self.actions_btn.config(
            state="normal" if has_selection and not self.is_scanning else "disabled"
        )
        self.plugins_btn.config(
            state="normal" if not self.is_scanning else "disabled"
        )
        self.undo_btn.config(
            state="normal" if self.deleted_paths else "disabled"
        )
        self.context_menu.entryconfig(
            "Open in Finder", state="normal" if has_selection else "disabled"
        )
        self.context_menu.entryconfig(
            "Move to Trash", state="normal" if has_selection else "disabled"
        )
        self.context_menu.entryconfig(
            "Clean Folder", state="normal" if is_folder else "disabled"
        )
        self.actions_menu.entryconfig(
            "Open in Finder", state="normal" if has_selection else "disabled"
        )
        self.actions_menu.entryconfig(
            "Move to Trash", state="normal" if has_selection else "disabled"
        )
        self.actions_menu.entryconfig(
            "Clean Folder", state="normal" if is_folder else "disabled"
        )

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            item_id = selected[0]
            values = self.tree.item(item_id, "values")
            self.selected_item = {
                "category": values[0],
                "name": values[1],
                "path": values[2],
                "size": values[3]
            }
            self.set_status(f"Selected: {self.selected_item['path']} ({self.selected_item['size']})")
        else:
            self.selected_item = None
            self.set_status(f"Viewing {self.current_folder or 'system temps'}")
        self.update_button_states()

    def go_home(self):
        self.current_folder = os.path.expanduser("~")
        self.save_settings()
        self.start_scan()
        self.logger.info("Navigated to home")

    def open_in_finder(self, event=None):
        if not self.selected_item:
            return
        try:
            full_path = os.path.expanduser(self.selected_item["path"])
            subprocess.run(["open", "-R", full_path])
            self.logger.info(f"Opened {full_path} in Finder")
        except Exception as e:
            self.logger.error(f"Could not open {self.selected_item['path']}: {e}")
            messagebox.showerror("Error", f"Could not open {self.selected_item['path']}:\n{e}")

    def move_to_trash(self, event=None):
        if not self.selected_item:
            return
        if not send2trash:
            self.logger.error("send2trash package missing")
            messagebox.showerror("Error", "The 'send2trash' package is required. Install it with: pip install send2trash")
            return
        path = self.selected_item["path"]
        full_path = os.path.abspath(os.path.expanduser(path))
        if full_path in CRITICAL_SYSTEM_PATHS:
            self.logger.warning(f"Attempted to trash critical path: {full_path}")
            messagebox.showwarning("Warning", f"Cannot move critical system path: {full_path}")
            return
        if messagebox.askyesno("Confirm Move", f"Move {full_path} to Trash?"):
            for _ in range(3):
                try:
                    if subprocess.run(["lsof", full_path], capture_output=True).returncode == 0:
                        time.sleep(0.5)
                        continue
                    send2trash.send2trash(full_path)
                    self.deleted_paths.append(full_path)
                    self.items = [item for item in self.items if item["path"] != path]
                    self.apply_filter()
                    self.set_status(f"Moved {full_path} to Trash")
                    self.selected_item = None
                    self.update_button_states()
                    self.logger.info(f"Moved {full_path} to Trash")
                    return
                except PermissionError as e:
                    self.logger.error(f"Permission denied: {full_path}: {e}")
                    messagebox.showerror("Error", f"Permission denied: {full_path}. Check file permissions.\nSee cleanup.log for details.")
                    break
                except Exception as e:
                    self.logger.error(f"Could not move {full_path}: {e}")
                    messagebox.showerror("Error", f"Could not move {full_path}: {e}\nSee cleanup.log for details.")
                    break
            self.set_status(f"Error moving {full_path} to Trash")

    def clean_folder(self, event=None):
        if not self.selected_item:
            return
        if not send2trash:
            self.logger.error("send2trash package missing")
            messagebox.showerror("Error", "The 'send2trash' package is required. Install it with: pip install send2trash")
            return
        path = self.selected_item["path"]
        full_path = os.path.abspath(os.path.expanduser(path))
        if not os.path.isdir(full_path):
            self.logger.error(f"Not a directory: {full_path}")
            messagebox.showerror("Error", f"{full_path} is not a directory.")
            self.set_status("Error cleaning folder")
            return
        if full_path in CRITICAL_SYSTEM_PATHS:
            self.logger.warning(f"Attempted to clean critical path: {full_path}")
            messagebox.showwarning("Warning", f"Cannot clean critical system folder: {full_path}")
            return
        try:
            had_errors = False
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                for _ in range(3):
                    try:
                        if subprocess.run(["lsof", item_path], capture_output=True).returncode == 0:
                            time.sleep(0.5)
                            continue
                        send2trash.send2trash(item_path)
                        self.deleted_paths.append(item_path)
                        self.logger.info(f"Trashed {item_path}")
                        break
                    except Exception as e:
                        had_errors = True
                        self.logger.error(f"Failed to trash {item_path}: {e}")
                        break
            self.items = [item for item in self.items if item["path"] != path]
            self.items.append({
                "category": self.selected_item["category"],
                "name": self.selected_item["name"],
                "short_name": self.selected_item["name"],
                "path": path,
                "size": get_size(path),
            })
            self.apply_filter()
            self.set_status(f"Cleaned contents of {full_path} to Trash")
            self.selected_item = None
            self.update_button_states()
            self.logger.info(f"Cleaned folder {full_path}")
            if had_errors:
                messagebox.showwarning("Partial Clean", f"Some items in {full_path} could not be trashed.\nSee cleanup.log for details.")
        except PermissionError as e:
            self.logger.error(f"Permission denied for {full_path}: {e}")
            messagebox.showerror("Error", f"Permission denied for some items in {full_path}. Check permissions.\nSee cleanup.log for details.")
            self.set_status("Error cleaning folder")
        except Exception as e:
            self.logger.error(f"Could not clean {full_path}: {e}")
            messagebox.showerror("Error", f"Could not clean {full_path}: {e}\nSee cleanup.log for details.")
            self.set_status("Error cleaning folder")

    def go_deep(self):
        if not self.selected_item or not os.path.isdir(os.path.expanduser(self.selected_item["path"])):
            self.logger.warning("Go Deep attempted with invalid or non-directory item")
            return
        self.current_folder = self.selected_item["path"]
        self.save_settings()
        self.set_status(f"Scanning {self.current_folder} (max depth {self.max_depth.get()})...")
        self.start_scan()
        self.logger.info(f"Deep scan started for {self.current_folder}")

    def go_up(self):
        if not self.current_folder:
            return
        parent_folder = os.path.dirname(os.path.expanduser(self.current_folder))
        if parent_folder == os.path.expanduser(self.current_folder) or parent_folder == os.path.expanduser("~"):
            self.current_folder = os.path.expanduser("~")
        else:
            self.current_folder = parent_folder
        self.save_settings()
        self.start_scan()
        self.logger.info(f"Navigated up to {self.current_folder}")

    def undo_last_delete(self):
        if not self.deleted_paths:
            messagebox.showinfo("Undo", "Nothing to undo in this session.")
            self.logger.info("Undo attempted; nothing to undo")
            return
        last_path = self.deleted_paths[-1]
        if messagebox.askyesno(
            "Undo (Restore Manually)",
            f"To restore:\n'{last_path}'\nOpen the Trash in Finder now?"
        ):
            subprocess.run(["open", os.path.expanduser("~/.Trash")])
            self.deleted_paths.pop()
            self.logger.info(f"Undo initiated for {last_path}")
        self.update_button_states()

    def sort_by_column(self, col, descending):
        self.sort_column = col
        self.sort_descending = descending
        self.save_settings()
        data = [
            (self.tree.set(child, col), child)
            for child in self.tree.get_children("")
        ]
        if col == "size":
            data.sort(key=lambda t: size_to_bytes(t[0]), reverse=descending)
        else:
            data.sort(reverse=descending)
        for idx, (val, child) in enumerate(data):
            self.tree.move(child, "", idx)
        self.tree.heading(col, command=lambda: self.sort_by_column(col, not descending))
        self.logger.info(f"Sorted by {col}, descending={descending}")

def main():
    root = tk.Tk()
    app = CleanupApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
