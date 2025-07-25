# downloader.py
from yt_dlp import YoutubeDL
import os
import socket

from .logger import get_logger

logger = get_logger(__name__)

class DownloaderError(Exception):
    pass

class NetworkError(DownloaderError):
    pass

class AudioConversionError(DownloaderError):
    pass

class Downloader:
    """Utility class for downloading YouTube audio."""

    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def get_ydl_opts(self, download_path, progress_hook):
        """Return yt-dlp options for downloading a single video's audio."""
        opts = {
            'format': 'bestaudio/best',
            # Use the video ID as the file name to avoid problems with
            # special characters in titles causing rename errors
            'outtmpl': os.path.join(download_path, '%(id)s.%(ext)s'),
            'restrictfilenames': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'progress_hooks': [progress_hook]  # Attach the progress hook
        }
        logger.debug("yt-dlp options: %s", opts)
        return opts

    def download_audio(self, url, download_path='downloads', ydl_opts=None):
        """Download audio from a YouTube URL and return the path to the MP3."""
        logger.debug("Starting download: url=%s, download_path=%s", url, download_path)

        if not os.path.exists(download_path):
            try:
                os.makedirs(download_path)
            except OSError as e:
                logger.error("Failed to create directory '%s': %s", download_path, e)
                raise DownloaderError(f"Failed to create directory '{download_path}': {e}")
        
        # Define the progress hook function
        def progress_hook(d):
            try:
                if self.progress_callback:
                    self.progress_callback(d)
            except Exception as e:
                logger.error("Progress callback failed: %s", e)

        # Use provided ydl_opts or get default options
        if ydl_opts is None:
            ydl_opts = self.get_ydl_opts(download_path, progress_hook)

        try:
            logger.debug("Invoking yt-dlp with options: %s", ydl_opts)
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                if info_dict is None:
                    raise DownloaderError("Failed to retrieve video information.")
        except (socket.timeout, socket.gaierror) as e:
            logger.error("Network error during download: %s", e)
            raise NetworkError("Network error occurred while trying to download the video.")
        except Exception:
            logger.exception("Unexpected error during download")
            raise DownloaderError("An unexpected error occurred while trying to download the video.")

        logger.debug("yt-dlp returned info: %s", info_dict)
        audio_filename = ydl.prepare_filename(info_dict)
        audio_path = os.path.splitext(audio_filename)[0] + '.mp3'

        logger.debug("Expected audio path: %s", audio_path)

        if not os.path.exists(audio_path):
            raise AudioConversionError("Audio conversion failed.")

        logger.info("Downloaded audio saved to %s", audio_path)
        return audio_path

