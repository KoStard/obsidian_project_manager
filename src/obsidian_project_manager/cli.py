import argparse
from typing import List
from .config import ConfigManager
from .project import Project

def configure_parser(parser: argparse.ArgumentParser) -> None:
    """Configure CLI parser with subcommands."""
    subparsers = parser.add_subparsers(dest="command")
    
    # Configure command
    config_parser = subparsers.add_parser("configure")
    config_subparsers = config_parser.add_subparsers(dest="subcommand")
    
    projects_parser = config_subparsers.add_parser("projects")
    projects_subparsers = projects_parser.add_subparsers(dest="action")
    
    projects_subparsers.add_parser("list")
    add_parser = projects_subparsers.add_parser("add")
    delete_parser = projects_subparsers.add_parser("delete")
    delete_parser.add_argument("alias")

    # Project commands
    project_parser = subparsers.add_parser("project")
    project_parser.add_argument("project")
    project_subparsers = project_parser.add_subparsers(dest="action")
    
    add_parser = project_subparsers.add_parser("add")
    add_parser.add_argument("path")
    
    finish_parser = project_subparsers.add_parser("finish")
    finish_parser.add_argument("path")
    
    continue_parser = project_subparsers.add_parser("continue")
    continue_parser.add_argument("path")
    
    sync_parser = project_subparsers.add_parser("sync")

def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Obsidian Project Manager")
    configure_parser(parser)
    args = parser.parse_args()
    
    config_manager = ConfigManager()
    
    if args.command == "configure" and args.subcommand == "projects":
        if args.action == "list":
            projects = config_manager.list_projects()
            for alias, config in projects.items():
                print(f"{alias}: {config['parent_dir']}")
        
        elif args.action == "add":
            alias = input("Project alias: ")
            parent_dir = input("Parent directory: ")
            finished = input("Finished folder name [1 - Finished]: ") or "1 - Finished"
            current = input("Current folder name [2 - Current]: ") or "2 - Current"
            config_manager.add_project(alias, parent_dir, finished, current)
            print(f"Added project {alias}")
        
        elif args.action == "delete":
            if config_manager.delete_project(args.alias):
                print(f"Deleted project {args.alias}")
            else:
                print(f"Project {args.alias} not found")
    
    elif args.command == "project":
        try:
            project_alias = args.project.split()[0]
            project = Project(project_alias, config_manager)
            if args.action.startswith("add"):
                success, error = project.add(args.path)
                print(error if error else f"Added {args.path}")
            elif args.action.startswith("finish"):
                success, error = project.finish(args.path)
                print(error if error else f"Finished {args.path}")
            elif args.action.startswith("continue"):
                success, error = project.continue_(args.path)
                print(error if error else f"Continued {args.path}")
            elif args.action == "sync":
                success, warnings = project.sync()
                if warnings:
                    print("Warnings found during sync:")
                    for warning in warnings:
                        print(f"- {warning}")
                else:
                    print("Project structure synced successfully")
        except ValueError as e:
            print(str(e))

if __name__ == "__main__":
    main()
