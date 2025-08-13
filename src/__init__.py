"""TranscribeMonkey application package."""

from .file_utils import open_output_folder
from .whisper_utils import is_whisper_model_installed

__all__ = [
    "open_output_folder",
    "is_whisper_model_installed",
]
