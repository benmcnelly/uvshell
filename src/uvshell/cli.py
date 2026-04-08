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

    # Initialize uv project if needed
    if not Path("pyproject.toml").exists():
        init_cmd = ["uv", "init"]
        if python:
            init_cmd += ["--python", python]
        subprocess.run(init_cmd, check=True)

        for file_to_remove in ["main.py", "hello.py"]:
            p = Path(file_to_remove)
            if p.exists():
                p.unlink()

    # Ensure .gitignore has .venv
    gitignore = Path(".gitignore")
    ignore_entry = f"{venv_dir.name}/\n"
    if not gitignore.exists():
        gitignore.write_text(f"# Virtual env\n{ignore_entry}")
    else:
        content = gitignore.read_text()
        if ignore_entry.strip() not in content and venv_dir.name not in content:
            with gitignore.open("a") as f:
                if not content.endswith("\n"):
                    f.write("\n")
                f.write(f"\n# Virtual env\n{ignore_entry}")

    # Optionally ensure .python-version if python is explicitly passed
    if python and not Path(".python-version").exists():
        Path(".python-version").write_text(f"{python}\n")

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

    import tempfile

    sh = _posix_shell()
    sh_name = Path(sh).name

    if sh_name == "bash":
        fd, rc_path = tempfile.mkstemp(suffix=".bashrc")
        with os.fdopen(fd, "w") as f:
            f.write(f"""
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi
source "{activate}"
rm -f "{rc_path}"
""")
        os.execvpe(sh, [sh, "--rcfile", rc_path, "-i"], os.environ)
    elif sh_name == "zsh":
        zdotdir = tempfile.mkdtemp(prefix="uvshell_zsh_")
        rc_path = Path(zdotdir) / ".zshrc"

        # Save original ZDOTDIR
        orig_zdotdir = os.environ.get("ZDOTDIR")

        # We need to unset ZDOTDIR in the child process so nested zsh shells don't look in the deleted dir
        # or restore it to its original value if it existed
        restore_zdotdir = f'export ZDOTDIR="{orig_zdotdir}"' if orig_zdotdir else "unset ZDOTDIR"

        # Determine the user's real .zshrc
        # If orig_zdotdir is set, it's there. Otherwise, it's in ~/.zshrc
        real_zshrc_dir = orig_zdotdir if orig_zdotdir else "~"
        real_zshrc = f"{real_zshrc_dir}/.zshrc"

        with open(rc_path, "w") as f:
            f.write(f"""
if [ -f {real_zshrc} ]; then
    source {real_zshrc}
fi
source "{activate}"
{restore_zdotdir}
rm -rf "{zdotdir}"
""")
        env = os.environ.copy()
        env["ZDOTDIR"] = zdotdir
        os.execvpe(sh, [sh, "-i"], env)
    else:
        # Fallback for other shells: print a message and start interactive shell.
        # It's hard to automatically source an arbitrary shell without knowing its init flag.
        print(f"uvshell: starting {sh}. Please run `source {activate}` to activate the virtual environment.")
        os.execvpe(sh, [sh, "-i"], os.environ)


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