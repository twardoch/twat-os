#!/usr/bin/env python3
"""Command-line interface for twat-os."""

import sys
from pathlib import Path
from typing import Optional

import fire
from rich.console import Console
from rich.table import Table

from twat_os.paths import PathManager

console = Console()


class TwatOSCLI:
    """Command-line interface for twat-os path management."""

    def __init__(self) -> None:
        """Initialize the CLI."""
        self.console = console

    def paths(
        self,
        package: Optional[str] = None,
        config: Optional[str] = None,
        create: bool = True,
    ) -> None:
        """Display all configured paths.
        
        Args:
            package: Package name for package-specific paths
            config: Path to custom configuration file
            create: Whether to create directories if they don't exist
        """
        try:
            manager = PathManager(
                package_name=package,
                config_file=config,
                create_dirs=create,
            )
            
            table = Table(title="Twat-OS Path Configuration")
            table.add_column("Category", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Path", style="green")
            table.add_column("Exists", style="red")
            
            # Add base paths
            categories = [
                ("cache", manager.cache),
                ("config", manager.config_dir),
                ("data", manager.data),
                ("temp", manager.temp),
                ("logs", manager.logs),
            ]
            
            for category, config_obj in categories:
                table.add_row(
                    category,
                    "base_dir",
                    str(config_obj.base_dir),
                    "✓" if config_obj.base_dir.exists() else "✗",
                )
                
                if config_obj.package_dir:
                    table.add_row(
                        "",
                        "package_dir",
                        str(config_obj.package_dir),
                        "✓" if config_obj.package_dir.exists() else "✗",
                    )
            
            # Add GenAI paths
            table.add_row(
                "genai",
                "base_dir",
                str(manager.genai.base_dir),
                "✓" if manager.genai.base_dir.exists() else "✗",
            )
            table.add_row(
                "",
                "lora_dir",
                str(manager.genai.lora_dir),
                "✓" if manager.genai.lora_dir.exists() else "✗",
            )
            table.add_row(
                "",
                "model_dir",
                str(manager.genai.model_dir),
                "✓" if manager.genai.model_dir.exists() else "✗",
            )
            table.add_row(
                "",
                "output_dir",
                str(manager.genai.output_dir),
                "✓" if manager.genai.output_dir.exists() else "✗",
            )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    def get(
        self,
        category: str,
        key: str = "base_dir",
        package: Optional[str] = None,
        config: Optional[str] = None,
        create: bool = True,
    ) -> None:
        """Get a specific path.
        
        Args:
            category: Path category (cache, config, data, temp, genai, logs)
            key: Path key within the category (base_dir, package_dir, etc.)
            package: Package name for package-specific paths
            config: Path to custom configuration file
            create: Whether to create directories if they don't exist
        """
        try:
            manager = PathManager(
                package_name=package,
                config_file=config,
                create_dirs=create,
            )
            
            path = manager.get_path(category, key)
            self.console.print(str(path))
            
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    def create(
        self,
        category: str,
        key: str = "base_dir",
        package: Optional[str] = None,
        config: Optional[str] = None,
    ) -> None:
        """Create a specific directory.
        
        Args:
            category: Path category (cache, config, data, temp, genai, logs)
            key: Path key within the category (base_dir, package_dir, etc.)
            package: Package name for package-specific paths
            config: Path to custom configuration file
        """
        try:
            manager = PathManager(
                package_name=package,
                config_file=config,
                create_dirs=False,
            )
            
            path = manager.get_path(category, key)
            path.mkdir(parents=True, exist_ok=True)
            
            self.console.print(f"[green]Created: {path}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    def clean(
        self,
        category: str,
        key: str = "base_dir",
        package: Optional[str] = None,
        config: Optional[str] = None,
        force: bool = False,
    ) -> None:
        """Clean (remove) a specific directory.
        
        Args:
            category: Path category (cache, config, data, temp, genai, logs)
            key: Path key within the category (base_dir, package_dir, etc.)
            package: Package name for package-specific paths
            config: Path to custom configuration file
            force: Skip confirmation prompt
        """
        try:
            manager = PathManager(
                package_name=package,
                config_file=config,
                create_dirs=False,
            )
            
            path = manager.get_path(category, key)
            
            if not path.exists():
                self.console.print(f"[yellow]Path does not exist: {path}[/yellow]")
                return
            
            if not force:
                response = input(f"Remove {path}? (y/N): ")
                if response.lower() != "y":
                    self.console.print("[yellow]Cancelled[/yellow]")
                    return
            
            import shutil
            shutil.rmtree(path)
            self.console.print(f"[green]Removed: {path}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    def info(self, package: Optional[str] = None) -> None:
        """Display information about the current configuration.
        
        Args:
            package: Package name for package-specific information
        """
        try:
            manager = PathManager(package_name=package, create_dirs=False)
            
            self.console.print(f"[cyan]Twat-OS Path Manager[/cyan]")
            self.console.print(f"Package: {package or 'None'}")
            self.console.print(f"Configuration: Default")
            self.console.print(f"Directory Creation: Disabled")
            self.console.print()
            
            # Show summary statistics
            total_paths = 0
            existing_paths = 0
            
            for category in ["cache", "config_dir", "data", "temp", "logs"]:
                config_obj = getattr(manager, category)
                total_paths += 1
                if config_obj.base_dir.exists():
                    existing_paths += 1
                
                if config_obj.package_dir:
                    total_paths += 1
                    if config_obj.package_dir.exists():
                        existing_paths += 1
            
            # GenAI paths
            genai_paths = ["base_dir", "lora_dir", "model_dir", "output_dir"]
            for path_attr in genai_paths:
                total_paths += 1
                path = getattr(manager.genai, path_attr)
                if path.exists():
                    existing_paths += 1
            
            self.console.print(f"Total paths: {total_paths}")
            self.console.print(f"Existing paths: {existing_paths}")
            self.console.print(f"Missing paths: {total_paths - existing_paths}")
            
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    def version(self) -> None:
        """Display version information."""
        try:
            import twat_os
            self.console.print(f"twat-os version: {twat_os.__version__}")
        except Exception as e:
            self.console.print(f"[red]Error getting version: {e}[/red]")
            sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    fire.Fire(TwatOSCLI)


if __name__ == "__main__":
    main()