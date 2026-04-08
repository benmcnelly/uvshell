# uvshell

Open a shell inside a local `uv` virtual environment.

`uvshell` creates a local `.venv` if it does not exist and opens a new shell session with the environment activated. Exit the shell to return to your normal environment.

## What It Does

- Creates a `.venv` using `uv` if one does not exist
- Initializes a `uv` project first if `pyproject.toml` is missing
- Marks newly initialized projects with `tool.uv.package = false` by default
- Opens a new interactive shell with the virtual environment activated
- Works across Windows, macOS, and Linux

## Installation

### Install From PyPI With uv

```bash
uv tool install uvshell
```

or:

```bash
uv pip install uvshell
```

### Install With pip

```bash
pip install uvshell
```

### Install From a Local Build

```bash
pip install dist/uvshell-0.1.4-py3-none-any.whl
```

## Requirements

- Python 3.9+
- `uv` installed and available on `PATH`

Install `uv` if needed:

```bash
pip install uv
```

or:

```bash
brew install uv
```

## Usage

From your project directory:

```bash
uvshell
```

Behavior:

- If `.venv` does not exist, it will be created
- If `pyproject.toml` does not exist, `uvshell` runs `uv init` first
- New auto-initialized projects default to `tool.uv.package = false`
- On Windows, `uvshell` opens a `cmd.exe` subshell
- Type `exit` to leave the environment

## Options

### Use a Different Virtual Environment Directory

```bash
uvshell --venv .venv-dev
```

### Specify Python When Creating the Environment

```bash
uvshell --python 3.13
```

### Initialize as a Packaged Project

```bash
uvshell --package
```

Use this if you want `uvshell` to create a packaged `uv` project when it has to run `uv init`.

### Error If the Environment Is Missing

```bash
uvshell --no-create
```

## Example Workflow

```bash
mkdir my-project
cd my-project
uvshell
exit
```

## Local Smoke Test

```powershell
python -m pip uninstall -y uvshell
python -m pip install .\dist\uvshell-0.1.4-py3-none-any.whl

mkdir C:\temp\uvshell-smoke
cd C:\temp\uvshell-smoke
uvshell --python 3.13
```

After `uvshell` starts, confirm that `.venv`, `.gitignore`, and optionally `.python-version` were created as expected.

## License

Apache License 2.0
