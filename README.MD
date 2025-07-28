# TranscribeMonkey

TranscribeMonkey is a desktop application. It allows users to download, transcribe, and translate audio files. It is ideal for content creators, researchers, and educators who need to process audio files efficiently. TranscribeMonkey supports audio from YouTube and local files, using OpenAI's Whisper for transcription and Google Translate for optional translation. Built with a Tkinter GUI, it processes audio in smaller, manageable chunks and offers various transcription options.

## Features

- **Download Audio from YouTube**: Easily download and save YouTube audio in MP3 format.
- **Safe Filenames**: Files are saved using the video ID so special characters in titles no longer cause errors.
- **Transcription**: Transcribe audio using OpenAI's Whisper models for accurate results.
- **Translation**: Translate transcriptions into various target languages using Google Translate.
- **SRT Formatting**: Generates `.srt` subtitle files for compatibility with video players.
- **Progress Display**: Displays progress for download, transcription, and translation tasks, including ETAs.
- **Detailed Progress**: Displays chunk creation, transcription, and translation progress with stage-specific updates.
- **Automatic Conversion**: Converts input audio to 16 kHz mono WAV for optimal AI analysis.
- **Audio Preprocessing**: Optional normalization, noise reduction, and silence trimming.
- **System Status**: Window focuses on launch and, when enabled, shows CUDA, Whisper model, and translation availability. The Whisper indicator turns red if the selected model is not installed.
- **Resizable Settings**: The settings window is larger and can be resized so all options fit comfortably.
- **Stop Button**: Cancel ongoing downloads or transcriptions safely.

## Requirements

Ensure you have Python 3.7 or higher installed on your system. You can find a Python installation guide [here](https://www.python.org/downloads/).

To install dependencies listed in `requirements.txt` manually:

```bash
pip install -r requirements.txt
```

Alternatively, run the setup script to automate this process:

```bash
python setup_env.py
```

Dependencies include:

- `yt-dlp` for downloading YouTube audio.
- `ffmpeg-python` for audio processing.
- `openai-whisper` for transcription.
- `googletrans` for translation.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/TranscribeMonkey.git
   cd TranscribeMonkey
   ```

2. **Run the setup script** (creates a conda environment and installs dependencies):

   ```bash
   python setup_env.py
   ```

3. **Start the program**:

   ```bash
   conda activate transcribemonkey
   python main.py
   ```

## Setup

1. **Configure Settings**: Modify `settings/settings.json` as needed. You can find an example [here](settings_example.json) or refer to the snippet below, e.g., `"chunk_length": 30` to set the audio chunk length to 30 seconds:

   - **General Settings**:
     - `chunk_length`: Length of audio chunks in seconds.
     - `model_variant`: Whisper model to use (e.g., `tiny`, `base`, `large`).
   - `delete_temp_files`: Whether to delete temporary files after processing.
   - `show_system_status`: Toggle display of GPU, Whisper, and translator availability.

   - **Language Options**:
     - `language`: Language for transcription or set to "Automatic Detection".
     - `translate`: Enable or disable translation.
     - `target_language`: Target language for translation if enabled.

   - **Output Options**:
     - `output_format`: Choose output format (`srt`, `vtt`, `txt`).
     - `output_directory`: Directory where output files will be saved.

2. **Run the App**:

```bash
python main.py
```

## Usage

1. Launch the app with `python main.py`.
2. Use the tabs to either enter a YouTube URL or browse for a local file.
3. Configure settings (e.g., chunk length, output directory).
4. Click the button on each tab to begin transcription.
5. Note that the transcription process may take some time depending on the file size, audio quality, and your system's performance. Typically, it may take anywhere from a few minutes for short files to an hour or more for longer recordings, especially on older hardware.
6. Once processing is complete, you can find the output files in the directory specified under `output_directory` in the settings. Verify that the output directory path is correct and accessible to avoid any issues.

## File Structure

- `src/` contains all application modules:
  - `gui.py` – the Tkinter GUI
  - `downloader.py` – YouTube audio downloader
  - `transcriber.py` – audio splitting and Whisper integration
  - `translator.py` – translation utilities
  - `srt_formatter.py` – subtitle formatting helpers
  - `logger.py` – centralized logging setup
  - `utils.py` – small helper functions
- `resources/` stores static files such as `icon.png`
- `tests/` includes unit tests
- `main.py` is the entry point
- `settings/settings.json` holds user configuration

## FAQ / Help

**Q: How do I change the output file format?**
A: Modify the `output_format` field in `settings/settings.json` to change the output file format. Supported formats are `srt`, `vtt`, and `txt`.

**Q: The app is not detecting my audio language correctly. What should I do?**
A: Specify the correct language in the `language` setting under `settings/settings.json`. If set to "Automatic Detection", Whisper will attempt to detect the language, but specifying it can improve accuracy.

**Q: What should I do if my output directory is inaccessible?**
A: Ensure that the output directory specified in `settings/settings.json` exists and that you have the necessary permissions to write to it.

**Q: Can I use a different Whisper model variant?**
A: Yes, specify the model variant (`tiny`, `base`, `large`, etc.) in `settings/settings.json` under `model_variant` to suit your needs.

**Q: Where can I find my output files?**
A: Once processing is complete, the output files are saved in the directory specified under `output_directory` in the settings.

**Q: I get a "Failed to load audio" error. What does it mean?**
A: The app attempts to convert unsupported files to a standard WAV format automatically. If conversion fails, try converting the file manually or ensure FFmpeg is installed.

**Q: Why isn't the progress bar showing the model download progress?**
A: Currently, the model download step is not reflected in the progress bar. This feature is planned for future updates.

## TODO

- [ ] Batch transcription to process multiple files at once
- [ ] Display Whisper model download progress in the GUI
- [ ] Pause and resume downloads and transcriptions
- [ ] Save a persistent log of completed tasks
- [ ] Write a detailed user manual with screenshots
- [ ] Multiple speaker recognition


## Logging

All runtime information and errors are logged to `app.log` in the project root. Check this file when troubleshooting issues.
Set the environment variable `DEBUG=1` before launching the app to enable
verbose debug messages in the log.


## Testing

Run the unit tests to verify core functionality:

```bash
python -m unittest discover tests
```

The tests mock external services, so they run offline and check settings handling, subtitle formatting, and translation logic.
