# translator.py
from googletrans import Translator as GoogleTranslator

class Translator:
    def __init__(self):
        self.translator = GoogleTranslator()

    def translate_text(self, text, target_language='en'):
        try:
            translated = self.translator.translate(text, dest=target_language)
            return translated.text
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Fallback to original text

