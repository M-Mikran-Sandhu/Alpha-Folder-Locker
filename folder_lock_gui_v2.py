#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════╗
║    FOLDER LOCK GUI v3.0 - MODERN PROTECTION               ║
║           [SECURE • SMART • AUTOMATIC]                    ║
╚═══════════════════════════════════════════════════════════╝

Advanced GUI with system tray and automatic unlock prompts
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from pathlib import Path
from folder_lock_core import FolderLockCore
import webbrowser
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Colors:
    BG_DARK = '#000000'      # Dark Black
    BG_MEDIUM = '#111111'    # Slightly lighter black
    BG_LIGHT = '#222222'     # Dark Gray
    ACCENT = '#006400'       # Dark Green
    ACCENT_HOVER = '#008000' # Green
    TEXT = '#FF0000'         # Red
    TEXT_DIM = '#B22222'     # Firebrick Red (Dimmer)
    ERROR = '#FF0000'        # Red
    WARNING = '#FF8C00'      # Dark Orange
    SUCCESS = '#006400'      # Dark Green
    BUTTON_TEXT = '#FFFFFF'  # White text on dark buttons

class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.default_bg = kwargs.get('bg', Colors.ACCENT)
        self.hover_bg = kwargs.get('activebackground', Colors.ACCENT_HOVER)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.configure(relief='flat', cursor='hand2')

    def on_enter(self, e):
        self['bg'] = self.hover_bg

    def on_leave(self, e):
        self['bg'] = self.default_bg

class ModernMessageBox(tk.Toplevel):
    def __init__(self, parent, title, message, type='info'):
        super().__init__(parent)
        self.result = None
        self.type = type
        
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.configure(bg=Colors.BG_DARK)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 100
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets(title, message)
        
        # Bindings
        self.bind('<Return>', lambda e: self.on_ok())
        self.bind('<Escape>', lambda e: self.on_cancel())
        
    def _create_widgets(self, title, message):
        # Header
        icon_text = "ℹ️"
        if self.type == 'error': icon_text = "❌"
        elif self.type == 'warning': icon_text = "⚠️"
        elif self.type == 'question': icon_text = "❓"
        
        header = tk.Frame(self, bg=Colors.BG_MEDIUM, height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header, text=f"{icon_text}  {title}",
            font=('Segoe UI', 12, 'bold'),
            bg=Colors.BG_MEDIUM, fg=Colors.TEXT
        ).pack(side='left', padx=20)
        
        # Message
        content = tk.Frame(self, bg=Colors.BG_DARK)
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(
            content, text=message,
            font=('Segoe UI', 10),
            bg=Colors.BG_DARK, fg=Colors.TEXT,
            wraplength=360, justify='left'
        ).pack(fill='both', expand=True)
        
        # Buttons
        button_frame = tk.Frame(self, bg=Colors.BG_DARK)
        button_frame.pack(fill='x', side='bottom', pady=20, padx=20)
        
        if self.type == 'question':
            ModernButton(
                button_frame, text="No",
                width=10, command=self.on_cancel,
                bg=Colors.BG_LIGHT, fg=Colors.TEXT
            ).pack(side='right', padx=(10, 0))
            
            ModernButton(
                button_frame, text="Yes",
                width=10, command=self.on_ok,
                bg=Colors.ACCENT, fg=Colors.BUTTON_TEXT
            ).pack(side='right')
        else:
            ModernButton(
                button_frame, text="OK",
                width=10, command=self.on_ok,
                bg=Colors.ACCENT, fg=Colors.BUTTON_TEXT
            ).pack(side='right')
            
    def on_ok(self):
        self.result = True
        self.destroy()
        
    def on_cancel(self):
        self.result = False
        self.destroy()

def show_error(title, message, parent=None):
    ModernMessageBox(parent, title, message, 'error')

def show_info(title, message, parent=None):
    ModernMessageBox(parent, title, message, 'info')

def show_warning(title, message, parent=None):
    ModernMessageBox(parent, title, message, 'warning')
    
def ask_yes_no(title, message, parent=None):
    msg = ModernMessageBox(parent, title, message, 'question')
    parent.wait_window(msg)
    return msg.result

