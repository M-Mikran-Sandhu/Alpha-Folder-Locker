#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════╗
║           ALPHA FOLDER LOCK v2.0 - PERMISSION GUARDIAN    ║
║                   [SECURE • STEALTH • SIMPLE]             ║
╚═══════════════════════════════════════════════════════════╝

Cross-platform folder locking using OS permissions + password
"""

import sys
import getpass
import msvcrt
from pathlib import Path
from folder_lock_core import FolderLockCore
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.layout import Layout
from rich.align import Align
from rich import print as rprint

console = Console()

class FolderLockCLI:
    def __init__(self):
        self.core = FolderLockCore()
        self.check_master_key()

    def get_password_input(self, prompt_text):
        """Custom password input that shows asterisks"""
        console.print(prompt_text, end=": ")
        sys.stdout.flush()
        
        if sys.platform != 'win32':
             # Fallback for non-windows
             return getpass.getpass("")
             
        password = ""
        while True:
            ch = msvcrt.getch()
            if ch == b'\r' or ch == b'\n':
                print('')
                return password
            elif ch == b'\x08': # Backspace
                if len(password) > 0:
                    password = password[:-1]
                    # Erase character from screen
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif ch == b'\x03': # Ctrl+C
                raise KeyboardInterrupt
            else:
                try:
                    char = ch.decode('utf-8')
                    password += char
                    sys.stdout.write('*')
                    sys.stdout.flush()
                except:
                    pass

    def check_master_key(self):
        """Check if master key is set, if not prompt to set it"""
        if not self.core.master_key_hash:
            console.print(Panel("[bold red]⚠️  MASTER KEY NOT DETECTED[/bold red]\n\nA Master Key is required to recover access to folders if you forget their specific passwords.", title="Setup Required", border_style="red"))
            
            while True:
                password = self.get_password_input("[bold cyan]Create Master Key[/bold cyan]")
                confirm = self.get_password_input("[bold cyan]Confirm Master Key[/bold cyan]")
                
                if password != confirm:
                    console.print("[bold red]Passwords do not match! Try again.[/bold red]")
                    continue
                
                if len(password) < 4:
                    console.print("[bold red]Password must be at least 4 characters![/bold red]")
                    continue
                
                self.core.set_master_key(password)
                console.print("[bold green]✓ Master Key set successfully![/bold green]")
                break
                
    def print_banner(self):
        banner_text = """
    █████╗ ██╗     ██████╗ ██╗  ██╗ █████╗ 
   ██╔══██╗██║     ██╔══██╗██║  ██║██╔══██╗
   ███████║██║     ██████╔╝███████║███████║
   ██╔══██║██║     ██╔═══╝ ██╔══██║██╔══██║
   ██║  ██║███████╗██║     ██║  ██║██║  ██║
   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝
                                           
    ███████╗ ██████╗ ██╗     ██████╗ ███████╗██████╗     ██╗      ██████╗  ██████╗██╗  ██╗
    ██╔════╝██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗    ██║     ██╔═══██╗██╔════╝██║ ██╔╝
    █████╗  ██║   ██║██║     ██║  ██║█████╗  ██████╔╝    ██║     ██║   ██║██║     █████╔╝ 
    ██╔══╝  ██║   ██║██║     ██║  ██║██╔══╝  ██╔══██╗    ██║     ██║   ██║██║     ██╔═██╗ 
    ██║     ╚██████╔╝███████╗██████╔╝███████╗██║  ██║    ███████╗╚██████╔╝╚██████╗██║  ██╗
    ╚═╝      ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝
        """
        console.print(Panel(Align.center(banner_text, vertical="middle"), style="bold cyan", title="ALPHA v1.0"))

    def list_locks(self):
        locks = self.core.get_all_locks()
        
        if not locks:
            console.print(Panel("[dim]No folders are currently locked.[/dim]", title="Locked Folders", border_style="blue"))
            return

        table = Table(title="Locked Folders", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Folder Name", style="bold cyan")
        table.add_column("Path", style="white")
        table.add_column("Status", justify="center")

        for idx, (path_str, info) in enumerate(locks.items(), 1):
            path = Path(path_str)
            exists = path.exists()
            status = "[bold green]ACTIVE[/bold green]" if exists else "[bold red]MISSING[/bold red]"
            name = info.get('name', path.name)
            table.add_row(str(idx), name, path_str, status)

        console.print(table)

    def lock_folder_interactive(self):
        folder = Prompt.ask("[bold cyan]Enter folder path to lock[/bold cyan]")
        folder_path = Path(folder).resolve()
        
        if not folder_path.exists():
            console.print(f"[bold red]Error: Folder '{folder}' does not exist.[/bold red]")
            return

        password = self.get_password_input("[bold cyan]Enter password for this folder[/bold cyan]")
        confirm = self.get_password_input("[bold cyan]Confirm password[/bold cyan]")
        
        if password != confirm:
            console.print("[bold red]Error: Passwords do not match![/bold red]")
            return
            
        if len(password) < 4:
            console.print("[bold red]Error: Password must be at least 4 characters![/bold red]")
            return

        with console.status("[bold green]Locking folder...[/bold green]"):
            success, message = self.core.lock_folder(str(folder_path), password)
            
        if success:
            console.print(Panel(f"[bold green]✓ {message}[/bold green]\n\nPath: {folder_path}", title="Success", border_style="green"))
        else:
            console.print(f"[bold red]✗ {message}[/bold red]")

    def unlock_folder_interactive(self):
        folder = Prompt.ask("[bold cyan]Enter folder path to unlock[/bold cyan]")
        
        password = self.get_password_input("[bold cyan]Enter password (or Master Key)[/bold cyan]")
        
        with console.status("[bold green]Unlocking folder...[/bold green]"):
            success, message = self.core.unlock_folder(folder, password)
            
        if success:
            console.print(Panel(f"[bold green]✓ {message}[/bold green]", title="Success", border_style="green"))
        else:
            console.print(f"[bold red]✗ {message}[/bold red]")

    def interactive_mode(self):
        self.print_banner()
        
        while True:
            console.print("\n[bold cyan]Main Menu[/bold cyan]")
            console.print("1. [green]Lock a folder[/green]")
            console.print("2. [yellow]Unlock a folder[/yellow]")
            console.print("3. [blue]List locked folders[/blue]")
            console.print("4. [red]Exit[/red]")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="3")
            
            if choice == '1':
                self.lock_folder_interactive()
            elif choice == '2':
                self.unlock_folder_interactive()
            elif choice == '3':
                self.list_locks()
            elif choice == '4':
                console.print("[bold cyan]Stay secure! 👋[/bold cyan]")
                break

def main():
    cli = FolderLockCLI()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'lock' and len(sys.argv) >= 3:
            folder = sys.argv[2]
            password = getpass.getpass("Enter password: ")
            confirm = getpass.getpass("Confirm password: ")
            
            if password != confirm:
                console.print("[bold red]Passwords do not match![/bold red]")
                sys.exit(1)
                
            success, message = cli.core.lock_folder(folder, password)
            if success:
                console.print(f"[bold green]✓ {message}[/bold green]")
            else:
                console.print(f"[bold red]✗ {message}[/bold red]")
                
        elif command == 'unlock' and len(sys.argv) >= 3:
            folder = sys.argv[2]
            password = getpass.getpass("Enter password (or Master Key): ")
            success, message = cli.core.unlock_folder(folder, password)
            if success:
                console.print(f"[bold green]✓ {message}[/bold green]")
            else:
                console.print(f"[bold red]✗ {message}[/bold red]")
                
        elif command == 'list':
            cli.list_locks()
            
        else:
            console.print(Panel("""
Usage:
  python folder_lock.py              # Interactive mode
  python folder_lock.py lock <path>  # Lock a folder
  python folder_lock.py unlock <path> # Unlock a folder
  python folder_lock.py list         # List locked folders
""", title="Help"))
    else:
        cli.interactive_mode()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation cancelled by user[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]CRITICAL ERROR: {e}[/bold red]")
        sys.exit(1)
