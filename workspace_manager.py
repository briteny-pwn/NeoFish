#!/usr/bin/env python3
"""
workspace_manager.py - File operations and bash execution for NeoFish agent.

Provides safe file operations within a workspace directory with:
- Path safety (strict mode for sandboxing, non-strict for flexibility)
- Dangerous command interception
- Async bash execution
"""

import os
import asyncio
import subprocess
from pathlib import Path
from typing import Optional

# Default workspace directory
WORKDIR = Path(os.getenv("WORKDIR", "./workspace")).resolve()


class WorkspaceManager:
    """Manages file operations and bash execution within a workspace."""

    def __init__(self, workdir: Path = None, strict: bool = False):
        """
        Initialize workspace manager.

        Args:
            workdir: Base directory for file operations. Defaults to WORKDIR env or ./workspace
            strict: If True, block operations outside workdir. If False, allow with warning.
        """
        self.workdir = (workdir or WORKDIR).resolve()
        self.strict = strict
        self.workdir.mkdir(parents=True, exist_ok=True)

    def safe_path(self, p: str, strict: bool = None) -> Path:
        """
        Resolve and validate a path.

        Args:
            p: Path string (relative or absolute)
            strict: Override default strict mode for this call

        Returns:
            Resolved Path object

        Raises:
            ValueError: If path escapes workspace in strict mode
        """
        use_strict = strict if strict is not None else self.strict
        path = Path(p)

        # If relative, resolve against workdir
        if not path.is_absolute():
            path = (self.workdir / path).resolve()
        else:
            path = path.resolve()

        # Check if path is within workspace
        if use_strict and not path.is_relative_to(self.workdir):
            raise ValueError(f"Path escapes workspace: {p}")

        return path

    async def run_bash(self, command: str, timeout: int = 120) -> str:
        """
        Execute a shell command with safety checks.

        Args:
            command: Shell command to execute
            timeout: Timeout in seconds (default 120)

        Returns:
            Command output or error message
        """
        # Dangerous command patterns to block
        dangerous_patterns = [
            "rm -rf /",
            "rm -rf /*",
            "sudo ",
            "shutdown",
            "reboot",
            "init 0",
            "mkfs",
            "dd if=",
            "> /dev/sd",
            ":(){ :|:& };:",  # Fork bomb
        ]

        for pattern in dangerous_patterns:
            if pattern in command:
                return f"Error: Dangerous command blocked (matched: {pattern.strip()})"

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workdir)
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return f"Error: Timeout ({timeout}s)"

            output = (stdout.decode() + stderr.decode()).strip()
            # Truncate large outputs
            return output[:50000] if output else "(no output)"

        except Exception as e:
            return f"Error: {str(e)}"

    async def read_file(self, path: str, limit: Optional[int] = None) -> str:
        """
        Read file contents.

        Args:
            path: File path (relative to workdir or absolute)
            limit: Maximum number of lines to read

        Returns:
            File contents or error message
        """
        try:
            fp = self.safe_path(path)

            if not fp.exists():
                return f"Error: File not found: {path}"

            if not fp.is_file():
                return f"Error: Not a file: {path}"

            lines = fp.read_text(encoding='utf-8', errors='replace').splitlines()

            if limit and limit < len(lines):
                lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]

            content = "\n".join(lines)
            return content[:50000] if content else "(empty file)"

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    async def write_file(self, path: str, content: str) -> str:
        """
        Write content to a file.

        Args:
            path: File path (relative to workdir or absolute)
            content: Content to write

        Returns:
            Success message or error
        """
        try:
            fp = self.safe_path(path)

            # Create parent directories if needed
            fp.parent.mkdir(parents=True, exist_ok=True)

            fp.write_text(content, encoding='utf-8')
            return f"Wrote {len(content)} characters to {path}"

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    async def edit_file(self, path: str, old_text: str, new_text: str) -> str:
        """
        Replace exact text in a file.

        Args:
            path: File path
            old_text: Text to find and replace
            new_text: Replacement text

        Returns:
            Success message or error
        """
        try:
            fp = self.safe_path(path)

            if not fp.exists():
                return f"Error: File not found: {path}"

            content = fp.read_text(encoding='utf-8')

            if old_text not in content:
                return f"Error: Text not found in {path}"

            # Replace only the first occurrence
            new_content = content.replace(old_text, new_text, 1)
            fp.write_text(new_content, encoding='utf-8')

            return f"Edited {path}: replaced {len(old_text)} chars with {len(new_text)} chars"

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error editing file: {str(e)}"

    async def list_dir(self, path: str = ".") -> str:
        """
        List directory contents.

        Args:
            path: Directory path

        Returns:
            Directory listing or error
        """
        try:
            fp = self.safe_path(path)

            if not fp.exists():
                return f"Error: Directory not found: {path}"

            if not fp.is_dir():
                return f"Error: Not a directory: {path}"

            items = list(fp.iterdir())
            lines = []

            for item in sorted(items, key=lambda x: (not x.is_dir(), x.name.lower())):
                prefix = "📁 " if item.is_dir() else "📄 "
                size = ""
                if item.is_file():
                    try:
                        size = f" ({item.stat().st_size} bytes)"
                    except:
                        pass
                lines.append(f"{prefix}{item.name}{size}")

            return "\n".join(lines) if lines else "(empty directory)"

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    async def delete_file(self, path: str) -> str:
        """
        Delete a file.

        Args:
            path: File path to delete

        Returns:
            Success message or error
        """
        try:
            fp = self.safe_path(path)

            if not fp.exists():
                return f"Error: File not found: {path}"

            if fp.is_dir():
                return f"Error: Is a directory, not a file: {path}"

            fp.unlink()
            return f"Deleted: {path}"

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"

    async def create_dir(self, path: str) -> str:
        """
        Create a directory.

        Args:
            path: Directory path to create

        Returns:
            Success message or error
        """
        try:
            fp = self.safe_path(path)
            fp.mkdir(parents=True, exist_ok=True)
            return f"Created directory: {path}"

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"


# Default instance
workspace = WorkspaceManager()