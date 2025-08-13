"""Whisper model utilities.

Provide helpers for checking and downloading Whisper models."""

from pathlib import Path
from typing import Callable, Optional
import hashlib
import time
import urllib.request
import whisper


def is_whisper_model_installed(variant: str) -> bool:
    """Return ``True`` if the specified Whisper model file exists locally."""
    cache_dir = Path.home() / ".cache" / "whisper"
    return (cache_dir / f"{variant}.pt").is_file()


def download_whisper_model(
    variant: str,
    progress_callback: Optional[Callable[[float, Optional[float]], None]] = None,
) -> None:
    """Download a Whisper model with optional progress reporting.

    Parameters
    ----------
    variant : str
        Name of the Whisper model variant, e.g. ``"base"``.
    progress_callback : Callable[[float, float | None], None], optional
        Callback receiving the download percentage and ETA in seconds.
    """

    url = whisper._MODELS.get(variant)
    if not url:
        raise ValueError(f"Unknown Whisper model variant: {variant}")

    cache_dir = Path.home() / ".cache" / "whisper"
    cache_dir.mkdir(parents=True, exist_ok=True)
    target_path = cache_dir / Path(url).name

    if target_path.exists():
        return

    expected_sha256 = url.split("/")[-2]

    with urllib.request.urlopen(url) as source, open(target_path, "wb") as output:
        total = int(source.info().get("Content-Length", 0))
        downloaded = 0
        start_time = time.time()
        while True:
            chunk = source.read(8192)
            if not chunk:
                break
            output.write(chunk)
            downloaded += len(chunk)
            if progress_callback and total:
                percent = downloaded / total * 100
                elapsed = time.time() - start_time
                rate = downloaded / elapsed if elapsed else 0
                eta = (total - downloaded) / rate if rate else None
                progress_callback(percent, eta)

    model_bytes = target_path.read_bytes()
    if hashlib.sha256(model_bytes).hexdigest() != expected_sha256:
        target_path.unlink(missing_ok=True)
        raise RuntimeError("Model download checksum mismatch")
