# downloader.py
from yt_dlp import YoutubeDL
import os
import logging
import socket

# Configure logging
logging.basicConfig(level=logging.INFO)

class DownloaderError(Exception):
    pass

class NetworkError(DownloaderError):
    pass

class AudioConversionError(DownloaderError):
    pass

class Downloader:
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def get_ydl_opts(self, download_path, progress_hook):
        return {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
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

    def download_audio(self, url, download_path='downloads', ydl_opts=None):
        if not os.path.exists(download_path):
            try:
                os.makedirs(download_path)
            except OSError as e:
                logging.error(f"Failed to create directory '{download_path}': {e}")
                raise DownloaderError(f"Failed to create directory '{download_path}': {e}")
        
        # Define the progress hook function
        def progress_hook(d):
            try:
                if self.progress_callback:
                    self.progress_callback(d)
            except Exception as e:
                logging.error(f"Progress callback failed: {e}")

        # Use provided ydl_opts or get default options
        if ydl_opts is None:
            ydl_opts = self.get_ydl_opts(download_path, progress_hook)

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                if info_dict is None:
                    raise DownloaderError("Failed to retrieve video information.")
        except (socket.timeout, socket.gaierror) as e:
            logging.error(f"Network error during download: {e}")
            raise NetworkError("Network error occurred while trying to download the video.")
        except Exception as e:
            logging.error(f"Unexpected error during download: {e}")
            raise DownloaderError("An unexpected error occurred while trying to download the video.")

        title = info_dict.get('title', 'output')
        audio_filename = ydl.prepare_filename(info_dict)
        audio_path = os.path.splitext(audio_filename)[0] + '.mp3'
        
        if not os.path.exists(audio_path):
            raise AudioConversionError("Audio conversion failed.")
        
        return audio_path

