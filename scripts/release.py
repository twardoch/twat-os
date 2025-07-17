#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire", "rich", "requests", "gitpython", "semver"]
# ///
"""Release script for twat-os package."""

import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import fire
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class Releaser:
    """Release automation for twat-os package."""

    def __init__(self) -> None:
        """Initialize the releaser."""
        self.console = console
        self.project_root = Path(__file__).parent.parent

    def _run_command(self, cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        return subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=check,
        )

    def _validate_version(self, version: str) -> bool:
        """Validate semantic version format."""
        # Pattern for semantic versioning (with optional pre-release)
        pattern = r'^v?(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)*))?$'
        return bool(re.match(pattern, version))

    def _get_current_version(self) -> Optional[str]:
        """Get current version from git tags."""
        try:
            result = self._run_command([
                "git", "describe", "--tags", "--abbrev=0"
            ], check=False)
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None

    def _get_next_version(self, current: Optional[str], bump: str) -> str:
        """Calculate next version based on bump type."""
        if current is None:
            return "v1.0.0"
        
        # Remove 'v' prefix if present
        current_clean = current.lstrip('v')
        
        # Parse version components
        version_parts = current_clean.split('.')
        if len(version_parts) != 3:
            raise ValueError(f"Invalid version format: {current}")
        
        major, minor, patch = map(int, version_parts)
        
        if bump == "major":
            return f"v{major + 1}.0.0"
        elif bump == "minor":
            return f"v{major}.{minor + 1}.0"
        elif bump == "patch":
            return f"v{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(f"Invalid bump type: {bump}")

    def _check_working_directory(self) -> bool:
        """Check if working directory is clean."""
        result = self._run_command(["git", "status", "--porcelain"], check=False)
        return result.returncode == 0 and not result.stdout.strip()

    def _check_current_branch(self) -> str:
        """Get current branch name."""
        result = self._run_command(["git", "branch", "--show-current"])
        return result.stdout.strip()

    def _generate_changelog(self, since_tag: Optional[str] = None) -> str:
        """Generate changelog from git history."""
        cmd = ["git", "log", "--oneline", "--pretty=format:- %s"]
        if since_tag:
            cmd.append(f"{since_tag}..HEAD")
        else:
            cmd.extend(["--max-count=20"])
        
        result = self._run_command(cmd, check=False)
        if result.returncode == 0:
            return result.stdout.strip()
        return "No changes found"

    def check(self) -> None:
        """Check if repository is ready for release."""
        self.console.print("[cyan]Checking release readiness...[/cyan]")
        
        issues = []
        
        # Check working directory
        if not self._check_working_directory():
            issues.append("Working directory is not clean")
        
        # Check current branch
        current_branch = self._check_current_branch()
        if current_branch != "main":
            issues.append(f"Current branch is '{current_branch}', should be 'main'")
        
        # Check if we're up to date with remote
        try:
            self._run_command(["git", "fetch", "origin"])
            result = self._run_command(["git", "status", "-uno"])
            if "Your branch is behind" in result.stdout:
                issues.append("Local branch is behind remote")
        except Exception:
            issues.append("Could not check remote status")
        
        # Check if tests pass
        try:
            self._run_command([sys.executable, "-m", "pytest", "-x"])
            self.console.print("[green]✓ Tests pass[/green]")
        except subprocess.CalledProcessError:
            issues.append("Tests are failing")
        
        # Display results
        if issues:
            self.console.print("[red]Release readiness check failed:[/red]")
            for issue in issues:
                self.console.print(f"  - {issue}")
            sys.exit(1)
        else:
            self.console.print("[green]✓ Repository is ready for release[/green]")

    def tag(self, version: str, push: bool = True) -> None:
        """Create and push a git tag.
        
        Args:
            version: Version to tag (e.g., v1.0.0)
            push: Whether to push the tag to remote
        """
        # Validate version format
        if not self._validate_version(version):
            self.console.print(f"[red]Invalid version format: {version}[/red]")
            self.console.print("Expected format: v1.0.0 or v1.0.0-alpha.1")
            sys.exit(1)
        
        # Ensure 'v' prefix
        if not version.startswith('v'):
            version = f'v{version}'
        
        # Check if tag already exists
        result = self._run_command(["git", "tag", "-l", version], check=False)
        if result.stdout.strip():
            self.console.print(f"[red]Tag {version} already exists[/red]")
            sys.exit(1)
        
        # Generate changelog
        current_version = self._get_current_version()
        changelog = self._generate_changelog(current_version)
        
        # Create tag with message
        tag_message = f"Release {version}\n\nChanges:\n{changelog}"
        
        try:
            self._run_command(["git", "tag", "-a", version, "-m", tag_message])
            self.console.print(f"[green]✓ Created tag: {version}[/green]")
            
            if push:
                self._run_command(["git", "push", "origin", version])
                self.console.print(f"[green]✓ Pushed tag to remote[/green]")
            
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]Failed to create tag: {e}[/red]")
            sys.exit(1)

    def release(
        self,
        version: Optional[str] = None,
        bump: Optional[str] = None,
        dry_run: bool = False,
    ) -> None:
        """Create a complete release.
        
        Args:
            version: Specific version to release (e.g., v1.0.0)
            bump: Auto-increment version (major, minor, patch)
            dry_run: Show what would be done without actually doing it
        """
        # Validate arguments
        if version and bump:
            self.console.print("[red]Cannot specify both version and bump[/red]")
            sys.exit(1)
        
        if not version and not bump:
            bump = "patch"  # Default to patch release
        
        # Determine version
        if version:
            release_version = version
        else:
            current_version = self._get_current_version()
            release_version = self._get_next_version(current_version, bump)
        
        # Validate version
        if not self._validate_version(release_version):
            self.console.print(f"[red]Invalid version format: {release_version}[/red]")
            sys.exit(1)
        
        # Ensure 'v' prefix
        if not release_version.startswith('v'):
            release_version = f'v{release_version}'
        
        self.console.print(f"[cyan]Preparing release: {release_version}[/cyan]")
        
        if dry_run:
            self.console.print("[yellow]DRY RUN - No changes will be made[/yellow]")
        
        # Check readiness
        if not dry_run:
            self.check()
        
        # Show what will be done
        current_version = self._get_current_version()
        changelog = self._generate_changelog(current_version)
        
        self.console.print(f"Current version: {current_version or 'None'}")
        self.console.print(f"Release version: {release_version}")
        self.console.print(f"Changes since last release:")
        self.console.print(changelog)
        
        # Confirm release
        if not dry_run:
            if not Confirm.ask(f"Create release {release_version}?"):
                self.console.print("[yellow]Release cancelled[/yellow]")
                return
        
        # Create and push tag
        if not dry_run:
            self.tag(release_version, push=True)
            self.console.print(f"[green]✓ Release {release_version} created successfully[/green]")
            self.console.print("GitHub Actions will now build and publish the release.")
        else:
            self.console.print(f"[yellow]Would create and push tag: {release_version}[/yellow]")

    def patch(self, dry_run: bool = False) -> None:
        """Create a patch release."""
        self.release(bump="patch", dry_run=dry_run)

    def minor(self, dry_run: bool = False) -> None:
        """Create a minor release."""
        self.release(bump="minor", dry_run=dry_run)

    def major(self, dry_run: bool = False) -> None:
        """Create a major release."""
        self.release(bump="major", dry_run=dry_run)

    def changelog(self, since: Optional[str] = None) -> None:
        """Generate changelog since a specific tag or last release.
        
        Args:
            since: Tag to generate changelog since (default: last tag)
        """
        if since is None:
            since = self._get_current_version()
        
        changelog = self._generate_changelog(since)
        
        self.console.print(f"[cyan]Changelog since {since or 'beginning'}:[/cyan]")
        self.console.print(changelog)

    def info(self) -> None:
        """Display release information."""
        current_version = self._get_current_version()
        current_branch = self._check_current_branch()
        is_clean = self._check_working_directory()
        
        self.console.print("[cyan]Release Information[/cyan]")
        self.console.print(f"Current version: {current_version or 'None'}")
        self.console.print(f"Current branch: {current_branch}")
        self.console.print(f"Working directory clean: {'✓' if is_clean else '✗'}")
        
        # Show available bump versions
        if current_version:
            for bump_type in ["patch", "minor", "major"]:
                next_version = self._get_next_version(current_version, bump_type)
                self.console.print(f"Next {bump_type} version: {next_version}")
        
        # Show recent tags
        try:
            result = self._run_command([
                "git", "tag", "-l", "--sort=-version:refname"
            ], check=False)
            if result.returncode == 0:
                tags = result.stdout.strip().split('\n')[:5]
                if tags and tags[0]:
                    self.console.print(f"Recent tags: {', '.join(tags)}")
        except Exception:
            pass


def main() -> None:
    """Main entry point."""
    fire.Fire(Releaser)


if __name__ == "__main__":
    main()