# translator.py
import time

from googletrans import Translator as GoogleTranslator
from deep_translator import MyMemoryTranslator

from src.logger import get_logger

logger = get_logger(__name__)


class Translator:
    """Translate text with retries and a fallback provider."""

    def __init__(self, retries=3, retry_delay=1.0):
        """Initialize the translator.

        Parameters
        ----------
        retries : int, optional
            Number of attempts for the primary translator, by default ``3``.
        retry_delay : float, optional
            Seconds to wait between retries, by default ``1.0``.
        """
        self.translator = GoogleTranslator()
        self.retries = retries
        self.retry_delay = retry_delay

    def translate_text(self, text, target_language='en'):
        """Translate text to the target language with retry and fallback.

        Parameters
        ----------
        text : str
            Text to translate.
        target_language : str, optional
            Language code to translate into, by default ``'en'``.

        Returns
        -------
        str
            Translated text or the original text if all providers fail.
        """
        for attempt in range(1, self.retries + 1):
            try:
                translated = self.translator.translate(text, dest=target_language)
                return translated.text
            except Exception as e:
                logger.error(
                    "Translation attempt %d/%d failed: %s",
                    attempt,
                    self.retries,
                    e,
                )
                time.sleep(self.retry_delay)

        try:
            return MyMemoryTranslator(
                source="auto", target=target_language
            ).translate(text)
        except Exception as e:
            logger.error("Fallback translation error: %s", e)
            return text

