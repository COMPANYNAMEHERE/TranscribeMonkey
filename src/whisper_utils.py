"""Whisper model utilities.

Provide helpers related to local Whisper model availability."""

from pathlib import Path


def is_whisper_model_installed(variant: str) -> bool:
    """Return True if the specified Whisper model file exists locally."""
    cache_dir = Path.home() / ".cache" / "whisper"
    return (cache_dir / f"{variant}.pt").is_file()