class UnlockDialog(tk.Toplevel):
    def __init__(self, parent, folder_path, locker):
        super().__init__(parent)
        
        self.folder_path = folder_path
        self.locker = locker
        self.result = None
        
        folder_name = Path(folder_path).name
        
        # Window setup
        self.title("🔒 Unlock Folder")
        self.geometry("480x320")
        self.resizable(False, False)
        self.configure(bg=Colors.BG_DARK)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 240
        y = (self.winfo_screenheight() // 2) - 160
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets(folder_name)
        
        # Bindings
        self.bind('<Return>', lambda e: self.unlock_folder())
        self.bind('<Escape>', lambda e: self.destroy())
        
        self.password_entry.focus_set()
    
    def _create_widgets(self, folder_name):
        # Header
        header_frame = tk.Frame(self, bg=Colors.BG_MEDIUM, height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        icon = tk.Label(
            header_frame,
            text="🔐",
            font=('Segoe UI Emoji', 32),
            bg=Colors.BG_MEDIUM,
            fg=Colors.ACCENT
        )
        icon.pack(side='left', padx=20)
        
        title_label = tk.Label(
            header_frame,
            text="Unlock Folder",
            font=('Segoe UI', 16, 'bold'),
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT
        )
        title_label.pack(side='left', fill='y')
        
        # Content
        content_frame = tk.Frame(self, bg=Colors.BG_DARK)
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Folder info
        info_frame = tk.Frame(content_frame, bg=Colors.BG_LIGHT, padx=10, pady=10)
        info_frame.pack(fill='x', pady=(0, 20))
        
        folder_label = tk.Label(
            info_frame,
            text=f"Folder: {folder_name}",
            font=('Segoe UI', 10),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT
        )
        folder_label.pack(anchor='w')
        
        # Password entry
        tk.Label(
            content_frame,
            text="Enter Password or Master Key:",
            font=('Segoe UI', 10),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_DIM
        ).pack(anchor='w', pady=(0, 5))
        
        self.password_entry = tk.Entry(
            content_frame,
            font=('Segoe UI', 12),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT,
            insertbackground=Colors.ACCENT,
            relief='flat',
            show='●'
        )
        self.password_entry.pack(fill='x', ipady=8, pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg=Colors.BG_DARK)
        button_frame.pack(fill='x', side='bottom')
        
        ModernButton(
            button_frame,
            text="Unlock",
            font=('Segoe UI', 10, 'bold'),
            bg=Colors.ACCENT,
            fg=Colors.BUTTON_TEXT,
            activebackground=Colors.ACCENT_HOVER,
            command=self.unlock_folder,
            width=15,
            pady=8
        ).pack(side='right')
        
        ModernButton(
            button_frame,
            text="Cancel",
            font=('Segoe UI', 10),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT,
            activebackground=Colors.BG_MEDIUM,
            command=self.destroy,
            width=10,
            pady=8
        ).pack(side='right', padx=10)

    def unlock_folder(self):
        password = self.password_entry.get()
        
        if not password:
            show_error("Error", "Please enter a password", parent=self)
            return
        
        success, message = self.locker.unlock_folder(self.folder_path, password)
        
        if success:
            self.result = True
            show_info("Success", "✓ Folder unlocked successfully!", parent=self)
            self.destroy()
        else:
            show_error("Access Denied", f"✗ {message}", parent=self)
            self.password_entry.delete(0, tk.END)

class LockDialog(tk.Toplevel):
    def __init__(self, parent, folder_path, locker):
        super().__init__(parent)
        
        self.folder_path = folder_path
        self.locker = locker
        self.result = None
        
        folder_name = Path(folder_path).name
        
        self.title("🔒 Lock Folder")
        self.geometry("480x400")
        self.resizable(False, False)
        self.configure(bg=Colors.BG_DARK)
        
        self.transient(parent)
        self.grab_set()
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 240
        y = (self.winfo_screenheight() // 2) - 200
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets(folder_name)
        
        self.bind('<Return>', lambda e: self.lock_folder())
        self.bind('<Escape>', lambda e: self.destroy())
        
        self.password_entry.focus_set()
    
    def _create_widgets(self, folder_name):
        # Header
        header_frame = tk.Frame(self, bg=Colors.BG_MEDIUM, height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        icon = tk.Label(
            header_frame,
            text="🛡️",
            font=('Segoe UI Emoji', 32),
            bg=Colors.BG_MEDIUM,
            fg=Colors.ACCENT
        )
        icon.pack(side='left', padx=20)
        
        title_label = tk.Label(
            header_frame,
            text="Secure Folder",
            font=('Segoe UI', 16, 'bold'),
            bg=Colors.BG_MEDIUM,
            fg=Colors.TEXT
        )
        title_label.pack(side='left', fill='y')
        
        # Content
        content_frame = tk.Frame(self, bg=Colors.BG_DARK)
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        tk.Label(
            content_frame,
            text=f"Locking: {folder_name}",
            font=('Segoe UI', 10, 'bold'),
            bg=Colors.BG_DARK,
            fg=Colors.ACCENT
        ).pack(anchor='w', pady=(0, 15))
        
        # Password
        tk.Label(
            content_frame,
            text="Create Password:",
            font=('Segoe UI', 10),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_DIM
        ).pack(anchor='w', pady=(0, 5))
        
        self.password_entry = tk.Entry(
            content_frame,
            font=('Segoe UI', 12),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT,
            insertbackground=Colors.ACCENT,
            relief='flat',
            show='●'
        )
        self.password_entry.pack(fill='x', ipady=8, pady=(0, 15))
        
        # Confirm
        tk.Label(
            content_frame,
            text="Confirm Password:",
            font=('Segoe UI', 10),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_DIM
        ).pack(anchor='w', pady=(0, 5))
        
        self.confirm_entry = tk.Entry(
            content_frame,
            font=('Segoe UI', 12),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT,
            insertbackground=Colors.ACCENT,
            relief='flat',
            show='●'
        )
        self.confirm_entry.pack(fill='x', ipady=8, pady=(0, 20))
        
        tk.Label(
            content_frame,
            text="⚠️ Password is required to unlock this specific folder.",
            font=('Segoe UI', 9),
            bg=Colors.BG_DARK,
            fg=Colors.WARNING
        ).pack(anchor='w', pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg=Colors.BG_DARK)
        button_frame.pack(fill='x', side='bottom')
        
        ModernButton(
            button_frame,
            text="Lock Now",
            font=('Segoe UI', 10, 'bold'),
            bg=Colors.ACCENT,
            fg=Colors.BUTTON_TEXT,
            activebackground=Colors.ACCENT_HOVER,
            command=self.lock_folder,
            width=15,
            pady=8
        ).pack(side='right')
        
        ModernButton(
            button_frame,
            text="Cancel",
            font=('Segoe UI', 10),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT,
            activebackground=Colors.BG_MEDIUM,
            command=self.destroy,
            width=10,
            pady=8
        ).pack(side='right', padx=10)

    def lock_folder(self):
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not password:
            show_error("Error", "Please enter a password", parent=self)
            return
        
        if password != confirm:
            show_error("Error", "Passwords do not match", parent=self)
            return
        
        if len(password) < 4:
            show_error("Error", "Password must be at least 4 characters", parent=self)
            return
        
        success, message = self.locker.lock_folder(self.folder_path, password)
        
        if success:
            self.result = True
            show_info("Success", f"✓ Folder locked successfully!", parent=self)
            self.destroy()
        else:
            show_error("Error", f"✗ {message}", parent=self)

class MasterKeySetup(tk.Toplevel):
    def __init__(self, parent, locker):
        super().__init__(parent)
        self.locker = locker
        self.title("🔑 Setup Master Key")
        self.geometry("480x350")
        self.resizable(False, False)
        self.configure(bg=Colors.BG_DARK)
        self.transient(parent)
        self.grab_set()
        
        # Center
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 240
        y = (self.winfo_screenheight() // 2) - 175
        self.geometry(f"+{x}+{y}")
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Header
        header = tk.Frame(self, bg=Colors.ERROR, height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header, text="⚠️ Setup Required", font=('Segoe UI', 14, 'bold'),
            bg=Colors.ERROR, fg=Colors.BG_DARK
        ).pack(side='left', padx=20)
        
        # Content
        content = tk.Frame(self, bg=Colors.BG_DARK)
        content.pack(fill='both', expand=True, padx=30, pady=20)
        
        tk.Label(
            content,
            text="Please create a Master Key.\nThis key can unlock ANY folder if you forget the specific password.",
            font=('Segoe UI', 10),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT,
            justify='left'
        ).pack(fill='x', pady=(0, 20))
        
        tk.Label(content, text="Master Password:", font=('Segoe UI', 10), bg=Colors.BG_DARK, fg=Colors.TEXT_DIM).pack(anchor='w')
        self.pw_entry = tk.Entry(content, show='●', font=('Segoe UI', 12), bg=Colors.BG_LIGHT, fg=Colors.TEXT, relief='flat', insertbackground=Colors.ACCENT)
        self.pw_entry.pack(fill='x', ipady=6, pady=(5, 15))
        
        tk.Label(content, text="Confirm Master Password:", font=('Segoe UI', 10), bg=Colors.BG_DARK, fg=Colors.TEXT_DIM).pack(anchor='w')
        self.cf_entry = tk.Entry(content, show='●', font=('Segoe UI', 12), bg=Colors.BG_LIGHT, fg=Colors.TEXT, relief='flat', insertbackground=Colors.ACCENT)
        self.cf_entry.pack(fill='x', ipady=6, pady=(5, 20))
        
        ModernButton(
            content, text="Save Master Key", font=('Segoe UI', 11, 'bold'),
            bg=Colors.SUCCESS, fg=Colors.BUTTON_TEXT, activebackground='#8bd5ca',
            command=self.save_key, pady=10
        ).pack(fill='x')
        
    def save_key(self):
        pw = self.pw_entry.get()
        cf = self.cf_entry.get()
        
        if len(pw) < 4:
            show_error("Error", "Password must be at least 4 characters", parent=self)
            return
        if pw != cf:
            show_error("Error", "Passwords do not match", parent=self)
            return
            
        self.locker.set_master_key(pw)
        show_info("Success", "Master Key saved successfully!", parent=self)
        self.destroy()
        
    def on_close(self):
        show_warning("Warning", "You must set a Master Key to continue.", parent=self)

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.locker = FolderLockCore()
        
        self.root.title("Folder Lock 3.0")
        try:
            icon_path = resource_path("app_icon.ico")
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error loading icon: {e}")

        self.root.geometry("800x600")
        self.root.configure(bg=Colors.BG_DARK)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.center_window()
        self._create_widgets()
        
        # Check Master Key
        self.root.after(100, self.check_master_key)
        self._refresh_list()
        
    def check_master_key(self):
        if not self.locker.master_key_hash:
            MasterKeySetup(self.root, self.locker)
        
    def center_window(self):
        self.root.update_idletasks()
        width = 800
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        # Sidebar
        sidebar = tk.Frame(self.root, bg=Colors.BG_MEDIUM, width=200)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Logo Area
        try:
            # Load and resize image
            from tkinter import PhotoImage
            # Using PIL for better resizing if available, otherwise fallback or direct load if PNG
            # Since standard tkinter PhotoImage supports PNG in newer python versions:
            img_path = resource_path("alpha kali exact.png")
            self.logo_img = tk.PhotoImage(file=img_path)
            # Resize if too big (subsample)
            # Assuming the image might be large, let's try to scale it down
            # A rough heuristic: if width > 150, subsample
            if self.logo_img.width() > 150:
                scale_factor = self.logo_img.width() // 150
                if scale_factor > 1:
                    self.logo_img = self.logo_img.subsample(scale_factor, scale_factor)
            
            tk.Label(
                sidebar, image=self.logo_img,
                bg=Colors.BG_MEDIUM
            ).pack(pady=(40, 10))
        except Exception as e:
            # Fallback if image fails
            print(f"Error loading logo: {e}")
            tk.Label(
                sidebar, text="🔒", font=('Segoe UI Emoji', 40),
                bg=Colors.BG_MEDIUM, fg=Colors.ACCENT
            ).pack(pady=(40, 10))
        
        tk.Label(
            sidebar, text="Alpha Folder Lock", font=('Segoe UI', 16, 'bold'),
            bg=Colors.BG_MEDIUM, fg=Colors.TEXT, justify='center'
        ).pack(pady=(0, 40))
        
        # Sidebar Buttons
        ModernButton(
            sidebar, text="+ Lock New Folder",
            bg=Colors.ACCENT, fg=Colors.BUTTON_TEXT,
            activebackground=Colors.ACCENT_HOVER,
            font=('Segoe UI', 10, 'bold'),
            command=self.lock_new_folder, pady=12
        ).pack(fill='x', padx=20, pady=10)
        
        ModernButton(
            sidebar, text="↻ Refresh List",
            bg=Colors.BG_LIGHT, fg=Colors.TEXT,
            activebackground=Colors.BG_DARK,
            font=('Segoe UI', 10),
            command=self._refresh_list, pady=12
        ).pack(fill='x', padx=20, pady=10)
        
        # Main Content
        main_area = tk.Frame(self.root, bg=Colors.BG_DARK)
        main_area.pack(side='left', fill='both', expand=True, padx=30, pady=30)
        
        # Header
        header = tk.Frame(main_area, bg=Colors.BG_DARK)
        header.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            header, text="Locked Folders", font=('Segoe UI', 20, 'bold'),
            bg=Colors.BG_DARK, fg=Colors.TEXT
        ).pack(side='left')
        
        self.count_label = tk.Label(
            header, text="0 Protected", font=('Segoe UI', 12),
            bg=Colors.BG_DARK, fg=Colors.TEXT_DIM
        )
        self.count_label.pack(side='right', pady=10)
        
        # Listbox container with custom styling
        list_container = tk.Frame(main_area, bg=Colors.BG_LIGHT)
        list_container.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(list_container, bg=Colors.BG_DARK)
        scrollbar.pack(side='right', fill='y')
        
        self.folder_list = tk.Listbox(
            list_container,
            font=('Segoe UI', 11),
            bg=Colors.BG_LIGHT,
            fg=Colors.TEXT,
            selectbackground=Colors.ACCENT,
            selectforeground=Colors.BUTTON_TEXT,
            relief='flat',
            borderwidth=0,
            yscrollcommand=scrollbar.set,
            highlightthickness=0,
            activestyle='none'
        )
        self.folder_list.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.config(command=self.folder_list.yview)
        
        self.folder_list.bind('<Double-Button-1>', self.unlock_selected_folder)
        self.folder_list.bind('<Return>', self.unlock_selected_folder)
        
        # Footer
        tk.Label(
            main_area, text="Double-click a folder to unlock it",
            font=('Segoe UI', 9), bg=Colors.BG_DARK, fg=Colors.TEXT_DIM
        ).pack(pady=(15, 0))

    def _refresh_list(self):
        self.folder_list.delete(0, tk.END)
        locks = self.locker.get_all_locks()
        
        for path_str, info in locks.items():
            name = info.get('name', Path(path_str).name)
            exists = Path(path_str).exists()
            status = "ACTIVE" if exists else "MISSING"
            
            # Use unicode icons for status
            icon = "🔒" if exists else "⚠️"
            display_text = f"{icon}  {name}  —  {path_str}"
            self.folder_list.insert(tk.END, display_text)
            
        self.count_label.config(text=f"{len(locks)} Protected")

    def lock_new_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            path = Path(folder_selected).resolve()
            
            # Check if already locked
            if str(path) in self.locker.locks:
                show_warning("Warning", "This folder is already locked!", parent=self.root)
                return
                
            LockDialog(self.root, str(path), self.locker)
            self._refresh_list()

    def unlock_selected_folder(self, event=None):
        selection = self.folder_list.curselection()
        if not selection:
            return
            
        index = selection[0]
        # Extract path from display text "🔒  Name  —  Path"
        item_text = self.folder_list.get(index)
        path_str = item_text.split("  —  ")[1]
        
        dialog = UnlockDialog(self.root, path_str, self.locker)
        self.root.wait_window(dialog)
        
        if dialog.result:
            self._refresh_list()
            # Ask to open folder
            if ask_yes_no("Open Folder", "Do you want to open the unlocked folder?", parent=self.root):
                webbrowser.open(path_str)

    def run(self):
        self.root.mainloop()

def main():
    app = MainApp()
    app.run()

if __name__ == "__main__":
    main()
