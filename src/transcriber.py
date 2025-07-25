# transcriber.py
import whisper
import ffmpeg
import os
import warnings

from .logger import get_logger

logger = get_logger(__name__)

# Set environment variable to improve CUDA memory handling
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

class Transcriber:
    def __init__(self, model_variant='base'):
        # Suppress the FutureWarning from Whisper regarding torch.load
        warnings.filterwarnings("ignore", category=FutureWarning, module="whisper")
        
        self.model = whisper.load_model(model_variant)

    def get_audio_duration(self, audio_path):
        """
        Retrieves the duration of the audio file in seconds.
        """
        try:
            probe = ffmpeg.probe(audio_path)
            return float(probe['format']['duration'])
        except ffmpeg.Error as e:
            logger.error("FFmpeg probe error: %s", e.stderr.decode())
            raise Exception(f"FFmpeg probe error: {e.stderr.decode()}")

    def split_audio(self, audio_path, chunk_length=15, download_path='downloads',
                    progress_callback=None, stop_event=None):  # Decreasing chunk length to reduce memory usage
        """Split the audio file into chunks of the given length.

        Parameters
        ----------
        audio_path : str
            Path to the source audio file.
        chunk_length : int, optional
            Length in seconds for each chunk, by default ``15``.
        download_path : str, optional
            Folder where chunk files are stored, by default ``'downloads'``.
        progress_callback : callable, optional
            Called with ``(percent, idx, total, stage)`` to report progress.
        stop_event : threading.Event, optional
            Event to allow cancellation of the splitting process.
        """
        duration = self.get_audio_duration(audio_path)
        num_chunks = int(duration // chunk_length) + 1
        chunk_paths = []

        for i in range(num_chunks):
            if stop_event and stop_event.is_set():
                break
            start_time = i * chunk_length
            end_time = min((i + 1) * chunk_length, duration)
            chunk_filename = os.path.join(download_path, f"chunk_{i}.mp3")
            try:
                (
                    ffmpeg
                    .input(audio_path, ss=start_time, t=chunk_length)
                    .output(chunk_filename, format='mp3', acodec='libmp3lame', loglevel="error")
                    .overwrite_output()
                    .run()
                )
                chunk_paths.append(chunk_filename)

                if progress_callback:
                    progress_callback((i + 1) / num_chunks * 100,
                                     i + 1,
                                     num_chunks,
                                     stage="Chunk Creation")
            except ffmpeg.Error as e:
                logger.error(
                    "FFmpeg error during chunk extraction: %s",
                    e.stderr.decode(),
                )
                raise Exception(f"FFmpeg error during chunk extraction: {e.stderr.decode()}")

        return chunk_paths

    def transcribe_chunks(self, chunk_paths, language=None,
                          progress_callback=None, stop_event=None):
        """Transcribe a list of audio chunks.

        Parameters
        ----------
        chunk_paths : list[str]
            List of paths to audio chunks.
        language : str | None, optional
            Language code or ``None`` for auto-detection.
        progress_callback : callable | None, optional
            Called with ``(percent, idx, total, stage)`` to report progress.
        stop_event : threading.Event | None, optional
            Allows canceling the process mid-way.

        Returns
        -------
        tuple[list[dict], str | None]
            Transcription segments and detected language code.
        """
        transcripts = []
        detected_language = None
        total_chunks = len(chunk_paths)

        for idx, chunk in enumerate(chunk_paths):
            if stop_event and stop_event.is_set():
                break
            language_param = language  # Already set to None if automatic

            try:
                # Transcribe the chunk
                result = self.model.transcribe(chunk, language=language_param)
                segments = result.get('segments', [])
                transcripts.extend(segments)

                # Detect language after the first chunk if automatic
                if language is None and not detected_language:
                    detected_lang_code = result.get('language', 'unknown')
                    detected_language = detected_lang_code  # Return code to map to name elsewhere

                # Update progress
                if progress_callback:
                    progress_callback(
                        (idx + 1) / total_chunks * 100,
                        idx + 1,
                        total_chunks,
                        stage="Transcription"
                    )

            except Exception as e:
                logger.error("Whisper transcription error: %s", e)
                msg = str(e)
                if "Failed to load audio" in msg:
                    msg = (
                        "Failed to load audio. The file may use an unsupported "
                        "codec or be corrupted."
                    )
                raise Exception(f"Whisper transcription error: {msg}")

        return transcripts, detected_language

    def convert_to_audio(self, file_path, out_dir='downloads'):
        """Convert a media file to 16 kHz mono WAV for Whisper.

        Parameters
        ----------
        file_path : str
            Path to the source media file.
        out_dir : str, optional
            Directory for the converted file, defaults to ``'downloads'``.

        Returns
        -------
        str
            Path to the converted WAV file.
        """
        audio_path = os.path.join(out_dir, 'temp_audio.wav')
        try:
            (
                ffmpeg
                .input(file_path)
                .output(
                    audio_path,
                    format='wav',
                    acodec='pcm_s16le',
                    ac=1,
                    ar=16000,
                    loglevel='error',
                )
                .overwrite_output()
                .run()
            )
            return audio_path
        except ffmpeg.Error as e:
            logger.error("FFmpeg conversion error: %s", e.stderr.decode())
            raise Exception(f"FFmpeg conversion error: {e.stderr.decode()}")

