"""
Multilingual text summarization with translation support - FULLY FIXED
"""

from transformers import pipeline, MBartForConditionalGeneration, MBart50TokenizerFast
from language_detector import LanguageDetector
from translator import TextTranslator
import logging
import re

class MultilingualSummarizer:
    """Handle summarization in multiple languages"""
    
    def __init__(self):
        self.translator = TextTranslator()
        self.language_detector = LanguageDetector()
        self.logger = logging.getLogger(__name__)
        
        # Multilingual model (lazy loading)
        self.mbart_model = None
        self.mbart_tokenizer = None
    
    def _load_mbart_model(self):
        """Load mBART multilingual model"""
        if self.mbart_model is None:
            self.logger.info("Loading mBART multilingual model...")
            self.mbart_model = MBartForConditionalGeneration.from_pretrained(
                "facebook/mbart-large-50-many-to-many-mmt"
            )
            self.mbart_tokenizer = MBart50TokenizerFast.from_pretrained(
                "facebook/mbart-large-50-many-to-many-mmt"
            )
    
    def summarize_multilingual(
        self, 
        text, 
        target_lang='en',
        method='translate',
        max_length=150,
        min_length=50
    ):
        """
        Summarize text in any language
        
        Args:
            text: Input text in any language
            target_lang: Language for summary output
            method: 'translate' or 'native'
            max_length: Maximum summary length
            min_length: Minimum summary length
            
        Returns:
            dict with summary and language info
        """
        try:
            # Detect input language
            detected_lang = self.language_detector.detect_language(text)
            lang_name = self.language_detector.get_language_name(detected_lang)
            
            self.logger.info(f"Detected language: {lang_name} ({detected_lang})")
            self.logger.info(f"Input text length: {len(text)} chars, {len(text.split())} words")
            
            if method == 'translate':
                return self._translate_and_summarize(
                    text, 
                    detected_lang, 
                    target_lang,
                    max_length,
                    min_length
                )
            else:
                return self._native_summarize(
                    text,
                    detected_lang,
                    target_lang,
                    max_length,
                    min_length
                )
                
        except Exception as e:
            self.logger.error(f"Multilingual summarization error: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise
    
    def _chunk_text(self, text, max_words=400):
        """Split text into manageable chunks"""
        # Split by sentences
        sentences = re.split(r'[.!?]+\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            words_in_sentence = len(sentence.split())
            
            if current_word_count + words_in_sentence > max_words and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_word_count = words_in_sentence
            else:
                current_chunk.append(sentence)
                current_word_count += words_in_sentence
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        self.logger.info(f"Split into {len(chunks)} chunks")
        return chunks
    
    def _translate_and_summarize(
        self,
        text,
        source_lang,
        target_lang,
        max_length,
        min_length
    ):
        """Translate, summarize, and translate back"""
        from summarizer import TextSummarizer
        summarizer = TextSummarizer()
        
        word_count = len(text.split())
        self.logger.info(f"Starting summarization: {word_count} words")
        
        # STEP 1: Translate to English if needed
        if source_lang != 'en':
            self.logger.info(f"Translating from {source_lang} to English...")
            
            if word_count > 500:
                self.logger.info("Text is long, chunking for translation...")
                chunks = self._chunk_text(text, max_words=400)
                translated_chunks = []
                
                for i, chunk in enumerate(chunks):
                    self.logger.info(f"Translating chunk {i+1}/{len(chunks)} ({len(chunk.split())} words)...")
                    try:
                        translated = self.translator.translate(chunk, 'en', source_lang)
                        if translated and len(translated.strip()) > 20:
                            translated_chunks.append(translated)
                            self.logger.info(f"✓ Chunk {i+1} translated ({len(translated.split())} words)")
                        else:
                            self.logger.warning(f"✗ Chunk {i+1} translation too short, using original")
                            translated_chunks.append(chunk)
                    except Exception as e:
                        self.logger.error(f"✗ Chunk {i+1} translation failed: {e}")
                        translated_chunks.append(chunk)
                
                text_en = ' '.join(translated_chunks)
            else:
                try:
                    text_en = self.translator.translate(text, 'en', source_lang)
                except Exception as e:
                    self.logger.error(f"Translation failed: {e}")
                    text_en = text
        else:
            text_en = text
        
        # VALIDATE: Ensure we have content
        text_en_words = len(text_en.split())
        self.logger.info(f"English text ready: {text_en_words} words")
        
        if text_en_words < 30:
            self.logger.error(f"Text too short after translation: {text_en_words} words")
            text_en = text  # Use original
            text_en_words = word_count
        
        # STEP 2: Summarize in English
        self.logger.info(f"Generating summary from {text_en_words} words...")
        
        try:
            if text_en_words > 700:
                self.logger.info("Using two-stage summarization...")
                # Stage 1: Extractive reduction
                intermediate = summarizer.summarize(
                    text_en,
                    method='extractive',
                    max_length=350,
                    min_length=100
                )
                self.logger.info(f"Intermediate: {len(intermediate.split())} words")
                
                # Stage 2: Transformer summary
                summary_en = summarizer.summarize(
                    intermediate,
                    method='transformer',
                    max_length=max_length,
                    min_length=min_length
                )
            else:
                # Direct summarization
                summary_en = summarizer.summarize(
                    text_en,
                    method='transformer',
                    max_length=max_length,
                    min_length=min_length
                )
            
            summary_en_words = len(summary_en.split())
            self.logger.info(f"✓ Summary generated: {summary_en_words} words")
            self.logger.info(f"Summary preview: {summary_en[:100]}...")
            
        except Exception as e:
            self.logger.error(f"Summarization failed: {e}")
            self.logger.info("Falling back to extractive...")
            try:
                summary_en = summarizer.summarize(
                    text_en,
                    method='extractive',
                    max_length=max_length,
                    min_length=min_length
                )
                summary_en_words = len(summary_en.split())
                self.logger.info(f"✓ Extractive summary: {summary_en_words} words")
            except Exception as e2:
                self.logger.error(f"Extractive also failed: {e2}")
                # Last resort: first sentences
                sentences = text_en.split('.')[:5]
                summary_en = '. '.join(sentences) + '.'
                summary_en_words = len(summary_en.split())
                self.logger.warning(f"✗ Using first sentences: {summary_en_words} words")
        
        # VALIDATE: Ensure we have a valid summary
        if not summary_en or len(summary_en.strip()) < 20:
            self.logger.error("Summary is empty or too short!")
            sentences = text_en.split('.')[:5]
            summary_en = '. '.join([s.strip() for s in sentences if s.strip()]) + '.'
            self.logger.warning(f"Using fallback summary: {summary_en[:100]}...")
        
        # STEP 3: Translate summary to target language
        if target_lang != 'en' and target_lang != source_lang:
            self.logger.info(f"Translating summary to {target_lang}...")
            try:
                summary_final = self.translator.translate(summary_en, target_lang, 'en')
                if not summary_final or len(summary_final.strip()) < 20:
                    self.logger.warning("Target translation too short, using English")
                    summary_final = summary_en
                    target_lang = 'en'
                else:
                    self.logger.info(f"✓ Translated to {target_lang}")
            except Exception as e:
                self.logger.error(f"Target translation failed: {e}")
                summary_final = summary_en
                target_lang = 'en'
                
        elif target_lang == source_lang and source_lang != 'en':
            self.logger.info(f"Translating summary back to {source_lang}...")
            try:
                summary_final = self.translator.translate(summary_en, source_lang, 'en')
                if not summary_final or len(summary_final.strip()) < 20:
                    self.logger.warning("Back-translation too short, using English")
                    summary_final = summary_en
                    target_lang = 'en'
                else:
                    self.logger.info(f"✓ Translated back to {source_lang}")
            except Exception as e:
                self.logger.error(f"Back-translation failed: {e}")
                summary_final = summary_en
                target_lang = 'en'
        else:
            summary_final = summary_en
        
        # FINAL VALIDATION
        final_words = len(summary_final.split())
        self.logger.info(f"✓✓✓ FINAL SUMMARY READY: {final_words} words")
        self.logger.info(f"Final preview: {summary_final[:150]}...")
        
        if not summary_final or final_words < 5:
            raise Exception("Failed to generate valid summary")
        
        return {
            'summary': summary_final,
            'source_language': source_lang,
            'source_language_name': self.language_detector.get_language_name(source_lang),
            'target_language': target_lang,
            'target_language_name': self.language_detector.get_language_name(target_lang),
            'method': 'translate',
            'original_length': word_count,
            'summary_length': final_words
        }
    
    def _native_summarize(
        self,
        text,
        source_lang,
        target_lang,
        max_length,
        min_length
    ):
        """Summarize directly using mBART"""
        self._load_mbart_model()
        
        lang_map = {
            'en': 'en_XX', 'es': 'es_XX', 'fr': 'fr_XX', 'de': 'de_DE',
            'it': 'it_IT', 'pt': 'pt_XX', 'ru': 'ru_RU', 'zh-cn': 'zh_CN',
            'ja': 'ja_XX', 'ko': 'ko_KR', 'ar': 'ar_AR', 'hi': 'hi_IN',
            'tr': 'tr_TR', 'nl': 'nl_XX', 'pl': 'pl_PL'
        }
        
        mbart_src = lang_map.get(source_lang, 'en_XX')
        mbart_tgt = lang_map.get(target_lang, 'en_XX')
        
        self.mbart_tokenizer.src_lang = mbart_src
        encoded = self.mbart_tokenizer(
            text,
            return_tensors="pt",
            max_length=1024,
            truncation=True
        )
        
        generated = self.mbart_model.generate(
            **encoded,
            forced_bos_token_id=self.mbart_tokenizer.lang_code_to_id[mbart_tgt],
            max_length=max_length,
            min_length=min_length,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )
        
        summary = self.mbart_tokenizer.batch_decode(
            generated,
            skip_special_tokens=True
        )[0]
        
        return {
            'summary': summary,
            'source_language': source_lang,
            'source_language_name': self.language_detector.get_language_name(source_lang),
            'target_language': target_lang,
            'target_language_name': self.language_detector.get_language_name(target_lang),
            'method': 'native',
            'original_length': len(text.split()),
            'summary_length': len(summary.split())
        }
    
    def translate_text(self, text, target_lang, source_lang='auto'):
        """Translation wrapper"""
        return self.translator.translate(text, target_lang, source_lang)