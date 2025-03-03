import json
from pathlib import Path
from typing import Dict, Optional

class ConfigManager:
    """Manages configuration for Obsidian projects."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "obsidian_project_manager"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file or create default."""
        if not self.config_file.exists():
            self.config = {"projects": {}}
            self._save_config()
        else:
            with open(self.config_file, "r") as f:
                self.config = json.load(f)

    def _save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_project(self, alias: str) -> Optional[dict]:
        """Get project configuration by alias."""
        return self.config["projects"].get(alias)

    def list_projects(self) -> Dict[str, dict]:
        """List all configured projects."""
        return self.config["projects"]

    def add_project(self, alias: str, parent_dir: str, 
                   finished_folder: str = "1 - Finished", 
                   current_folder: str = "2 - Current") -> None:
        """Add a new project to configuration."""
        self.config["projects"][alias] = {
            "parent_dir": parent_dir,
            "finished_folder": finished_folder,
            "current_folder": current_folder
        }
        self._save_config()

    def delete_project(self, alias: str) -> bool:
        """Delete a project from configuration."""
        if alias in self.config["projects"]:
            del self.config["projects"][alias]
            self._save_config()
            return True
        return False