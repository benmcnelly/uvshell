# uvshell

Simple command to enter a Python virtual environment created with `uv`.

`uvshell` creates a local `.venv` if it doesn’t exist and opens a new shell session with the environment activated. Exit the shell to return to your normal environment.

---

## What it does

- Creates a `.venv` using `uv` if one does not exist
- Opens a new interactive shell with the virtual environment activated
- Works across Windows, macOS, and Linux
- Keeps your workflow to a single command

---

## Installation

### Install with uv (recommended)

```bash
uv pip install uvshell
```

or install as a global tool:

```bash
uv tool install uvshell
```

### Install with pip

```bash
pip install uvshell
```

## Requirements

- Python 3.9+
- `uv` installed and available in your PATH

Install `uv` if needed:

```bash
pip install uv
```

or:

```bash
brew install uv
```

---

## Usage

From your project directory:

```bash
uvshell
```

Behavior:

- If `.venv` does not exist → it will be created
- A new shell opens with the virtual environment active
- Type `exit` to leave the environment

---

## Options

### Use a different virtual environment directory

```bash
uvshell --venv .venv-dev
```

### Specify Python version when creating environment

```bash
uvshell --python 3.13
```

### Error if environment is missing

```bash
uvshell --no-create
```

---

## Example Workflow

```bash
git clone my-project
cd my-project
uvshell
# work normally inside environment
exit
```

---

## License

Apache License 2.0