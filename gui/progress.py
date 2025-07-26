"""Utility functions for formatting progress messages."""

from __future__ import annotations


def format_progress(stage: str, percent: float, idx: int | None = None,
                    total: int | None = None, target_language: str = "N/A") -> str:
    """Return a formatted progress message for display in the GUI.

    Parameters
    ----------
    stage : str
        Name of the processing stage, e.g. ``"Transcription"``.
    percent : float
        Completion percentage from 0 to 100.
    idx : int | None, optional
        Current chunk index, if applicable.
    total : int | None, optional
        Total number of chunks, if applicable.
    target_language : str, optional
        Language label to display, default ``"N/A"``.

    Returns
    -------
    str
        A human-readable progress message.
    """
    chunk_info = ""
    if idx is not None and total is not None:
        chunk_info = f" (Chunk {idx}/{total})"

    if stage == "Transcription":
        lang_text = "Language: Detecting..."
    elif stage == "Translation":
        lang_text = f"Language: {target_language}"
    else:
        lang_text = "Language: N/A"

    return f"{stage} Progress: {int(percent)}%{chunk_info} | {lang_text}"
