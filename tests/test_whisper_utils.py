"""Tests for Whisper model utility functions."""

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile

from src import whisper_utils


class TestWhisperUtils(unittest.TestCase):
    """Validate model download logic and installation checks."""

    @patch("src.whisper_utils.urllib.request.urlopen")
    @patch("src.whisper_utils.Path.home")
    @patch.object(whisper_utils, "whisper")
    def test_download_whisper_model_with_progress(self, mock_whisper, mock_home, mock_urlopen):
        """Model download writes file and reports progress."""
        # Prepare temporary directory to act as cache
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_home.return_value = Path(tmpdir)

            # Configure model URL with embedded SHA256
            data = b"testdata"
            sha256 = "810ff2fb242a5dee4220f2cb0e6a519891fb67f2f828a6cab4ef8894633b1f50"
            url = f"https://host/{sha256}/model.bin"
            mock_whisper._MODELS = {"dummy": url}

            # Mock HTTP response
            resp = MagicMock()
            resp.read = MagicMock(side_effect=[data, b""])
            resp.__enter__.return_value = resp
            resp.info.return_value = {"Content-Length": str(len(data))}
            mock_urlopen.return_value = resp

            progress = []

            def cb(percent, eta):
                progress.append(percent)

            whisper_utils.download_whisper_model("dummy", progress_callback=cb)

            # File saved
            cache_file = Path(tmpdir) / ".cache" / "whisper" / "model.bin"
            self.assertTrue(cache_file.is_file())
            self.assertEqual(cache_file.read_bytes(), data)
            # Callback invoked
            self.assertTrue(progress)
            self.assertEqual(progress[-1], 100.0)

    def test_is_whisper_model_installed(self):
        """Detect existing model files in cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".cache" / "whisper"
            cache_dir.mkdir(parents=True)
            model_file = cache_dir / "small.pt"
            model_file.write_bytes(b"dummy")

            with patch("src.whisper_utils.Path.home", return_value=Path(tmpdir)):
                self.assertTrue(whisper_utils.is_whisper_model_installed("small"))
                self.assertFalse(whisper_utils.is_whisper_model_installed("base"))


if __name__ == "__main__":
    unittest.main()
