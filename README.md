# 🔒 Folder Lock - Permission Guardian v3.0

A cross-platform dark "hacker-style" CLI tool that locks folders using OS permissions with an additional password layer for security. Now with **Master Key** support and a modern **Rich** interface.

```
╔═══════════════════════════════════════════════════════════╗
║           FOLDER LOCK v3.0 - PERMISSION GUARDIAN          ║
║                   [SECURE • STEALTH • SIMPLE]             ║
╚═══════════════════════════════════════════════════════════╝
```

## ✨ New in v3.0

- 🔑 **Master Key Support**: Create a master key to unlock ANY folder if you forget the specific password.
- 🎨 **Rich UI**: Beautiful, modern terminal interface with colors, tables, and panels.
- ⚡ **Shared Core**: Improved reliability with a unified backend for CLI and GUI.

## 🚀 Features

- 🌐 **Cross-Platform**: Works on Windows, (Linux, and macOS) comming soon
- 🔐 **Double Security**: OS permissions + password protection
- 🔑 **Master Key**: Emergency access mechanism
- 💾 **Persistent Database**: Tracks all locked folders
- 🚀 **Interactive & CLI Modes**: Use interactively or via command line

## 📦 Installation

### Requirements
- Python 3.6+
- `rich` library (`pip install rich`)
- Administrator/sudo privileges (for permission changes)

### Setup

1. **Install dependencies**:
```bash
pip install rich
```

2. **Run the script**:
```bash
python folder_lock.py
```

## 📖 Usage

### Interactive Mode
Simply run without arguments. You will be prompted to set up a Master Key on first run.

```bash
python folder_lock.py
```

### Command Line Mode

**Lock a folder:**
```bash
python folder_lock.py lock /path/to/folder
# You'll be prompted for a password
```

**Unlock a folder:**
```bash
python folder_lock.py unlock /path/to/folder
# Enter your password OR the Master Key when prompted
```

**List all locked folders:**
```bash
python folder_lock.py list
```

## 🔑 Master Key

The **Master Key** is a single powerful password that can unlock ANY folder protected by this tool.
- **Setup**: You will be asked to create one when you first run the tool.
- **Usage**: When asked for a password to unlock a folder, you can enter EITHER the folder's specific password OR the Master Key.
- **Recovery**: Use this if you forget a specific folder's password.

## 🔧 How It Works

1. **OS Permissions Layer**:
   - **Windows**: Uses `icacls` to deny user access.
   - **Linux/Unix**: Sets folder permissions to `000` (no access).
   
2. **Password Layer**:
   - Passwords are hashed using SHA-256.
   - Stored in `~/.folder_lock/locks.json`.

## ⚠️ Important Notes

- **Keep your Master Key safe!** It is the only way to recover access if you forget passwords.
- **Run as Administrator/Sudo**: Permission changes require elevated privileges.
- **Not Encryption**: This tool hides and locks access, but does not encrypt files on disk.

## ⚖️ License

MIT License - feel free to use and modify as needed.
