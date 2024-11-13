# settings.py
import json
import os
import copy
import tempfile
import tkinter as tk
from tkinter import filedialog

# Path to the settings file where user configurations are saved
SETTINGS_FILE = 'settings.json'

# Default settings used if no settings file is found
DEFAULT_SETTINGS = {
    'chunk_length': 30,  # Length of audio chunks in seconds for processing
    'model_variant': 'base',  # The model variant to use for transcription (e.g., tiny, base, small)
    'language': 'Automatic Detection',  # Default language setting for automatic detection
    'output_format': 'srt',  # Format of the output transcript (e.g., srt, vtt, txt)
    'output_directory': 'output',  # Directory where output files will be saved
    'delete_temp_files': True,  # Whether temporary files should be deleted after processing
    'translate': False,  # Whether to enable translation after transcription
    'target_language': 'English'  # Default target language for translation
}

def load_settings():
    """
    Loads settings from the settings file if it exists, otherwise returns default settings.
    """
    if os.path.exists(SETTINGS_FILE):  # Check if the settings file exists
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)  # Load settings from the file
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error reading settings file: {e}. Using default settings.")
            return DEFAULT_SETTINGS.copy()  # Return default settings if JSON is invalid or there is an OS error
    else:
        return DEFAULT_SETTINGS.copy()  # Return a shallow copy of the default settings if the file is not found

def save_settings(settings):
    """
    Saves the provided settings to the settings file.
    """
    try:
        # Use a temporary file to ensure atomic writes
        with tempfile.NamedTemporaryFile('w', delete=False, dir=os.path.dirname(SETTINGS_FILE), encoding='utf-8') as tmp_file:
            json.dump(settings, tmp_file, indent=4)  # Write settings to the temporary file with pretty formatting for readability
            temp_file_name = tmp_file.name
        # Rename the temporary file to the target settings file
        os.replace(temp_file_name, SETTINGS_FILE)
    except (OSError, IOError) as e:
        print(f"Error saving settings to file: {e}")  # Handle file-related errors, such as permissions or disk space issues
    except TypeError as e:
        print(f"Error serializing settings: {e}")  # Handle serialization errors if settings contain non-serializable data types

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
        print(f"Output directory set to: {selected_directory}")
    else:
        print("No directory selected. Keeping the current output directory.")

