#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire", "rich", "pytest", "pytest-cov", "pytest-xdist"]
# ///
"""Test script for twat-os package."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import fire
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class Tester:
    """Test automation for twat-os package."""

    def __init__(self) -> None:
        """Initialize the tester."""
        self.console = console
        self.project_root = Path(__file__).parent.parent

    def run(
        self,
        tests: Optional[str] = None,
        coverage: bool = True,
        parallel: bool = True,
        verbose: bool = False,
        markers: Optional[str] = None,
    ) -> None:
        """Run the test suite.
        
        Args:
            tests: Specific test file or directory to run
            coverage: Whether to collect coverage data
            parallel: Whether to run tests in parallel
            verbose: Whether to run in verbose mode
            markers: Pytest markers to filter tests
        """
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test target
        if tests:
            cmd.append(tests)
        else:
            cmd.append("tests")
        
        # Add coverage options
        if coverage:
            cmd.extend([
                "--cov=src/twat_os",
                "--cov=tests",
                "--cov-report=term-missing",
                "--cov-report=xml",
                "--cov-config=pyproject.toml"
            ])
        
        # Add parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add verbose output
        if verbose:
            cmd.append("-v")
        
        # Add markers
        if markers:
            cmd.extend(["-m", markers])
        
        # Add other useful options
        cmd.extend([
            "--tb=short",
            "--durations=10",
            "-p", "no:briefcase"
        ])
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Running tests...", total=None)
            
            try:
                result = subprocess.run(
                    cmd,
                    cwd=self.project_root,
                    check=True,
                )
                
                progress.remove_task(task)
                self.console.print("[green]✓ Tests passed successfully[/green]")
                
            except subprocess.CalledProcessError as e:
                progress.remove_task(task)
                self.console.print(f"[red]Tests failed with exit code {e.returncode}[/red]")
                sys.exit(e.returncode)

    def unit(self, coverage: bool = True, verbose: bool = False) -> None:
        """Run only unit tests.
        
        Args:
            coverage: Whether to collect coverage data
            verbose: Whether to run in verbose mode
        """
        self.run(tests="tests/unit", coverage=coverage, verbose=verbose)

    def integration(self, coverage: bool = True, verbose: bool = False) -> None:
        """Run only integration tests.
        
        Args:
            coverage: Whether to collect coverage data
            verbose: Whether to run in verbose mode
        """
        self.run(tests="tests/integration", coverage=coverage, verbose=verbose)

    def config(self, coverage: bool = True, verbose: bool = False) -> None:
        """Run configuration tests.
        
        Args:
            coverage: Whether to collect coverage data
            verbose: Whether to run in verbose mode
        """
        self.run(tests="tests/test_config_loading.py", coverage=coverage, verbose=verbose)

    def platform(self, coverage: bool = True, verbose: bool = False) -> None:
        """Run cross-platform tests.
        
        Args:
            coverage: Whether to collect coverage data
            verbose: Whether to run in verbose mode
        """
        self.run(tests="tests/test_cross_platform.py", coverage=coverage, verbose=verbose)

    def quick(self) -> None:
        """Run a quick test suite (no coverage, no parallel)."""
        self.run(coverage=False, parallel=False, verbose=False)

    def watch(self) -> None:
        """Run tests in watch mode (requires pytest-watch)."""
        cmd = [sys.executable, "-m", "ptw", "tests", "--", "-x"]
        
        try:
            subprocess.run(cmd, cwd=self.project_root, check=True)
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]Watch mode failed: {e}[/red]")
            sys.exit(1)
        except FileNotFoundError:
            self.console.print("[red]pytest-watch not installed. Install with: pip install pytest-watch[/red]")
            sys.exit(1)

    def benchmark(self) -> None:
        """Run benchmark tests."""
        cmd = [
            sys.executable, "-m", "pytest",
            "tests",
            "-m", "benchmark",
            "--benchmark-only",
            "--benchmark-sort=mean",
            "-v"
        ]
        
        try:
            subprocess.run(cmd, cwd=self.project_root, check=True)
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]Benchmark tests failed: {e}[/red]")
            sys.exit(1)

    def lint(self) -> None:
        """Run linting checks."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Running linter...", total=None)
            
            try:
                # Run ruff check
                subprocess.run([
                    sys.executable, "-m", "ruff", "check",
                    "src/twat_os", "tests",
                    "--output-format=github"
                ], cwd=self.project_root, check=True)
                
                # Run ruff format check
                subprocess.run([
                    sys.executable, "-m", "ruff", "format",
                    "src/twat_os", "tests",
                    "--check", "--respect-gitignore"
                ], cwd=self.project_root, check=True)
                
                progress.remove_task(task)
                self.console.print("[green]✓ Linting passed[/green]")
                
            except subprocess.CalledProcessError as e:
                progress.remove_task(task)
                self.console.print(f"[red]Linting failed: {e}[/red]")
                sys.exit(1)

    def typecheck(self) -> None:
        """Run type checking."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Running type checker...", total=None)
            
            try:
                subprocess.run([
                    sys.executable, "-m", "mypy",
                    "src/twat_os", "tests"
                ], cwd=self.project_root, check=True)
                
                progress.remove_task(task)
                self.console.print("[green]✓ Type checking passed[/green]")
                
            except subprocess.CalledProcessError as e:
                progress.remove_task(task)
                self.console.print(f"[red]Type checking failed: {e}[/red]")
                sys.exit(1)

    def all(self) -> None:
        """Run complete test pipeline: lint, typecheck, tests."""
        self.lint()
        self.typecheck()
        self.run()
        self.console.print("[green]✓ All tests passed successfully[/green]")

    def coverage_report(self) -> None:
        """Generate and display coverage report."""
        try:
            # Generate HTML coverage report
            subprocess.run([
                sys.executable, "-m", "coverage", "html"
            ], cwd=self.project_root, check=True)
            
            # Display coverage report
            subprocess.run([
                sys.executable, "-m", "coverage", "report"
            ], cwd=self.project_root, check=True)
            
            self.console.print("[green]✓ Coverage report generated[/green]")
            self.console.print("HTML report available in htmlcov/index.html")
            
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]Coverage report generation failed: {e}[/red]")
            sys.exit(1)

    def clean(self) -> None:
        """Clean test artifacts."""
        import shutil
        
        artifacts = [
            self.project_root / ".coverage",
            self.project_root / "coverage.xml",
            self.project_root / "htmlcov",
            self.project_root / ".pytest_cache",
        ]
        
        for artifact in artifacts:
            if artifact.exists():
                if artifact.is_dir():
                    shutil.rmtree(artifact)
                else:
                    artifact.unlink()
                self.console.print(f"[green]Removed: {artifact}[/green]")
        
        self.console.print("[green]✓ Test artifacts cleaned[/green]")

    def info(self) -> None:
        """Display test environment information."""
        self.console.print("[cyan]Test Environment Information[/cyan]")
        self.console.print(f"Project root: {self.project_root}")
        self.console.print(f"Python executable: {sys.executable}")
        self.console.print(f"Python version: {sys.version}")
        
        # Check for required tools
        tools = ["pytest", "coverage", "mypy", "ruff"]
        for tool in tools:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", tool, "--version"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                version = result.stdout.strip().split('\n')[0]
                self.console.print(f"[green]✓ {tool}: {version}[/green]")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.console.print(f"[red]✗ {tool} not available[/red]")
        
        # Show test discovery
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            test_count = result.stdout.count("test session starts")
            self.console.print(f"Discovered tests: {test_count}")
        except subprocess.CalledProcessError:
            self.console.print("[yellow]Could not discover tests[/yellow]")


def main() -> None:
    """Main entry point."""
    fire.Fire(Tester)


if __name__ == "__main__":
    main()