# HyperLang Tools
# Copyleft 🄯 2026 HyperLang Technologies

import shutil
from pathlib import Path

def clean_pycache():
    # Gets the directory where this script is located (HyperLang/tools)
    script_dir = Path(__file__).resolve().parent
    
    # Gets the parent directory (HyperLang)
    root_dir = script_dir.parent
    
    print(f"Scanning for __pycache__ folders in: {root_dir}\n")
    
    deleted_count = 0
    
    # rglob recursively searches for all folders named '__pycache__'
    for pycache_dir in root_dir.rglob('__pycache__'):
        if pycache_dir.is_dir():
            try:
                # shutil.rmtree completely deletes a directory and all its contents
                shutil.rmtree(pycache_dir)
                print(f"Deleted: {pycache_dir}")
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {pycache_dir}: {e}")
                
    print(f"\nCleanup complete! Successfully deleted {deleted_count} __pycache__ folder(s).")

if __name__ == "__main__":
    clean_pycache()