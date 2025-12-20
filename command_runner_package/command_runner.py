import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path


class Command(ABC):
    """Abstract base class for all commands."""
    @abstractmethod
    def execute(self):
        pass


class ShellCommand(Command):
    """A shell command that can be executed in a subprocess."""

    def __init__(self, command: str):
        self.command = command
        self.output = None
        self.error = None

    def execute(self):
        try:
            result = subprocess.run(
                self.command,
                shell=True,
                check=True,
                text=True,
                capture_output=True
            )
            self.output = result.stdout.strip()
            self.error = None
        except subprocess.CalledProcessError as e:
            self.output = None
            self.error = e.stderr.strip() or f"Command failed: {self.command}"

        return self  # convenient chaining


class CommandRunner:
    """Executes shell commands directly or from a file."""

    @staticmethod
    def run(command: str) -> ShellCommand:
        """Run a single shell command."""
        cmd = ShellCommand(command)
        cmd.execute()
        return cmd

    @staticmethod
    def run_from_file(file_path: str | Path) -> list[ShellCommand]:
        """
        Read a file containing shell commands (one per line)
        and execute them sequentially.

        Returns:
            List[ShellCommand]: Each object contains .command, .output, .error
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Command file not found: {file_path}")

        results: list[ShellCommand] = []

        with file_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                    
                print(line)    

                cmd = ShellCommand(line)
                try:
                    cmd.execute()
                    print(cmd.output)
                except Exception as e:
                    cmd.output = None
                    cmd.error = f"Error on line {line_num}: {e}"
                results.append(cmd)

        return results

if __name__ == "__main__":
    cmd = CommandRunner()
    sys.exit(cmd.run_from_file("commands.txt"))
