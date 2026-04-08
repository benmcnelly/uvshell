import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import uvshell
from uvshell import cli


def test_version_matches_package():
    assert uvshell.__version__ == "0.1.4"


def test_ensure_uv_exists_exits_when_missing(monkeypatch):
    monkeypatch.setattr(cli.shutil, "which", lambda _: None)

    with pytest.raises(SystemExit, match="uv is not installed"):
        cli._ensure_uv_exists()


def test_ensure_venv_returns_immediately_when_venv_exists(tmp_path, monkeypatch):
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()

    called = []

    def fake_run(*args, **kwargs):
        called.append((args, kwargs))

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    cli._ensure_venv(venv_dir, python=None, package=False)

    assert called == []


def test_ensure_venv_creates_gitignore_python_version_and_runs_uv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    commands = []
    package_settings = []

    monkeypatch.setattr(cli, "_ensure_uv_exists", lambda: None)
    monkeypatch.setattr(cli, "_ensure_project_package_setting", lambda package: package_settings.append(package))
    monkeypatch.setattr(
        cli.subprocess,
        "run",
        lambda cmd, check: commands.append((cmd, check)),
    )

    venv_dir = tmp_path / ".venv"
    cli._ensure_venv(venv_dir, python="3.13", package=False)

    assert (tmp_path / ".gitignore").read_text() == "# Virtual env\n.venv/\n"
    assert (tmp_path / ".python-version").read_text() == "3.13\n"
    assert package_settings == [False]
    assert commands == [
        (["uv", "init", "--python", "3.13"], True),
        (["uv", "venv", str(venv_dir), "--python", "3.13"], True),
    ]


def test_ensure_venv_appends_gitignore_once(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    (tmp_path / ".gitignore").write_text("node_modules/\n")

    commands = []
    monkeypatch.setattr(cli, "_ensure_uv_exists", lambda: None)
    monkeypatch.setattr(
        cli.subprocess,
        "run",
        lambda cmd, check: commands.append((cmd, check)),
    )

    venv_dir = tmp_path / ".venv"
    cli._ensure_venv(venv_dir, python=None, package=False)

    assert (tmp_path / ".gitignore").read_text() == "node_modules/\n\n# Virtual env\n.venv/\n"
    assert commands == [(["uv", "venv", str(venv_dir)], True)]


def test_ensure_project_package_setting_appends_to_existing_pyproject(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")

    cli._ensure_project_package_setting(package=False)

    assert (tmp_path / "pyproject.toml").read_text() == "[project]\nname='demo'\n\n[tool.uv]\npackage = false\n"


def test_ensure_venv_uses_packaged_init_when_requested(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    commands = []

    monkeypatch.setattr(cli, "_ensure_uv_exists", lambda: None)
    monkeypatch.setattr(
        cli.subprocess,
        "run",
        lambda cmd, check: commands.append((cmd, check)),
    )

    venv_dir = tmp_path / ".venv"
    cli._ensure_venv(venv_dir, python="3.13", package=True)

    assert not (tmp_path / "pyproject.toml").exists()
    assert commands == [
        (["uv", "init", "--package", "--python", "3.13"], True),
        (["uv", "venv", str(venv_dir), "--python", "3.13"], True),
    ]


def test_main_errors_when_no_create_and_venv_missing(tmp_path):
    missing = tmp_path / ".venv"

    with pytest.raises(SystemExit, match="No venv found"):
        cli.main(["--venv", str(missing), "--no-create"])


def test_main_dispatches_to_windows_subshell(tmp_path, monkeypatch):
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()

    monkeypatch.setattr(cli.os, "name", "nt")
    called = []
    monkeypatch.setattr(cli, "_spawn_windows_cmd_subshell", lambda path: called.append(path))

    cli.main(["--venv", str(venv_dir)])

    assert called == [venv_dir.resolve()]
