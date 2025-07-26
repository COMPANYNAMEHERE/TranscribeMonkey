"""Settings window implementation."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from src.settings.settings import save_settings
from src.logger import get_logger

# Recompute language options locally to avoid circular import
try:
    from googletrans import LANGUAGES
    LANGUAGE_OPTIONS = [('Automatic Detection', 'auto')] + sorted(
        [(name.title(), code) for code, name in LANGUAGES.items()],
        key=lambda x: x[0]
    )
except Exception:  # pragma: no cover - googletrans may not be installed
    LANGUAGE_OPTIONS = [('Automatic Detection', 'auto')]

LANGUAGE_NAME_TO_CODE = {name: code for name, code in LANGUAGE_OPTIONS}

logger = get_logger(__name__)


def open_settings(gui):
    """Open the settings window for the given GUI."""
    settings_window = tk.Toplevel(gui.root)
    settings_window.title("Settings")
    settings_window.geometry("600x550")
    settings_window.resizable(True, True)

    notebook = ttk.Notebook(settings_window)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)

    general_tab = ttk.Frame(notebook)
    process_tab = ttk.Frame(notebook)
    output_tab = ttk.Frame(notebook)
    about_tab = ttk.Frame(notebook)

    notebook.add(general_tab, text='General')
    notebook.add(process_tab, text='Process')
    notebook.add(output_tab, text='Output')
    notebook.add(about_tab, text='About')

    # General Tab Options
    tk.Label(general_tab, text="Chunk Length (seconds):").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    chunk_length_var = tk.IntVar(value=gui.settings.get('chunk_length', 30))
    tk.Entry(general_tab, textvariable=chunk_length_var).grid(row=0, column=1, padx=10, pady=10)

    tk.Label(general_tab, text="Whisper Model Variant:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    model_var = tk.StringVar(value=gui.settings.get('model_variant', 'base'))
    model_options = ['tiny', 'base', 'small', 'medium', 'large']
    tk.OptionMenu(general_tab, model_var, *model_options).grid(row=1, column=1, padx=10, pady=10, sticky='w')

    tk.Label(general_tab, text="Transcription Language:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
    language_var = tk.StringVar(value=gui.settings.get('language', 'Automatic Detection'))
    language_names = [name for name, _ in LANGUAGE_OPTIONS]
    language_menu = ttk.Combobox(general_tab, textvariable=language_var, values=language_names, state='readonly')
    language_menu.grid(row=2, column=1, padx=10, pady=10, sticky='w')
    language_menu.set(gui.settings.get('language', 'Automatic Detection'))

    tk.Label(general_tab, text="Show System Status:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
    show_status_var = tk.BooleanVar(value=gui.settings.get('show_system_status', True))
    tk.Checkbutton(general_tab, variable=show_status_var).grid(row=3, column=1, padx=10, pady=10, sticky='w')

    # Process Tab Options
    tk.Label(process_tab, text="Normalize Audio:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    normalize_var = tk.BooleanVar(value=gui.settings.get('normalize_audio', True))
    tk.Checkbutton(process_tab, variable=normalize_var).grid(row=0, column=1, padx=10, pady=10, sticky='w')

    tk.Label(process_tab, text="Reduce Noise:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    reduce_noise_var = tk.BooleanVar(value=gui.settings.get('reduce_noise', False))
    tk.Checkbutton(process_tab, variable=reduce_noise_var).grid(row=1, column=1, padx=10, pady=10, sticky='w')

    tk.Label(process_tab, text="Trim Silence:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
    trim_silence_var = tk.BooleanVar(value=gui.settings.get('trim_silence', False))
    tk.Checkbutton(process_tab, variable=trim_silence_var).grid(row=2, column=1, padx=10, pady=10, sticky='w')

    tk.Label(process_tab, text="Enable Translation:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
    translate_var = tk.BooleanVar(value=gui.settings.get('translate', False))
    target_lang_var = tk.StringVar(value=gui.settings.get('target_language', 'English'))
    translate_check = tk.Checkbutton(process_tab, variable=translate_var)
    translate_check.grid(row=3, column=1, padx=10, pady=10, sticky='w')

    tk.Label(process_tab, text="Target Language:").grid(row=4, column=0, padx=10, pady=10, sticky='e')
    target_language_names = [name for name, code in LANGUAGE_OPTIONS if code != 'auto']
    target_lang_menu = ttk.Combobox(process_tab, textvariable=target_lang_var, values=target_language_names, state='disabled')
    target_lang_menu.grid(row=4, column=1, padx=10, pady=10, sticky='w')
    target_lang_menu.set(gui.settings.get('target_language', 'English'))

    def toggle_translation_options(*_):
        if translate_var.get():
            target_lang_menu.config(state='readonly')
        else:
            target_lang_menu.config(state='disabled')

    translate_var.trace_add('write', lambda *_: toggle_translation_options())
    toggle_translation_options()

    # Output Tab Options
    tk.Label(output_tab, text="Output Format:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    format_var = tk.StringVar(value=gui.settings.get('output_format', 'srt'))
    format_options = ['srt', 'vtt', 'txt']
    tk.OptionMenu(output_tab, format_var, *format_options).grid(row=0, column=1, padx=10, pady=10, sticky='w')

    tk.Label(output_tab, text="Output Directory:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    output_dir_var = tk.StringVar(value=gui.settings.get('output_directory', 'output'))

    def select_output_directory():
        selected_directory = filedialog.askdirectory(title="Select Output Directory")
        if selected_directory:
            output_dir_var.set(selected_directory)

    tk.Button(output_tab, text="Select Folder", command=select_output_directory).grid(row=1, column=1, padx=10, pady=10, sticky='w')

    tk.Label(output_tab, text="Delete Temporary Files:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
    delete_temp_var = tk.BooleanVar(value=gui.settings.get('delete_temp_files', True))
    tk.Checkbutton(output_tab, variable=delete_temp_var).grid(row=2, column=1, padx=10, pady=10, sticky='w')

    # About Tab
    about_text = (
        "TranscribeMonkey downloads, processes and transcribes audio files using Whisper."
    )
    tk.Label(about_tab, text=about_text, wraplength=500, justify='left').pack(padx=10, pady=10, anchor='w')

    def save_local_settings():
        old_variant = gui.settings.get('model_variant', 'base')
        gui.settings['chunk_length'] = chunk_length_var.get()
        gui.settings['model_variant'] = model_var.get()
        gui.settings['language'] = language_var.get()
        gui.settings['output_format'] = format_var.get()
        gui.settings['output_directory'] = output_dir_var.get()
        gui.settings['delete_temp_files'] = delete_temp_var.get()
        gui.settings['translate'] = translate_var.get()
        gui.settings['target_language'] = target_lang_var.get()
        gui.settings['show_system_status'] = show_status_var.get()
        gui.settings['normalize_audio'] = normalize_var.get()
        gui.settings['reduce_noise'] = reduce_noise_var.get()
        gui.settings['trim_silence'] = trim_silence_var.get()
        if show_status_var.get():
            gui.status_frame.pack(anchor='ne', pady=5, padx=5)
            gui.check_system_status()
        else:
            gui.status_frame.pack_forget()
        if gui.settings['model_variant'] != old_variant:
            gui.transcriber = None
        save_settings(gui.settings)
        messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
        settings_window.destroy()

    tk.Button(settings_window, text="Save Settings", command=save_local_settings).pack(pady=10)

