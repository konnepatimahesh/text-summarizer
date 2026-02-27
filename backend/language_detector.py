"""
Language detection and translation utilities
"""

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent results
DetectorFactory.seed = 0

class LanguageDetector:
    """Detect and manage language operations"""
    
    # Supported languages with their codes and names
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'zh-cn': 'Chinese (Simplified)',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'bn': 'Bengali',
        'te': 'Telugu',
        'ta': 'Tamil',
        'mr': 'Marathi',
        'ur': 'Urdu',
        'nl': 'Dutch',
        'tr': 'Turkish',
        'pl': 'Polish'
    }
    
    # Multilingual summarization models
    MULTILINGUAL_MODELS = {
        'mbart': 'facebook/mbart-large-50',
        'mt5': 'google/mt5-base',
        'mT5-small': 'google/mt5-small'
    }
    
    @staticmethod
    def detect_language(text):
        """
        Detect the language of input text
        
        Args:
            text: Input text string
            
        Returns:
            Language code (e.g., 'en', 'es', 'fr')
        """
        try:
            lang_code = detect(text)
            return lang_code
        except LangDetectException:
            # Default to English if detection fails
            return 'en'
    
    @staticmethod
    def get_language_name(lang_code):
        """Get full language name from code"""
        return LanguageDetector.SUPPORTED_LANGUAGES.get(
            lang_code, 
            'Unknown'
        )
    
    @staticmethod
    def is_supported(lang_code):
        """Check if language is supported"""
        return lang_code in LanguageDetector.SUPPORTED_LANGUAGES
    
    @staticmethod
    def get_all_languages():
        """Get list of all supported languages"""
        return [
            {'code': code, 'name': name}
            for code, name in LanguageDetector.SUPPORTED_LANGUAGES.items()
        ]
    
    @staticmethod
    def normalize_language_code(lang_code):
        """Normalize language code variations"""
        # Map common variations to standard codes
        code_map = {
            'zh': 'zh-cn',
            'zh-hans': 'zh-cn',
            'zh-hant': 'zh-cn',
            'pa': 'pa'
        }
        return code_map.get(lang_code.lower(), lang_code.lower())