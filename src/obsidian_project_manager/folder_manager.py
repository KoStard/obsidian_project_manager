from pathlib import Path
from typing import List, Tuple, Optional, Dict
from .file_manager import FileManager

class FolderManager:
    """Manages folder structure and operations for Obsidian projects."""
    
    def __init__(self, parent_dir: str, finished_folder: str, current_folder: str):
        self.parent_dir = Path(parent_dir)
        self.finished_folder = Path(parent_dir) / finished_folder
        self.current_folder = Path(parent_dir) / current_folder
        self.file_manager = FileManager()
        
        # Ensure base folders exist
        self.file_manager.create_folder(self.finished_folder)
        self.file_manager.create_folder(self.current_folder)
    
    def _normalize_path(self, path: str) -> List[str]:
        """Convert user-provided path to list of folder names without indices."""
        return [self.file_manager.strip_index(part) for part in path.split("/")]
    
    def _build_indexed_path(self, base: Path, folders: List[str]) -> Path:
        """Build a path with proper indices."""
        current = base
        for i, folder in enumerate(folders, 1):
            structure = self.file_manager.get_folder_structure(current)
            if folder not in structure["folders"]:
                current = current / self.file_manager.add_index(folder, len(structure["folders"]) + 1)
            else:
                for item in current.iterdir():
                    if self.file_manager.strip_index(item.name) == folder:
                        current = item
                        break
        return current
    
    def add_folder(self, path: str, base_folder: Path) -> Tuple[bool, Optional[str]]:
        """Add a new folder structure."""
        folders = self._normalize_path(path)
        target_path = self._build_indexed_path(base_folder, folders)
        
        success = self.file_manager.create_folder(target_path)
        return success, None if success else f"Failed to create folder {target_path}"
    
    def move_folder(self, path: str, source_base: Path, dest_base: Path) -> Tuple[bool, Optional[str]]:
        """Move folder between project states with merging."""
        folders = self._normalize_path(path)
        
        # Find source path
        source_path = self._build_indexed_path(source_base, folders)
        if not source_path.exists():
            return False, f"Path {path} not found in source"
            
        # Build destination path with new indices
        dest_path = self._build_indexed_path(dest_base, folders)
        
        # Dry run to check conflicts
        dest_structure = self.file_manager.get_folder_structure(dest_path.parent)
        source_structure = self.file_manager.get_folder_structure(source_path)
        conflicts = self.file_manager.check_conflicts(dest_path.parent, source_structure)
        
        if conflicts:
            return False, f"Conflicts found: {'; '.join(conflicts)}"
            
        # Perform the move
        success, error = self.file_manager.move_path(source_path, dest_path)
        if not success:
            return False, error
            
        # Re-index remaining folders in source
        self._reindex_folders(source_path.parent)
        self._reindex_folders(dest_path.parent)
        
        return True, None
    
    def _reindex_folders(self, folder: Path) -> None:
        """Re-index all folders in a directory."""
        if not folder.exists():
            return
            
        folders = [(self.file_manager.strip_index(item.name), item) 
                  for item in folder.iterdir() if item.is_dir()]
        folders.sort()  # Sort by name without indices
        
        for i, (name, path) in enumerate(folders, 1):
            new_name = self.file_manager.add_index(name, i)
            if path.name != new_name:
                path.rename(folder / new_name)