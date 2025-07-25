# translator.py
from googletrans import Translator as GoogleTranslator

from .logger import get_logger

logger = get_logger(__name__)

class Translator:
    def __init__(self):
        self.translator = GoogleTranslator()

    def translate_text(self, text, target_language='en'):
        try:
            translated = self.translator.translate(text, dest=target_language)
            return translated.text
        except Exception as e:
            logger.error("Translation error: %s", e)
            return text  # Fallback to original text

