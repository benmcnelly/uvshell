import argparse
import os
import shutil
import subprocess
from pathlib import Path


def _ensure_uv_exists() -> None:
    if shutil.which("uv") is None:
        raise SystemExit("uv is not installed or not on PATH. Install with: pip install uv")


def _ensure_venv(venv_dir: Path, python: str | None) -> None:
    if venv_dir.exists():
        return
    _ensure_uv_exists()
    cmd = ["uv", "venv", str(venv_dir)]
    if python:
        cmd += ["--python", python]
    subprocess.run(cmd, check=True)


def _posix_shell() -> str:
    return os.environ.get("SHELL") or "/bin/bash"


def _spawn_windows_cmd_subshell(venv_dir: Path) -> None:
    scripts = venv_dir / "Scripts"
    activate_bat = scripts / "activate.bat"

    if not activate_bat.exists():
        raise SystemExit(f"Could not find: {activate_bat}")

    # Use subprocess.call (not exec) to avoid weird console-host behavior.
    # This blocks until the user types `exit`, then returns to the parent shell.
    rc = subprocess.call(["cmd.exe", "/k", str(activate_bat)])
    raise SystemExit(rc)


def _spawn_posix_subshell(venv_dir: Path) -> None:
    activate = venv_dir / "bin" / "activate"
    if not activate.exists():
        raise SystemExit(f"Could not find: {activate}")

    sh = _posix_shell()
    # Start a NEW interactive shell, source venv, then stay there
    cmd = f"source '{activate}' && exec '{sh}' -i"
    os.execvp(sh, [sh, "-i", "-c", cmd])


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(
        prog="uvshell",
        description="Enter a uv-created .venv in a subshell (pipenv/poetry-like).",
    )
    p.add_argument("--venv", default=".venv", help="Venv directory (default: .venv)")
    p.add_argument("--python", default=None, help="Passed to `uv venv --python ...` when creating.")
    p.add_argument("--no-create", action="store_true", help="Do not create the venv if missing; error instead.")
    args = p.parse_args(argv)

    venv_dir = Path(args.venv).resolve()

    if not venv_dir.exists():
        if args.no_create:
            raise SystemExit(f"No venv found at {venv_dir}")
        _ensure_venv(venv_dir, args.python)

    if os.name == "nt":
        _spawn_windows_cmd_subshell(venv_dir)
    else:
        _spawn_posix_subshell(venv_dir)


if __name__ == "__main__":
    main()