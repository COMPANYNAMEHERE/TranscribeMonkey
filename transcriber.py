# transcriber.py
import whisper
import ffmpeg
import os
import warnings

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
            raise Exception(f"FFmpeg probe error: {e.stderr.decode()}")

    def split_audio(self, audio_path, chunk_length=15, download_path='downloads'):  # Decreasing chunk length to reduce memory usage
        """
        Splits the audio file into chunks of specified length.
        """
        duration = self.get_audio_duration(audio_path)
        num_chunks = int(duration // chunk_length) + 1
        chunk_paths = []

        for i in range(num_chunks):
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
            except ffmpeg.Error as e:
                raise Exception(f"FFmpeg error during chunk extraction: {e.stderr.decode()}")

        return chunk_paths

    def transcribe_chunks(self, chunk_paths, language=None, progress_callback=None):
        """
        Transcribes each audio chunk and detects language if set to automatic.
        Returns a list of transcripts and the detected language code.
        """
        transcripts = []
        detected_language = None
        total_chunks = len(chunk_paths)

        for idx, chunk in enumerate(chunk_paths):
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
                    progress_callback((idx + 1) / total_chunks * 100)

            except Exception as e:
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
            raise Exception(f"FFmpeg conversion error: {e.stderr.decode()}")

