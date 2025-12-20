import pytest
from command_runner import CommandRunner, ShellCommand


def test_shell_command_success():
    cmd = ShellCommand("echo hello")
    cmd.execute()
    assert cmd.output.strip() == "hello"
    assert cmd.error is None


def test_shell_command_failure():
    cmd = ShellCommand("exit 1")
    cmd.execute()
    assert cmd.output is None
    assert "Command failed" in cmd.error


def test_runner_run_single_command():
    result = CommandRunner.run("echo test123")
    assert isinstance(result, ShellCommand)
    assert result.output == "test123"
    assert result.error is None


def test_run_from_file_success(tmp_path):
    file_path = tmp_path / "commands.txt"
    file_path.write_text("""
        # test commands
        echo one
        echo two
    """)

    results = CommandRunner.run_from_file(file_path)
    assert len(results) == 2
    assert [r.output for r in results] == ["one", "two"]
    assert all(r.error is None for r in results)


def test_run_from_file_with_error(tmp_path):
    file_path = tmp_path / "commands_with_error.txt"
    file_path.write_text("""
        echo before
        someinvalidcommand
        echo after
    """)

    results = CommandRunner.run_from_file(file_path)
    assert len(results) == 3
    assert results[0].output == "before"
    assert results[1].error is not None  # invalid command should fail
    assert results[2].output == "after"


def test_run_from_file_missing(tmp_path):
    missing_file = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError):
        CommandRunner.run_from_file(missing_file)
