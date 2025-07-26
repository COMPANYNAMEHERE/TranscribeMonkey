"""Load and save user configuration settings."""

import json
import os
import tempfile
import tkinter as tk
from tkinter import filedialog

from ..logger import get_logger

logger = get_logger(__name__)

# Path to the settings file where user configurations are saved
# Path to the settings file located alongside this module
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

# Default settings used if no settings file is found
DEFAULT_SETTINGS = {
    'chunk_length': 30,  # Length of audio chunks in seconds for processing
    'model_variant': 'base',  # The model variant to use for transcription (e.g., tiny, base, small)
    'language': 'Automatic Detection',  # Default language setting for automatic detection
    'output_format': 'srt',  # Format of the output transcript (e.g., srt, vtt, txt)
    'output_directory': 'output',  # Directory where output files will be saved
    'delete_temp_files': True,  # Whether temporary files should be deleted after processing
    'translate': False,  # Whether to enable translation after transcription
    'target_language': 'English',  # Default target language for translation
    'show_system_status': True,  # Display GPU/Whisper/Translator info in the GUI
    'normalize_audio': True,  # Apply volume normalization before transcription
    'reduce_noise': False,  # Apply basic noise reduction
    'trim_silence': False  # Trim leading and trailing silence
}

def load_settings():
    """
    Loads settings from the settings file if it exists, otherwise returns default settings.
    """
    if os.path.exists(SETTINGS_FILE):  # Check if the settings file exists
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged = DEFAULT_SETTINGS.copy()
                merged.update(data)
                return merged
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Error reading settings file: %s. Using default settings.", e)
            return DEFAULT_SETTINGS.copy()  # Return default settings if JSON is invalid or there is an OS error
    else:
        return DEFAULT_SETTINGS.copy()  # Return a shallow copy of the default settings if the file is not found

def save_settings(settings):
    """
    Saves the provided settings to the settings file.
    """
    try:
        # Use a temporary file to ensure atomic writes
        settings_dir = os.path.dirname(SETTINGS_FILE)
        os.makedirs(settings_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile('w', delete=False, dir=settings_dir, encoding='utf-8') as tmp_file:
            json.dump(settings, tmp_file, indent=4)  # Write settings to the temporary file with pretty formatting for readability
            temp_file_name = tmp_file.name
        # Rename the temporary file to the target settings file
        os.replace(temp_file_name, SETTINGS_FILE)
    except (OSError, IOError) as e:
        logger.error("Error saving settings to file: %s", e)
    except TypeError as e:
        logger.error("Error serializing settings: %s", e)

def select_output_directory(settings):
    """
    Opens a GUI folder selector to set the output directory.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    selected_directory = filedialog.askdirectory(title="Select Output Directory")
    if selected_directory:
        settings['output_directory'] = selected_directory
        save_settings(settings)  # Save the updated settings
        logger.info("Output directory set to: %s", selected_directory)
    else:
        logger.info("No directory selected. Keeping the current output directory.")

