# 🔒 Folder Lock GUI v3.0 - Modern Protection

A beautiful, cross-platform graphical application that locks folders with password protection. Now featuring a **Master Key** and a modern dark theme.

![Version](https://img.shields.io/badge/version-3.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)

## ✨ New in v3.0

- 🔑 **Master Key System**: Set up a master password to unlock ANY folder. Never get locked out again!
- 🎨 **Modern Dark UI**: A completely refreshed, professional dark interface.
- 🔄 **Unified Core**: Powered by the new `FolderLockCore` for better stability.

## 🚀 Core Features

- **🖱️ Click to Unlock**: Double-click any locked folder to get a password prompt.
- **🔐 Dual Auth**: Unlock with the specific folder password OR the Master Key.
- **📊 Dashboard**: View all protected folders, their status, and paths.
- **⚡ Instant Action**: Lock and unlock folders instantly without encryption delays.

## 📖 Quick Start

### 1. Launch
Run the application (ensure you have Python installed):
```bash
python folder_lock_gui_v2.py
```

### 2. Setup Master Key
On first launch, you will be prompted to create a **Master Key**. 
> **Important**: This key can unlock ALL folders. Remember it well!

### 3. Lock a Folder
1. Click **+ Lock New Folder**.
2. Select the directory you want to protect.
3. Set a specific password for this folder.

### 4. Unlock a Folder
1. Double-click the folder in the list.
2. Enter the folder's password **OR** your Master Key.
3. The folder opens automatically!

## 📸 Interface

The new interface features a modern sidebar layout, clear status indicators, and a clean dark theme designed for ease of use.

- **Active Locks**: Shown with a 🔒 icon.
- **Missing Folders**: Shown with a ⚠️ icon (if the folder was moved or deleted externally).

## ⚠️ Security Note

This tool uses **OS-level permissions** to secure folders.
- **Windows**: Denies access via ACLs.
- **Linux/Mac**: Removes read/write/execute permissions.

It prevents unauthorized access from standard users but does **not** encrypt the data on disk. For military-grade security, use full-disk encryption.

## 🤝 Contributing

Feel free to submit issues or pull requests to improve the tool!
