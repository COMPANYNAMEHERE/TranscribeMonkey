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
- All source modules live in the repository root; avoid new directories unless
  absolutely necessary.
- Do **not** commit generated content such as `output/`, `downloads/` or
  `__pycache__/`.
- GUI logic stays in `gui.py`; download/transcribe/translate logic remains in
  their respective modules.

## Required Checks
Before committing run:

```bash
python -m py_compile *.py
```

All files must compile successfully. If additional tests are introduced, run
those as well.

## Commit Practices
- Write concise commit messages.
- Update `README.MD` when user-facing behavior changes.
- Never commit API keys or personal settings.
