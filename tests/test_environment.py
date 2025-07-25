import os
import tempfile
import unittest
from unittest.mock import patch

import src.settings as settings
from src.settings import load_settings, save_settings, DEFAULT_SETTINGS
from src.srt_formatter import (
    parse_srt,
    time_to_seconds,
    seconds_to_time,
    format_srt,
    correct_srt_format,
)
from src.translator import Translator


class TestSettings(unittest.TestCase):
    """Tests for settings load and save functions."""

    def test_load_defaults_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp_file = os.path.join(tmp, 'settings.json')
            with patch.object(settings, 'SETTINGS_FILE', temp_file):
                loaded = load_settings()
                self.assertEqual(loaded, DEFAULT_SETTINGS)

    def test_save_and_load_settings(self):
        sample_settings = {"chunk_length": 10}
        with tempfile.TemporaryDirectory() as tmp:
            temp_file = os.path.join(tmp, 'settings.json')
            with patch.object(settings, 'SETTINGS_FILE', temp_file):
                save_settings(sample_settings)
                loaded = load_settings()
                self.assertEqual(loaded["chunk_length"], 10)


class TestSrtFormatter(unittest.TestCase):
    """Tests for SRT formatting utilities."""

    SAMPLE_SRT = """1
00:00:00,000 --> 00:00:01,000
Hello

2
00:00:01,000 --> 00:00:02,000
World
"""

    def test_parse_and_format(self):
        entries = parse_srt(self.SAMPLE_SRT)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]['text'], 'Hello')
        formatted = format_srt(entries)
        self.assertIn('1', formatted)
        corrected = correct_srt_format(self.SAMPLE_SRT)
        self.assertIn('World', corrected)

    def test_time_conversions(self):
        seconds = time_to_seconds('00:00:10,500')
        self.assertAlmostEqual(seconds, 10.5)
        time_str = seconds_to_time(10.5)
        self.assertEqual(time_str, '00:00:10,500')


class TestTranslator(unittest.TestCase):
    """Tests for the Translator class using mocks."""

    @patch('src.translator.GoogleTranslator')
    def test_translate_text(self, mock_google):
        mock_instance = mock_google.return_value
        mock_instance.translate.return_value.text = 'Hola'
        tr = Translator()
        result = tr.translate_text('Hello', 'es')
        mock_instance.translate.assert_called_once_with('Hello', dest='es')
        self.assertEqual(result, 'Hola')



if __name__ == "__main__":
    unittest.main()

