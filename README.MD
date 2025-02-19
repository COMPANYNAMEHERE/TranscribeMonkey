# TranscribeMonkey

TranscribeMonkey is a desktop application. It allows users to download, transcribe, and translate audio files. It is ideal for content creators, researchers, and educators who need to process audio files efficiently. TranscribeMonkey supports audio from YouTube and local files, using OpenAI's Whisper for transcription and Google Translate for optional translation. Built with a Tkinter GUI, it processes audio in smaller, manageable chunks and offers various transcription options.

## Features

- **Download Audio from YouTube**: Easily download and save YouTube audio in MP3 format.
- **Transcription**: Transcribe audio using OpenAI's Whisper models for accurate results.
- **Translation**: Translate transcriptions into various target languages using Google Translate.
- **SRT Formatting**: Generates `.srt` subtitle files for compatibility with video players.
- **Progress Display**: Displays progress for download, transcription, and translation tasks, including ETAs.

## Requirements

Ensure you have Python 3.7 or higher installed on your system. You can find a Python installation guide [here](https://www.python.org/downloads/).

To install dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Dependencies include:

- `yt-dlp` for downloading YouTube audio.
- `ffmpeg-python` for audio processing.
- `openai-whisper` for transcription.
- `googletrans` for translation.

## Setup

1. **Configure Settings**: Modify `settings.json` as needed. You can find an example [here](settings_example.json) or refer to the snippet below, e.g., `"chunk_length": 30` to set the audio chunk length to 30 seconds:

   - **General Settings**:
     - `chunk_length`: Length of audio chunks in seconds.
     - `model_variant`: Whisper model to use (e.g., `tiny`, `base`, `large`).
     - `delete_temp_files`: Whether to delete temporary files after processing.

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
2. Enter a YouTube URL or select a local file to transcribe.
3. Configure settings (e.g., chunk length, output directory).
4. Click "Download and Transcribe" or "Transcribe File".
5. Note that the transcription process may take some time depending on the file size, audio quality, and your system's performance. Typically, it may take anywhere from a few minutes for short files to an hour or more for longer recordings, especially on older hardware.
6. Once processing is complete, you can find the output files in the directory specified under `output_directory` in the settings. Verify that the output directory path is correct and accessible to avoid any issues.

## File Structure

- `downloader.py`: Downloads and converts YouTube audio.
- `transcriber.py`: Handles audio splitting and transcription.
- `translator.py`: Translates transcriptions.
- `srt_formatter.py`: Corrects and formats `.srt` subtitles.
- `gui.py`: Defines the Tkinter GUI.
- `settings.json`: User configuration file.
- `utils.py`: Helper functions, including opening output folders.

## FAQ / Help

**Q: How do I change the output file format?**
A: Modify the `output_format` field in `settings.json` to change the output file format. Supported formats are `srt`, `vtt`, and `txt`.

**Q: The app is not detecting my audio language correctly. What should I do?**
A: Specify the correct language in the `language` setting under `settings.json`. If set to "Automatic Detection", Whisper will attempt to detect the language, but specifying it can improve accuracy.

**Q: What should I do if my output directory is inaccessible?**
A: Ensure that the output directory specified in `settings.json` exists and that you have the necessary permissions to write to it.

**Q: Can I use a different Whisper model variant?**
A: Yes, specify the model variant (`tiny`, `base`, `large`, etc.) in `settings.json` under `model_variant` to suit your needs.

**Q: Where can I find my output files?**
A: Once processing is complete, the output files are saved in the directory specified under `output_directory` in the settings.

**Q: Why isn't the progress bar showing the model download progress?**
A: Currently, the model download step is not reflected in the progress bar. This feature is planned for future updates.

## TODO

### Transcription Enhancements
- Implement batch processing to allow users to transcribe multiple files at once.
- Add more customizable transcription settings, such as output formats and processing modes.
- Add more advanced audio quality settings for finer control.

### User Interface Improvements
- Improve GUI layout for a more user-friendly experience.
- Add model download progress to the progress bar.
- Improve user feedback during processing for better responsiveness.

### User Experience Features
- Add error handling for network issues during YouTube download.
- Implement a feature to pause and resume downloads.
- Add a logging feature to keep a record of transcriptions and translations.
- Create a detailed user manual with screenshots.

