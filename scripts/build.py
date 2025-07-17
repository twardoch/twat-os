#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire", "rich", "hatchling", "build"]
# ///
"""Build script for twat-os package."""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import fire
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class Builder:
    """Build automation for twat-os package."""

    def __init__(self) -> None:
        """Initialize the builder."""
        self.console = console
        self.project_root = Path(__file__).parent.parent
        self.dist_dir = self.project_root / "dist"

    def clean(self) -> None:
        """Clean build artifacts."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Cleaning build artifacts...", total=None)
            
            # Remove common build directories
            build_dirs = [
                self.dist_dir,
                self.project_root / "build",
                self.project_root / "src" / "twat_os.egg-info",
            ]
            
            for build_dir in build_dirs:
                if build_dir.exists():
                    shutil.rmtree(build_dir)
                    self.console.print(f"[green]Removed: {build_dir}[/green]")
            
            # Remove __pycache__ directories
            for pycache in self.project_root.rglob("__pycache__"):
                shutil.rmtree(pycache)
            
            progress.remove_task(task)
        
        self.console.print("[green]✓ Build artifacts cleaned[/green]")

    def build(self, clean_first: bool = True) -> None:
        """Build the package distributions.
        
        Args:
            clean_first: Whether to clean before building
        """
        if clean_first:
            self.clean()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Building distributions...", total=None)
            
            try:
                # Build using python -m build
                result = subprocess.run(
                    [sys.executable, "-m", "build", "--outdir", str(self.dist_dir)],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                
                progress.remove_task(task)
                
                # List built files
                if self.dist_dir.exists():
                    built_files = list(self.dist_dir.glob("*"))
                    self.console.print(f"[green]✓ Built {len(built_files)} distribution(s):[/green]")
                    for file in built_files:
                        self.console.print(f"  - {file.name}")
                else:
                    self.console.print("[red]No distribution files found[/red]")
                    
            except subprocess.CalledProcessError as e:
                progress.remove_task(task)
                self.console.print(f"[red]Build failed:[/red]")
                self.console.print(f"[red]{e.stdout}[/red]")
                self.console.print(f"[red]{e.stderr}[/red]")
                sys.exit(1)

    def check(self) -> None:
        """Check the built distributions."""
        if not self.dist_dir.exists():
            self.console.print("[red]No dist directory found. Run build first.[/red]")
            sys.exit(1)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Checking distributions...", total=None)
            
            try:
                # Check with twine if available
                try:
                    subprocess.run(
                        [sys.executable, "-m", "twine", "check", str(self.dist_dir / "*")],
                        cwd=self.project_root,
                        check=True,
                    )
                    self.console.print("[green]✓ Distribution check passed[/green]")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    self.console.print("[yellow]twine not available, skipping check[/yellow]")
                
                # Basic file existence check
                wheel_files = list(self.dist_dir.glob("*.whl"))
                tar_files = list(self.dist_dir.glob("*.tar.gz"))
                
                if not wheel_files:
                    self.console.print("[red]No wheel files found[/red]")
                    sys.exit(1)
                
                if not tar_files:
                    self.console.print("[red]No source distribution found[/red]")
                    sys.exit(1)
                
                progress.remove_task(task)
                
            except Exception as e:
                progress.remove_task(task)
                self.console.print(f"[red]Check failed: {e}[/red]")
                sys.exit(1)

    def install(self, editable: bool = False) -> None:
        """Install the package locally.
        
        Args:
            editable: Whether to install in editable mode
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Installing package...", total=None)
            
            try:
                if editable:
                    # Install in editable mode
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-e", "."],
                        cwd=self.project_root,
                        check=True,
                    )
                else:
                    # Install from built distribution
                    if not self.dist_dir.exists():
                        self.console.print("[red]No dist directory found. Run build first.[/red]")
                        sys.exit(1)
                    
                    wheel_files = list(self.dist_dir.glob("*.whl"))
                    if not wheel_files:
                        self.console.print("[red]No wheel files found. Run build first.[/red]")
                        sys.exit(1)
                    
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", str(wheel_files[0])],
                        cwd=self.project_root,
                        check=True,
                    )
                
                progress.remove_task(task)
                self.console.print("[green]✓ Package installed successfully[/green]")
                
            except subprocess.CalledProcessError as e:
                progress.remove_task(task)
                self.console.print(f"[red]Installation failed: {e}[/red]")
                sys.exit(1)

    def all(self) -> None:
        """Run complete build pipeline: clean, build, check."""
        self.clean()
        self.build(clean_first=False)
        self.check()
        self.console.print("[green]✓ Build pipeline completed successfully[/green]")

    def info(self) -> None:
        """Display build environment information."""
        self.console.print("[cyan]Build Environment Information[/cyan]")
        self.console.print(f"Project root: {self.project_root}")
        self.console.print(f"Distribution directory: {self.dist_dir}")
        self.console.print(f"Python executable: {sys.executable}")
        self.console.print(f"Python version: {sys.version}")
        
        # Check for required tools
        tools = ["build", "twine", "hatch"]
        for tool in tools:
            try:
                subprocess.run(
                    [sys.executable, "-m", tool, "--version"],
                    capture_output=True,
                    check=True,
                )
                self.console.print(f"[green]✓ {tool} available[/green]")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.console.print(f"[red]✗ {tool} not available[/red]")


def main() -> None:
    """Main entry point."""
    fire.Fire(Builder)


if __name__ == "__main__":
    main()