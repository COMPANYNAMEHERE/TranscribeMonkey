# gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os

from .downloader import Downloader
from .transcriber import Transcriber
from .translator import Translator
from .settings import load_settings
from .settings.settings_gui import open_settings as open_settings_window
from .utils import open_output_folder, is_whisper_model_installed
from googletrans import LANGUAGES
from .srt_formatter import correct_srt_format  # Importing the SRT formatter
from .logger import get_logger
from .progress import format_progress

logger = get_logger(__name__)

LANGUAGE_OPTIONS = [('Automatic Detection', 'auto')] + sorted(
    [(name.title(), code) for code, name in LANGUAGES.items()], key=lambda x: x[0]
)
LANGUAGE_NAME_TO_CODE = {name: code for name, code in LANGUAGE_OPTIONS}
LANGUAGE_CODE_TO_NAME = {code: name for name, code in LANGUAGE_OPTIONS}

class TranscribeMonkeyGUI:
    def __init__(self, root):
        self.root = root
        self.settings = load_settings()
        self.transcriber = None
        self.stop_event = threading.Event()
        self.setup_window()  # Setup window title and icon
        self.create_widgets()
        self.check_system_status()
        # Bring window to the front on launch
        try:
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            self.root.focus_force()
        except Exception as e:
            logger.debug("Failed to set focus: %s", e)

    def setup_window(self):
        # Set window title
        self.root.title("Transcribe Monkey")

        # Set window icon
        # Icons are stored in the project's 'resources' folder
        icon_filename_windows = 'icon.ico'
        icon_filename_others = 'icon.png'
        project_root = os.path.dirname(os.path.dirname(__file__))
        resources_dir = os.path.join(project_root, 'resources')
        icon_path_windows = os.path.join(resources_dir, icon_filename_windows)
        icon_path_others = os.path.join(resources_dir, icon_filename_others)

        try:
            if os.name == 'nt':  # Windows
                if os.path.exists(icon_path_windows):
                    self.root.iconbitmap(icon_path_windows)
                else:
                    logger.warning(
                        "Windows icon file '%s' not found at %s. Skipping icon setting.",
                        icon_filename_windows,
                        icon_path_windows,
                    )
            else:  # macOS, Linux
                if os.path.exists(icon_path_others):
                    icon = tk.PhotoImage(file=icon_path_others)
                    self.root.iconphoto(True, icon)
                else:
                    logger.warning(
                        "Icon file '%s' not found at %s. Skipping icon setting.",
                        icon_filename_others,
                        icon_path_others,
                    )
        except Exception as e:
            logger.error("Failed to set window icon: %s", e)

    def create_widgets(self):
        """Create and layout all widgets in the main window."""
        # Status indicators at the top right
        self.status_frame = tk.Frame(self.root)
        if self.settings.get('show_system_status', True):
            self.status_frame.pack(anchor='ne', pady=5, padx=5)
        self.cuda_status = tk.Label(self.status_frame, text="")
        self.cuda_status.pack(side='right', padx=5)
        self.translate_status = tk.Label(self.status_frame, text="")
        self.translate_status.pack(side='right', padx=5)
        self.whisper_status = tk.Label(self.status_frame, text="")
        self.whisper_status.pack(side='right', padx=5)

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

        # Stop Button
        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_process, state='disabled')
        self.stop_button.pack(pady=5)

        # Status Label
        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=5)

        # ETA and Language Label
        self.eta_lang_label = tk.Label(self.root, text="ETA: N/A | Language: N/A")
        self.eta_lang_label.pack(pady=(0, 10))

    def check_system_status(self):
        """Update status indicators for CUDA, Whisper, and translation."""
        # CUDA availability
        cuda_color = "green"
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            cuda_color = "green" if cuda_available else "yellow"
            cuda_text = "CUDA" if cuda_available else "CPU"
        except Exception:
            cuda_color = "yellow"
            cuda_text = "No CUDA"
        self.cuda_status.config(text=cuda_text, fg=cuda_color)

        # Whisper model availability
        model_variant = self.settings.get('model_variant', 'base')
        try:
            import whisper  # noqa: F401
            if is_whisper_model_installed(model_variant):
                color = "green"
                text = f"Whisper ({model_variant})"
            else:
                color = "red"
                text = f"Whisper ({model_variant}) Missing"
        except Exception:
            color = "red"
            text = "Whisper Missing"
        self.whisper_status.config(text=text, fg=color)

        # Google Translate availability
        translate_required = self.settings.get('translate', False)
        try:
            import googletrans  # noqa: F401
            color = "green"
            text = "Translator"
        except Exception:
            color = "red" if translate_required else "yellow"
            text = "Translator Missing"
        self.translate_status.config(text=text, fg=color)

    def download_from_youtube(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Required", "Please enter a YouTube URL.")
            return
        self.start_task()
        threading.Thread(target=self.process_youtube, args=(url,), daemon=True).start()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio/Video File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.flac"), ("Video Files", "*.mp4 *.mkv *.avi *.mov"), ("All Files", "*.*")]
        )
        if file_path:
            self.start_task()
            threading.Thread(target=self.process_file, args=(file_path,), daemon=True).start()

    def open_settings(self):
        open_settings_window(self)

    def update_transcription_progress(self, percent, idx=None, total=None, stage="Transcription"):
        """Update progress information displayed to the user."""
        self.progress['value'] = percent
        msg = format_progress(
            stage,
            percent,
            idx=idx,
            total=total,
            target_language=self.settings.get('target_language', 'N/A'),
        )
        self.eta_lang_label.config(text=msg)
        self.root.update_idletasks()

    def get_transcriber(self):
        """Return a cached Transcriber instance for the selected model."""
        model_variant = self.settings.get('model_variant', 'base')
        if self.transcriber is None or self.transcriber.model_variant != model_variant:
            self.transcriber = Transcriber(model_variant=model_variant)
        return self.transcriber

    def start_task(self):
        """Prepare UI for a long running task."""
        self.stop_event.clear()
        self.stop_button.config(state='normal')
        self.download_button.config(state='disabled')
        self.file_button.config(state='disabled')

    def end_task(self):
        """Reset UI state after task completion."""
        self.stop_button.config(state='disabled')
        self.download_button.config(state='normal')
        self.file_button.config(state='normal')

    def stop_process(self):
        """Signal running threads to stop."""
        self.stop_event.set()
        self.status_label.config(text="Stopping...")

    def process_youtube(self, url):
        downloader = Downloader(progress_callback=self.update_progress, stop_event=self.stop_event)
        try:
            audio_path = downloader.download_audio(url)
            transcriber = self.get_transcriber()
            audio_path = transcriber.convert_to_audio(
                audio_path,
                normalize_audio=self.settings.get('normalize_audio', True),
                reduce_noise=self.settings.get('reduce_noise', False),
                trim_silence=self.settings.get('trim_silence', False),
            )
            self.status_label.config(text="Download and conversion complete. Starting transcription...")
            self.eta_lang_label.config(text="ETA: Calculating... | Language: N/A")
            self.progress['value'] = 0
            self.root.update_idletasks()

            self.transcribe_audio(audio_path, os.path.basename(audio_path))
        except Exception as e:
            if self.stop_event.is_set():
                self.status_label.config(text="Process stopped.")
            else:
                messagebox.showerror("Error", f"Failed to download or process YouTube video:\n{e}")
                self.status_label.config(text="Failed to download YouTube video.")
            self.progress['value'] = 0
            self.eta_lang_label.config(text="ETA: N/A | Language: N/A")
        finally:
            self.end_task()

    def process_file(self, file_path):
        transcriber = self.get_transcriber()
        try:
            # Convert to optimal format (16 kHz mono WAV)
            audio_path = transcriber.convert_to_audio(
                file_path,
                normalize_audio=self.settings.get('normalize_audio', True),
                reduce_noise=self.settings.get('reduce_noise', False),
                trim_silence=self.settings.get('trim_silence', False),
            )
            self.status_label.config(text="Conversion complete. Starting transcription...")
            self.eta_lang_label.config(text="ETA: Calculating... | Language: N/A")
            self.progress['value'] = 0
            self.root.update_idletasks()

            self.transcribe_audio(audio_path, os.path.basename(file_path))
        except Exception as e:
            if self.stop_event.is_set():
                self.status_label.config(text="Process stopped.")
            else:
                messagebox.showerror("Error", f"Failed to process file:\n{e}")
                self.status_label.config(text="Failed to process file.")
            self.progress['value'] = 0
            self.eta_lang_label.config(text="ETA: N/A | Language: N/A")
        finally:
            self.end_task()

    def transcribe_audio(self, audio_path, base_name):
        transcriber = self.get_transcriber()
        translator = Translator() if self.settings.get('translate', False) else None

        try:
            duration = transcriber.get_audio_duration(audio_path)
            chunk_length = self.settings.get('chunk_length', 30)
            self.progress['value'] = 0
            self.status_label.config(text="Splitting audio into chunks...")
            self.eta_lang_label.config(text="Chunk Creation Progress: 0% | Language: N/A")
            self.root.update_idletasks()
            chunk_paths = transcriber.split_audio(
                audio_path,
                chunk_length=chunk_length,
                progress_callback=self.update_transcription_progress,
                stop_event=self.stop_event,
            )

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
                progress_callback=self.update_transcription_progress,
                stop_event=self.stop_event
            )

            if self.stop_event.is_set():
                self.status_label.config(text="Process stopped.")
                return

            # Map detected language code to language name
            if selected_language == 'Automatic Detection' and detected_lang_code:
                detected_language = LANGUAGE_CODE_TO_NAME.get(detected_lang_code, 'Unknown')
            else:
                detected_language = selected_language

            # Translate if enabled
            if translator:
                self.progress['value'] = 0
                self.status_label.config(text="Translating transcript...")
                self.eta_lang_label.config(
                    text=f"Translation Progress: 0% | Language: {detected_language}"
                )
                self.root.update_idletasks()
                for idx, segment in enumerate(transcripts):
                    if self.stop_event.is_set():
                        self.status_label.config(text="Process stopped.")
                        return
                    segment['translated_text'] = translator.translate_text(
                        segment['text'],
                        target_language=LANGUAGE_NAME_TO_CODE.get(
                            self.settings.get('target_language'), 'en'
                        )
                    )
                    self.update_transcription_progress(
                        (idx + 1) / len(transcripts) * 100,
                        idx + 1,
                        len(transcripts),
                        stage="Translation",
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
            if self.stop_event.is_set():
                self.status_label.config(text="Process stopped.")
            else:
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
        if self.stop_event.is_set():
            return
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
