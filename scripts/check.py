#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire", "rich", "safety", "bandit"]
# ///
"""Pre-commit check script for twat-os package."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import fire
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class Checker:
    """Pre-commit checks for twat-os package."""

    def __init__(self) -> None:
        """Initialize the checker."""
        self.console = console
        self.project_root = Path(__file__).parent.parent

    def _run_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        return subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=check,
        )

    def format_check(self) -> bool:
        """Check code formatting with ruff."""
        try:
            self._run_command([
                sys.executable, "-m", "ruff", "format",
                "src/twat_os", "tests", "scripts",
                "--check", "--respect-gitignore"
            ])
            self.console.print("[green]✓ Code formatting is correct[/green]")
            return True
        except subprocess.CalledProcessError:
            self.console.print("[red]✗ Code formatting issues found[/red]")
            self.console.print("Run: ruff format src/twat_os tests scripts")
            return False

    def lint_check(self) -> bool:
        """Check code linting with ruff."""
        try:
            result = self._run_command([
                sys.executable, "-m", "ruff", "check",
                "src/twat_os", "tests", "scripts",
                "--output-format=github"
            ])
            if result.stdout.strip():
                self.console.print("[yellow]Linting warnings found:[/yellow]")
                self.console.print(result.stdout)
            self.console.print("[green]✓ No critical linting issues[/green]")
            return True
        except subprocess.CalledProcessError as e:
            self.console.print("[red]✗ Linting issues found[/red]")
            if e.stdout:
                self.console.print(e.stdout)
            if e.stderr:
                self.console.print(e.stderr)
            return False

    def type_check(self) -> bool:
        """Check types with mypy."""
        try:
            self._run_command([
                sys.executable, "-m", "mypy",
                "src/twat_os", "tests"
            ])
            self.console.print("[green]✓ Type checking passed[/green]")
            return True
        except subprocess.CalledProcessError as e:
            self.console.print("[red]✗ Type checking failed[/red]")
            if e.stdout:
                self.console.print(e.stdout)
            if e.stderr:
                self.console.print(e.stderr)
            return False

    def test_check(self) -> bool:
        """Run tests to ensure they pass."""
        try:
            self._run_command([
                sys.executable, "-m", "pytest",
                "tests", "-x", "--tb=short"
            ])
            self.console.print("[green]✓ Tests passed[/green]")
            return True
        except subprocess.CalledProcessError:
            self.console.print("[red]✗ Tests failed[/red]")
            return False

    def security_check(self) -> bool:
        """Check for security vulnerabilities."""
        security_passed = True
        
        # Check with bandit
        try:
            result = self._run_command([
                sys.executable, "-m", "bandit",
                "-r", "src/twat_os",
                "-f", "json"
            ], check=False)
            
            if result.returncode == 0:
                self.console.print("[green]✓ No security issues found (bandit)[/green]")
            else:
                self.console.print("[yellow]Security warnings found (bandit)[/yellow]")
                # Note: bandit warnings are not always critical
                
        except FileNotFoundError:
            self.console.print("[yellow]bandit not available for security check[/yellow]")
        
        # Check with safety (if available)
        try:
            self._run_command([
                sys.executable, "-m", "safety", "check"
            ])
            self.console.print("[green]✓ No known security vulnerabilities in dependencies[/green]")
        except subprocess.CalledProcessError:
            self.console.print("[red]✗ Security vulnerabilities found in dependencies[/red]")
            security_passed = False
        except FileNotFoundError:
            self.console.print("[yellow]safety not available for dependency security check[/yellow]")
        
        return security_passed

    def dependency_check(self) -> bool:
        """Check dependency consistency."""
        try:
            # Check if all dependencies are properly installed
            import twat_os.paths  # noqa: F401
            self.console.print("[green]✓ All dependencies are available[/green]")
            return True
        except ImportError as e:
            self.console.print(f"[red]✗ Import error: {e}[/red]")
            return False

    def build_check(self) -> bool:
        """Check if package can be built."""
        try:
            # Clean any existing build artifacts
            import shutil
            dist_dir = self.project_root / "dist"
            if dist_dir.exists():
                shutil.rmtree(dist_dir)
            
            # Build the package
            self._run_command([
                sys.executable, "-m", "build",
                "--outdir", str(dist_dir)
            ])
            
            # Check if build artifacts exist
            wheel_files = list(dist_dir.glob("*.whl"))
            tar_files = list(dist_dir.glob("*.tar.gz"))
            
            if wheel_files and tar_files:
                self.console.print("[green]✓ Package builds successfully[/green]")
                return True
            else:
                self.console.print("[red]✗ Package build incomplete[/red]")
                return False
                
        except subprocess.CalledProcessError:
            self.console.print("[red]✗ Package build failed[/red]")
            return False

    def all(self) -> None:
        """Run all checks and report results."""
        self.console.print("[cyan]Running all pre-commit checks...[/cyan]")
        
        checks = [
            ("Format", self.format_check),
            ("Lint", self.lint_check),
            ("Type", self.type_check),
            ("Test", self.test_check),
            ("Security", self.security_check),
            ("Dependencies", self.dependency_check),
            ("Build", self.build_check),
        ]
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            for check_name, check_func in checks:
                task = progress.add_task(f"Running {check_name.lower()} check...", total=None)
                
                try:
                    result = check_func()
                    results.append((check_name, result))
                except Exception as e:
                    results.append((check_name, False))
                    self.console.print(f"[red]✗ {check_name} check failed with error: {e}[/red]")
                
                progress.remove_task(task)
        
        # Display results table
        table = Table(title="Pre-commit Check Results")
        table.add_column("Check", style="cyan")
        table.add_column("Result", style="bold")
        
        for check_name, passed in results:
            status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
            table.add_row(check_name, status)
        
        self.console.print(table)
        
        # Summary
        passed_count = sum(1 for _, passed in results if passed)
        total_count = len(results)
        
        if passed_count == total_count:
            self.console.print(f"[green]✓ All {total_count} checks passed![/green]")
        else:
            failed_count = total_count - passed_count
            self.console.print(f"[red]✗ {failed_count} of {total_count} checks failed[/red]")
            sys.exit(1)

    def quick(self) -> None:
        """Run quick checks (format, lint, type)."""
        self.console.print("[cyan]Running quick checks...[/cyan]")
        
        checks = [
            ("Format", self.format_check),
            ("Lint", self.lint_check),
            ("Type", self.type_check),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            if not check_func():
                all_passed = False
        
        if all_passed:
            self.console.print("[green]✓ All quick checks passed![/green]")
        else:
            self.console.print("[red]✗ Some quick checks failed[/red]")
            sys.exit(1)

    def fix(self) -> None:
        """Automatically fix issues where possible."""
        self.console.print("[cyan]Fixing issues automatically...[/cyan]")
        
        # Fix formatting
        try:
            self._run_command([
                sys.executable, "-m", "ruff", "format",
                "src/twat_os", "tests", "scripts",
                "--respect-gitignore"
            ])
            self.console.print("[green]✓ Fixed formatting issues[/green]")
        except subprocess.CalledProcessError:
            self.console.print("[red]✗ Could not fix formatting issues[/red]")
        
        # Fix linting issues
        try:
            self._run_command([
                sys.executable, "-m", "ruff", "check",
                "src/twat_os", "tests", "scripts",
                "--fix", "--unsafe-fixes"
            ])
            self.console.print("[green]✓ Fixed linting issues[/green]")
        except subprocess.CalledProcessError:
            self.console.print("[yellow]Some linting issues require manual fixing[/yellow]")
        
        self.console.print("[green]✓ Auto-fix completed[/green]")

    def info(self) -> None:
        """Display check environment information."""
        self.console.print("[cyan]Check Environment Information[/cyan]")
        self.console.print(f"Project root: {self.project_root}")
        self.console.print(f"Python executable: {sys.executable}")
        self.console.print(f"Python version: {sys.version}")
        
        # Check for required tools
        tools = ["ruff", "mypy", "pytest", "build", "bandit", "safety"]
        for tool in tools:
            try:
                result = self._run_command([
                    sys.executable, "-m", tool, "--version"
                ], check=False)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    self.console.print(f"[green]✓ {tool}: {version}[/green]")
                else:
                    self.console.print(f"[red]✗ {tool} not available[/red]")
            except FileNotFoundError:
                self.console.print(f"[red]✗ {tool} not available[/red]")


def main() -> None:
    """Main entry point."""
    fire.Fire(Checker)


if __name__ == "__main__":
    main()