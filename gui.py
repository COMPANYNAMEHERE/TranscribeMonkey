# gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os

from downloader import Downloader
from transcriber import Transcriber
from translator import Translator
from settings import load_settings, save_settings
from utils import open_output_folder
from googletrans import LANGUAGES
from srt_formatter import correct_srt_format  # Importing the SRT formatter

LANGUAGE_OPTIONS = [('Automatic Detection', 'auto')] + sorted(
    [(name.title(), code) for code, name in LANGUAGES.items()], key=lambda x: x[0]
)
LANGUAGE_NAME_TO_CODE = {name: code for name, code in LANGUAGE_OPTIONS}
LANGUAGE_CODE_TO_NAME = {code: name for name, code in LANGUAGE_OPTIONS}

class TranscribeMonkeyGUI:
    def __init__(self, root):
        self.root = root
        self.settings = load_settings()
        self.setup_window()  # Setup window title and icon
        self.create_widgets()

    def setup_window(self):
        # Set window title
        self.root.title("Transcribe Monkey")

        # Set window icon
        # Make sure 'icon.ico' or 'icon.png' is in the same directory as gui.py
        icon_filename_windows = 'icon.ico'
        icon_filename_others = 'icon.png'
        current_dir = os.path.dirname(__file__)
        icon_path_windows = os.path.join(current_dir, icon_filename_windows)
        icon_path_others = os.path.join(current_dir, icon_filename_others)

        try:
            if os.name == 'nt':  # Windows
                if os.path.exists(icon_path_windows):
                    self.root.iconbitmap(icon_path_windows)
                else:
                    print(f"Windows icon file '{icon_filename_windows}' not found at {icon_path_windows}. Skipping icon setting.")
            else:  # macOS, Linux
                if os.path.exists(icon_path_others):
                    icon = tk.PhotoImage(file=icon_path_others)
                    self.root.iconphoto(True, icon)
                else:
                    print(f"Icon file '{icon_filename_others}' not found at {icon_path_others}. Skipping icon setting.")
        except Exception as e:
            print(f"Failed to set window icon: {e}")

    def create_widgets(self):
        # YouTube URL Entry
        self.url_label = tk.Label(self.root, text="Enter YouTube URL:")
        self.url_label.pack(pady=(10, 0))

        self.url_entry = tk.Entry(self.root, width=60)
        self.url_entry.pack(pady=5)

        self.download_button = tk.Button(self.root, text="Download and Transcribe from YouTube", command=self.download_from_youtube)
        self.download_button.pack(pady=5)

        # Separator
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', pady=10)

        # File Selection
        self.file_button = tk.Button(self.root, text="Browse Files to Transcribe", command=self.open_file)
        self.file_button.pack(pady=5)

        # Settings Button
        self.settings_button = tk.Button(self.root, text="Settings", command=self.open_settings)
        self.settings_button.pack(pady=5)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=10)

        # Status Label
        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=5)

        # ETA and Language Label
        self.eta_lang_label = tk.Label(self.root, text="ETA: N/A | Language: N/A")
        self.eta_lang_label.pack(pady=(0, 10))

    def download_from_youtube(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Required", "Please enter a YouTube URL.")
            return
        threading.Thread(target=self.process_youtube, args=(url,), daemon=True).start()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio/Video File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac"), ("Video Files", "*.mp4 *.mkv *.avi *.mov"), ("All Files", "*.*")]
        )
        if file_path:
            threading.Thread(target=self.process_file, args=(file_path,), daemon=True).start()

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x450")
        settings_window.resizable(False, False)

        # Chunk Length
        tk.Label(settings_window, text="Chunk Length (seconds):").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        chunk_length_var = tk.IntVar(value=self.settings.get('chunk_length', 30))
        tk.Entry(settings_window, textvariable=chunk_length_var).grid(row=0, column=1, padx=10, pady=10)

        # Model Variant
        tk.Label(settings_window, text="Whisper Model Variant:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        model_var = tk.StringVar(value=self.settings.get('model_variant', 'base'))
        model_options = ['tiny', 'base', 'small', 'medium', 'large']
        tk.OptionMenu(settings_window, model_var, *model_options).grid(row=1, column=1, padx=10, pady=10, sticky='w')

        # Language
        tk.Label(settings_window, text="Transcription Language:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        language_var = tk.StringVar(value=self.settings.get('language', 'Automatic Detection'))
        language_names = [name for name, code in LANGUAGE_OPTIONS]
        language_menu = ttk.Combobox(settings_window, textvariable=language_var, values=language_names, state='readonly')
        language_menu.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        language_menu.set(self.settings.get('language', 'Automatic Detection'))  # Set to saved value

        # Output Format
        tk.Label(settings_window, text="Output Format:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        format_var = tk.StringVar(value=self.settings.get('output_format', 'srt'))
        format_options = ['srt', 'vtt', 'txt']
        tk.OptionMenu(settings_window, format_var, *format_options).grid(row=3, column=1, padx=10, pady=10, sticky='w')

        # Output Directory
        tk.Label(settings_window, text="Output Directory:").grid(row=4, column=0, padx=10, pady=10, sticky='e')
        output_dir_var = tk.StringVar(value=self.settings.get('output_directory', 'output'))

        def select_output_directory():
            selected_directory = filedialog.askdirectory(title="Select Output Directory")
            if selected_directory:
                output_dir_var.set(selected_directory)

        tk.Button(settings_window, text="Select Folder", command=select_output_directory).grid(row=4, column=1, padx=10, pady=10, sticky='w')

        # Delete Temporary Files
        tk.Label(settings_window, text="Delete Temporary Files:").grid(row=5, column=0, padx=10, pady=10, sticky='e')
        delete_temp_var = tk.BooleanVar(value=self.settings.get('delete_temp_files', True))
        tk.Checkbutton(settings_window, variable=delete_temp_var).grid(row=5, column=1, padx=10, pady=10, sticky='w')

        # Translation Settings
        # Enable Translation
        tk.Label(settings_window, text="Enable Translation:").grid(row=6, column=0, padx=10, pady=10, sticky='e')
        translate_var = tk.BooleanVar(value=self.settings.get('translate', False))
        translate_check = tk.Checkbutton(settings_window, variable=translate_var, command=lambda: toggle_translation_options(translate_var, target_lang_menu))
        translate_check.grid(row=6, column=1, padx=10, pady=10, sticky='w')

        # Target Language
        tk.Label(settings_window, text="Target Language:").grid(row=7, column=0, padx=10, pady=10, sticky='e')
        target_lang_var = tk.StringVar(value=self.settings.get('target_language', 'English'))
        target_language_names = [name for name, code in LANGUAGE_OPTIONS if code != 'auto']
        target_lang_menu = ttk.Combobox(settings_window, textvariable=target_lang_var, values=target_language_names, state='disabled')
        target_lang_menu.grid(row=7, column=1, padx=10, pady=10, sticky='w')
        target_lang_menu.set(self.settings.get('target_language', 'English'))  # Set to saved value

        # Function to enable/disable target language selection
        def toggle_translation_options(translate_var, target_lang_menu):
            if translate_var.get():
                target_lang_menu.config(state='readonly')
            else:
                target_lang_menu.config(state='disabled')

        # Renamed the nested function to avoid conflict
        def save_local_settings():
            self.settings['chunk_length'] = chunk_length_var.get()
            self.settings['model_variant'] = model_var.get()
            self.settings['language'] = language_var.get()
            self.settings['output_format'] = format_var.get()
            self.settings['output_directory'] = output_dir_var.get()
            self.settings['delete_temp_files'] = delete_temp_var.get()
            self.settings['translate'] = translate_var.get()
            self.settings['target_language'] = target_lang_var.get()
            save_settings(self.settings)  # Call the imported save_settings function
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
            settings_window.destroy()

        # Save Button now calls save_local_settings instead of save_settings
        tk.Button(settings_window, text="Save Settings", command=save_local_settings).grid(row=8, column=0, columnspan=2, pady=20)

    def update_transcription_progress(self, percent):
        """
        Updates the progress bar and label during transcription.
        
        :param percent: Float representing the percentage of transcription completed.
        """
        self.progress['value'] = percent
        self.eta_lang_label.config(text=f"Transcription Progress: {int(percent)}% | Language: Detecting...")
        self.root.update_idletasks()

    def process_youtube(self, url):
        downloader = Downloader(progress_callback=self.update_progress)
        try:
            audio_path = downloader.download_audio(url)
            self.status_label.config(text="Download complete. Starting transcription...")
            self.eta_lang_label.config(text="ETA: Calculating... | Language: N/A")
            self.progress['value'] = 0
            self.root.update_idletasks()

            self.transcribe_audio(audio_path, os.path.basename(audio_path))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download or process YouTube video:\n{e}")
            self.status_label.config(text="Failed to download YouTube video.")
            self.progress['value'] = 0
            self.eta_lang_label.config(text="ETA: N/A | Language: N/A")

    def process_file(self, file_path):
        transcriber = Transcriber(model_variant=self.settings.get('model_variant', 'base'))
        try:
            # Convert to mp3 if necessary
            audio_path = transcriber.convert_to_audio(file_path)
            self.status_label.config(text="Conversion complete. Starting transcription...")
            self.eta_lang_label.config(text="ETA: Calculating... | Language: N/A")
            self.progress['value'] = 0
            self.root.update_idletasks()

            self.transcribe_audio(audio_path, os.path.basename(file_path))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file:\n{e}")
            self.status_label.config(text="Failed to process file.")
            self.progress['value'] = 0
            self.eta_lang_label.config(text="ETA: N/A | Language: N/A")

    def transcribe_audio(self, audio_path, base_name):
        transcriber = Transcriber(model_variant=self.settings.get('model_variant', 'base'))
        translator = Translator() if self.settings.get('translate', False) else None

        try:
            duration = transcriber.get_audio_duration(audio_path)
            chunk_length = self.settings.get('chunk_length', 30)
            chunk_paths = transcriber.split_audio(audio_path, chunk_length=chunk_length)

            # Determine the language parameter
            selected_language = self.settings.get('language')
            if selected_language == 'Automatic Detection':
                language = None  # Enable automatic language detection
            else:
                language = LANGUAGE_NAME_TO_CODE.get(selected_language, None)

            # Reset progress bar and update labels for transcription
            self.progress['value'] = 0
            self.eta_lang_label.config(text="Transcription Progress: 0% | Language: Detecting...")
            self.status_label.config(text="Starting transcription...")
            self.root.update_idletasks()

            # Start transcription with progress callback
            transcripts, detected_lang_code = transcriber.transcribe_chunks(
                chunk_paths,
                language=language,
                progress_callback=self.update_transcription_progress
            )

            # Map detected language code to language name
            if selected_language == 'Automatic Detection' and detected_lang_code:
                detected_language = LANGUAGE_CODE_TO_NAME.get(detected_lang_code, 'Unknown')
            else:
                detected_language = selected_language

            # Translate if enabled
            if translator:
                for segment in transcripts:
                    segment['translated_text'] = translator.translate_text(
                        segment['text'],
                        target_language=LANGUAGE_NAME_TO_CODE.get(self.settings.get('target_language'), 'en')
                    )

            # Format transcript
            srt_content = self.format_transcript(transcripts)

            # Correct SRT formatting
            try:
                corrected_srt = correct_srt_format(srt_content)
            except Exception as e:
                raise Exception(f"SRT formatting failed: {e}")

            # Save corrected .srt file
            output_filename = f"{base_name}.{self.settings.get('output_format', 'srt')}"
            output_dir = self.settings.get('output_directory', 'output')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(corrected_srt)

            # Delete temporary audio file if enabled
            if self.settings.get('delete_temp_files', True):
                os.remove(audio_path)

            # Finalize progress bar and labels
            self.status_label.config(text="Transcription successful!")
            self.progress['value'] = 100
            self.eta_lang_label.config(text=f"ETA: 0 seconds | Language: {detected_language}")
            self.root.update_idletasks()

            # Prompt to open output folder
            if messagebox.askyesno("Transcription Complete", "Transcription successful! Do you want to open the file location?"):
                open_output_folder(output_path)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to transcribe audio:\n{e}")
            self.status_label.config(text="Failed to transcribe audio.")
            self.progress['value'] = 0
            self.eta_lang_label.config(text="ETA: N/A | Language: N/A")

    def format_transcript(self, segments):
        srt_counter = 1
        srt_text = ""
        for segment in segments:
            start = self.format_time(segment['start'])
            end = self.format_time(segment['end'])
            # Use translated_text if available, else use original text
            text = segment.get('translated_text', segment['text']).strip()

            srt_text += f"{srt_counter}\n{start} --> {end}\n{text}\n\n"
            srt_counter += 1
        return srt_text

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    def update_progress(self, d):
        """
        Updates the progress bar and label during download.
        
        :param d: Dictionary containing download status information.
        """
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes:
                percentage = downloaded_bytes / total_bytes * 100
                self.progress['value'] = percentage
                # Update ETA (in seconds)
                eta = d.get('eta')
                if eta is not None:
                    self.eta_lang_label.config(text=f"ETA: {int(eta)} seconds | Language: N/A")
                else:
                    self.eta_lang_label.config(text="ETA: N/A | Language: N/A")
        elif d['status'] == 'finished':
            self.progress['value'] = 100
            self.eta_lang_label.config(text="ETA: 0 seconds | Language: N/A")

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = TranscribeMonkeyGUI(root)
    root.mainloop()
