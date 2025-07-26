# Contribution Guide for Agents

TranscribeMonkey is a Tkinter-based desktop app for downloading, transcribing,
and optionally translating audio files. Automated contributors should adhere to
the following conventions.

## Style
- Follow **PEP 8** with 4‑space indentation and `lower_snake_case` for
  functions.
- Provide docstrings for public classes and functions.
- Add any third‑party packages to `requirements.txt`.

## Repository Layout
The project uses a simple directory structure:

- `src/` – core utilities
- `gui/` – Tkinter interface modules
- `processor/` – transcription and translation logic
- `tests/` – unit tests
- `resources/` – static assets like icons
- `main.py` in the repository root launches the GUI

Do **not** commit generated content such as `output/`, `downloads/` or
`__pycache__/`.

## Required Checks
Before committing run:

```bash
python -m py_compile src/*.py gui/*.py processor/*.py main.py setup_env.py
python -m unittest discover tests
```

All files must compile successfully and the tests should pass.

## Commit Practices
- Write concise commit messages.
- Never commit API keys or personal settings.
