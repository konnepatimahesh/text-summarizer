"""
Translation utilities using Google Translate API
"""

from googletrans import Translator, LANGUAGES
import logging

class TextTranslator:
    """Handle text translation between languages"""
    
    def __init__(self):
        self.translator = Translator()
        self.logger = logging.getLogger(__name__)
    
    def translate(self, text, target_lang='en', source_lang='auto'):
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'en', 'es')
            source_lang: Source language code (default: 'auto' for auto-detect)
            
        Returns:
            Translated text
        """
        try:
            # Handle empty text
            if not text or not text.strip():
                return text
            
            # Skip translation if source and target are the same
            if source_lang != 'auto' and source_lang == target_lang:
                return text
            
            # Translate
            result = self.translator.translate(
                text,
                src=source_lang,
                dest=target_lang
            )
            
            return result.text
            
        except Exception as e:
            self.logger.error(f"Translation error: {str(e)}")
            # Return original text if translation fails
            return text
    
    def detect_language(self, text):
        """
        Detect language of text
        
        Args:
            text: Input text
            
        Returns:
            Detected language code
        """
        try:
            result = self.translator.detect(text)
            return result.lang
        except Exception as e:
            self.logger.error(f"Language detection error: {str(e)}")
            return 'en'
    
    def translate_batch(self, texts, target_lang='en', source_lang='auto'):
        """
        Translate multiple texts
        
        Args:
            texts: List of texts to translate
            target_lang: Target language code
            source_lang: Source language code
            
        Returns:
            List of translated texts
        """
        try:
            results = []
            for text in texts:
                translated = self.translate(text, target_lang, source_lang)
                results.append(translated)
            return results
        except Exception as e:
            self.logger.error(f"Batch translation error: {str(e)}")
            return texts
    
    @staticmethod
    def get_supported_languages():
        """Get all supported language codes and names"""
        return LANGUAGES
    
    @staticmethod
    def is_language_supported(lang_code):
        """Check if language is supported"""
        return lang_code.lower() in LANGUAGES