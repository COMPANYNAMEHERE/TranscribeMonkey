"""Tests for the Transcriber class."""

import unittest
from unittest.mock import patch, call

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


if __name__ == '__main__':
    unittest.main()
