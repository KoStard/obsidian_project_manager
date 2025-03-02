from pathlib import Path
from typing import List, Tuple, Optional, Dict
import os
import shutil
import re

class FileManager:
    """Handles low-level file system operations and index management."""
    
    INDEX_PATTERN = r"^\d+\s*-\s*"
    
    @staticmethod
    def strip_index(name: str) -> str:
        """Remove index prefix from a name if it exists.
        
        Args:
            name: The name with potential index prefix
            
        Returns:
            The name without the index prefix
        """
        match = re.match(r'^\d+\s*-\s*(.*)', name)
        return match.group(1) if match else name
    
    @staticmethod
    def add_index(name: str, index: int) -> str:
        """Add index prefix to a name."""
        return f"{index} - {name}"
    
    @staticmethod
    def get_folder_structure(base_path: Path) -> Dict[str, List[str]]:
        """Recursively get folder structure without indices."""
        structure = {"folders": [], "files": []}
        if not base_path.exists():
            return structure
            
        for item in base_path.iterdir():
            name = FileManager.strip_index(item.name)
            if item.is_dir():
                structure["folders"].append(name)
            else:
                structure["files"].append(name)
        return structure
    
    @staticmethod
    def create_folder(path: Path) -> bool:
        """Create a folder if it doesn't exist."""
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except OSError:
            return False
    
    @staticmethod
    def move_path(source: Path, dest: Path, dry_run: bool = False) -> Tuple[bool, Optional[str]]:
        """Move a path with conflict checking."""
        if not source.exists():
            return False, f"Source path {source} does not exist"
            
        if dest.exists():
            if source.is_dir() and dest.is_dir():
                # Merge directories
                if not dry_run:
                    for item in source.iterdir():
                        shutil.move(str(item), str(dest))
                    shutil.rmtree(str(source))
                return True, None
            return False, f"Destination {dest} already exists"
            
        if not dry_run:
            shutil.move(str(source), str(dest))
        return True, None
    
    @staticmethod
    def remove_empty_folders(path: Path, protected_paths: List[Path] = None) -> bool:
        """Recursively remove empty folders, going up the tree."""
        if not path.exists() or not path.is_dir():
            return False
            
        # Don't delete protected folders
        if protected_paths and any(path.samefile(p) for p in protected_paths if p.exists()):
            return False
            
        # Check if folder is empty
        if any(path.iterdir()):
            return False
            
        # Remove the empty folder
        try:
            path.rmdir()
            # Try to remove parent if it's now empty
            parent = path.parent
            FileManager.remove_empty_folders(parent, protected_paths)
            return True
        except OSError:
            return False
    
    @staticmethod
    def check_conflicts(path: Path, structure: Dict[str, List[str]]) -> List[str]:
        """Check for file/folder conflicts."""
        conflicts = []
        seen_files = set()
        seen_folders = set()
        
        for folder in structure["folders"]:
            if folder in seen_folders:
                conflicts.append(f"Duplicate folder: {folder}")
            seen_folders.add(folder)
            
        for file in structure["files"]:
            if file in seen_files:
                conflicts.append(f"Duplicate file: {file}")
            seen_files.add(file)
            
        return conflicts
