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

    def transcribe_chunks(self, chunk_paths, language=None, progress_callback=None, stop_event=None):
        """Transcribe a list of audio chunks.

        :param chunk_paths: List of paths to audio chunks.
        :param language: Language code or ``None`` for auto-detection.
        :param progress_callback: Optional callback receiving progress percent, current chunk index, and total chunks.
        :param stop_event: Optional ``threading.Event`` to stop processing.
        :return: Tuple of transcripts list and detected language code.
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
                    progress_callback((idx + 1) / total_chunks * 100, idx + 1, total_chunks)

            except Exception as e:
                logger.error("Whisper transcription error: %s", e)
                raise Exception(f"Whisper transcription error: {e}")

        return transcripts, detected_language

    def convert_to_audio(self, file_path):
        """
        Converts the given audio/video file to MP3 format.
        """
        audio_path = os.path.join('downloads', 'temp_audio.mp3')
        try:
            (
                ffmpeg
                .input(file_path)
                .output(audio_path, format='mp3', acodec='libmp3lame', loglevel="error")
                .overwrite_output()
                .run()
            )
            return audio_path
        except ffmpeg.Error as e:
            logger.error("FFmpeg conversion error: %s", e.stderr.decode())
            raise Exception(f"FFmpeg conversion error: {e.stderr.decode()}")

