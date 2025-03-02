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
        if success:
            # Create Entry.md file in the leaf folder
            entry_file = target_path / "Entry.md"
            try:
                with open(entry_file, "w") as f:
                    f.write(f"# {folders[-1]}\n\nEntry file for {'/'.join(folders)}")
                return True, None
            except Exception as e:
                return False, f"Created folder but failed to create Entry.md: {str(e)}"
        return False, f"Failed to create folder {target_path}"
    
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
            
        # Check and remove empty parent folders, but protect important folders
        protected_paths = [self.parent_dir, self.finished_folder, self.current_folder]
        self.file_manager.remove_empty_folders(source_path.parent, protected_paths)
            
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
    
    def change_index(self, path: str, new_index: int) -> Tuple[bool, Optional[str]]:
        """Change the index of a folder within its parent directory."""
        folders = self._normalize_path(path)
        if not folders:
            return False, "Invalid path"
            
        # Get parent folder and target folder
        parent_path = self._build_indexed_path(self.parent_dir, folders[:-1])
        target_name = folders[-1]
        
        # Get all folders in parent
        folders_in_parent = []
        for item in parent_path.iterdir():
            if item.is_dir():
                name = self.file_manager.strip_index(item.name)
                current_index = int(item.name.split(" - ")[0])
                folders_in_parent.append((name, item, current_index))
                
        folder_count = len(folders_in_parent)
        
        # Validate new index
        if new_index < 1 or new_index > folder_count:
            return False, f"Index must be between 1 and {folder_count}"
            
        # Find the target folder
        target_folder = None
        target_current_index = None
        for name, path, idx in folders_in_parent:
            if name == target_name:
                target_folder = path
                target_current_index = idx
                break
                
        if not target_folder:
            return False, f"Folder {target_name} not found in {parent_path}"
            
        # If index isn't changing, nothing to do
        if target_current_index == new_index:
            return True, None
            
        # Sort folders by their current indices
        folders_in_parent.sort(key=lambda x: x[2])
        
        # Remove target from the list
        folders_in_parent = [(name, path, idx) for name, path, idx in folders_in_parent 
                            if name != target_name]
        
        # Insert target at the new position
        folders_in_parent.insert(new_index - 1, (target_name, target_folder, target_current_index))
        
        # Rename all folders with new indices
        for i, (name, path, _) in enumerate(folders_in_parent, 1):
            new_name = self.file_manager.add_index(name, i)
            if path.name != new_name:
                path.rename(parent_path / new_name)
                
        return True, None
    
    def sync(self) -> Tuple[bool, List[str]]:
        """Sync project structure, fix indices, and check for conflicts."""
        warnings = []
        
        # Check for path+filename conflicts between finished and current
        finished_files = self._get_all_files(self.finished_folder)
        current_files = self._get_all_files(self.current_folder)
        
        # Check for conflicts between finished and current
        for path, files in finished_files.items():
            if path in current_files:
                for file in files:
                    if file in current_files[path]:
                        warnings.append(f"File conflict between finished and current: {path}/{file}")
        
        # Check for folder name conflicts within each state
        finished_conflicts = self._check_folder_conflicts(self.finished_folder)
        current_conflicts = self._check_folder_conflicts(self.current_folder)
        warnings.extend(finished_conflicts)
        warnings.extend(current_conflicts)
        
        # Fix indices in both states
        self._fix_indices_recursive(self.finished_folder)
        self._fix_indices_recursive(self.current_folder)
        
        return len(warnings) == 0, warnings
    
    def _get_all_files(self, base_path: Path) -> Dict[str, List[str]]:
        """Get all files in the project with their normalized paths."""
        result = {}
        if not base_path.exists():
            return result
            
        def process_dir(path: Path, current_path: str = ""):
            for item in path.iterdir():
                name = self.file_manager.strip_index(item.name)
                if item.is_dir():
                    new_path = f"{current_path}/{name}" if current_path else name
                    process_dir(item, new_path)
                else:
                    if current_path not in result:
                        result[current_path] = []
                    result[current_path].append(name)
                    
        process_dir(base_path)
        return result
    
    def _check_folder_conflicts(self, base_path: Path) -> List[str]:
        """Check for folder name conflicts within a project state."""
        conflicts = []
        if not base_path.exists():
            return conflicts
            
        def check_dir(path: Path):
            folder_names = {}
            file_names = {}
            
            for item in path.iterdir():
                name = self.file_manager.strip_index(item.name)
                
                if item.is_dir():
                    if name in folder_names:
                        conflicts.append(f"Folder name conflict in {path}: {name}")
                    folder_names[name] = True
                    check_dir(item)  # Recursively check subdirectories
                else:
                    if name in file_names:
                        conflicts.append(f"File name conflict in {path}: {name}")
                    file_names[name] = True
                    
        check_dir(base_path)
        return conflicts
    
    def _fix_indices_recursive(self, path: Path) -> None:
        """Recursively fix indices in all folders."""
        if not path.exists():
            return
            
        # Fix indices in current directory
        self._reindex_folders(path)
        
        # Recursively fix indices in subdirectories
        for item in path.iterdir():
            if item.is_dir():
                self._fix_indices_recursive(item)
