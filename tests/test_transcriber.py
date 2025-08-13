"""Tests for the Transcriber class."""

import unittest
from unittest.mock import patch, call, Mock

from processor.transcriber import Transcriber


class TestTranscriber(unittest.TestCase):
    """Ensure transcription logic selects the proper device."""

    @patch('processor.transcriber.whisper.load_model')
    @patch('processor.transcriber.torch')
    def test_mps_fallback_on_error(self, mock_torch, mock_load_model):
        """Fallback to CPU if MPS load fails."""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = True
        mock_torch.backends.mps.is_built.return_value = True
        mock_load_model.side_effect = [RuntimeError('fail'), object()]

        tr = Transcriber()

        self.assertEqual(tr.device, 'cpu')
        self.assertEqual(mock_load_model.call_args_list, [
            call('base', device='mps'),
            call('base', device='cpu'),
        ])

    @patch('processor.transcriber.whisper.load_model')
    @patch('processor.transcriber.torch')
    def test_transcribe_chunks_offsets_timestamps(self, mock_torch, mock_load_model):
        """Offset chunk timestamps so subtitles align with the original audio."""
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = False

        mock_model = Mock()
        mock_model.transcribe.side_effect = [
            {'segments': [{'start': 0, 'end': 5, 'text': 'Hello'}], 'language': 'en'},
            {'segments': [{'start': 0, 'end': 4, 'text': 'World'}]},
        ]
        mock_load_model.return_value = mock_model

        tr = Transcriber()

        segments, detected = tr.transcribe_chunks(
            ['chunk0.mp3', 'chunk1.mp3'],
            chunk_length=15,
        )

        self.assertEqual(detected, 'en')
        self.assertEqual(segments[0]['start'], 0)
        self.assertEqual(segments[1]['start'], 15)
        self.assertEqual(segments[1]['end'], 19)


if __name__ == '__main__':
    unittest.main()
