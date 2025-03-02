from typing import List, Optional, Tuple
from .folder_manager import FolderManager
from .config import ConfigManager

class Project:
    """Represents an Obsidian project with its folder structure."""
    
    def __init__(self, alias: str, config_manager: ConfigManager):
        self.alias = alias
        self.config_manager = config_manager
        config = config_manager.get_project(alias)
        if not config:
            raise ValueError(f"Project {alias} not found")
        self.folder_manager = FolderManager(
            config["parent_dir"],
            config["finished_folder"],
            config["current_folder"]
        )

    def add(self, path: str) -> Tuple[bool, Optional[str]]:
        """Add a new folder structure to Current."""
        return self.folder_manager.add_folder(path, self.folder_manager.current_folder)

    def finish(self, path: str) -> Tuple[bool, Optional[str]]:
        """Move folder from Current to Finished."""
        return self.folder_manager.move_folder(
            path,
            self.folder_manager.current_folder,
            self.folder_manager.finished_folder
        )

    def continue_(self, path: str) -> Tuple[bool, Optional[str]]:
        """Move folder from Finished to Current."""
        return self.folder_manager.move_folder(
            path,
            self.folder_manager.finished_folder,
            self.folder_manager.current_folder
        )
        
    def sync(self) -> Tuple[bool, List[str]]:
        """Sync project structure, fix indices, and check for conflicts."""
        return self.folder_manager.sync()
        
    def change_index(self, path: str, new_index: int) -> Tuple[bool, Optional[str]]:
        """Change the index of a folder within its parent directory."""
        return self.folder_manager.change_index(path, new_index)
