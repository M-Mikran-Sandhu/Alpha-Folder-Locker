#!/usr/bin/env python3
"""
Quick launcher for Folder Lock GUI
Double-click this file to start the application
"""

import sys
import os
from pathlib import Path

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Path to the main GUI application
    gui_script = script_dir / "folder_lock_gui_v2.py"
    
    if not gui_script.exists():
        print("Error: Could not find folder_lock_gui_v2.py")
        print(f"Looking in: {script_dir}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Run the GUI application
    print("Starting Folder Lock GUI...")
    print("Please wait...")
    
    # Import and run the main application
    sys.path.insert(0, str(script_dir))
    
    try:
        import folder_lock_gui_v2
        folder_lock_gui_v2.main()
    except ImportError as e:
        print(f"Error importing application: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"Error running application: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
