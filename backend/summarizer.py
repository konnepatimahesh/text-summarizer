"""
Text summarization using transformer and extractive methods
"""

from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class TextSummarizer:
    """Handle text summarization"""
    
    def __init__(self):
        self.transformer_summarizer = None
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            logger.warning("Stopwords not found, downloading...")
            nltk.download('stopwords')
            self.stop_words = set(stopwords.words('english'))
        
        # Download punkt if not available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.warning("Punkt tokenizer not found, downloading...")
            nltk.download('punkt')
    
    def _load_transformer(self):
        """Lazy load the transformer model"""
        if self.transformer_summarizer is None:
            logger.info("Loading BART summarization model...")
            try:
                self.transformer_summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn"
                )
                logger.info("BART model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load BART model: {e}")
                raise
    
    def summarize(self, text, method='transformer', max_length=150, min_length=50):
        """
        Summarize text using specified method
        
        Args:
            text: Input text to summarize
            method: 'transformer' or 'extractive'
            max_length: Maximum length of summary
            min_length: Minimum length of summary
            
        Returns:
            Summary text
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        if method == 'transformer':
            return self._transformer_summarize(text, max_length, min_length)
        elif method == 'extractive':
            # Calculate number of sentences based on length
            num_sentences = max(3, min(10, len(text.split()) // 50))
            return self._extractive_summarize(text, num_sentences=num_sentences)
        else:
            raise ValueError(f"Invalid method: {method}. Use 'transformer' or 'extractive'")
    
    def _transformer_summarize(self, text, max_length, min_length):
        """
        Abstractive summarization using BART transformer
        """
        self._load_transformer()
        
        # Check text length
        word_count = len(text.split())
        
        # If text is too long, use extractive first to reduce it
        if word_count > 1000:
            logger.info(f"Text too long ({word_count} words), pre-processing with extractive method...")
            # Use extractive to get it down to ~500 words first
            num_sentences = min(20, word_count // 25)
            text = self._extractive_summarize(text, num_sentences=num_sentences)
            logger.info(f"Pre-processed to {len(text.split())} words")
        
        try:
            # BART has a max input length of 1024 tokens
            result = self.transformer_summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True  # Truncate if still too long
            )
            return result[0]['summary_text']
        except Exception as e:
            logger.error(f"Transformer summarization failed: {e}")
            # Fallback to extractive if transformer fails
            logger.info("Falling back to extractive method...")
            return self._extractive_summarize(text, num_sentences=5)
    
    def _extractive_summarize(self, text, num_sentences=3):
        """
        Extractive summarization using word frequency
        """
        try:
            # Tokenize into sentences
            sentences = sent_tokenize(text)
            
            if len(sentences) <= num_sentences:
                return text
            
            # Calculate word frequencies
            word_freq = Counter()
            for sentence in sentences:
                words = word_tokenize(sentence.lower())
                for word in words:
                    if word.isalnum() and word not in self.stop_words:
                        word_freq[word] += 1
            
            # Score sentences based on word frequencies
            sentence_scores = {}
            for sentence in sentences:
                words = word_tokenize(sentence.lower())
                score = sum(
                    word_freq[word] for word in words 
                    if word.isalnum() and word not in self.stop_words
                )
                # Normalize by sentence length to avoid bias toward long sentences
                if len(words) > 0:
                    sentence_scores[sentence] = score / len(words)
                else:
                    sentence_scores[sentence] = 0
            
            # Get top sentences
            top_sentences = sorted(
                sentence_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:num_sentences]
            
            # Sort by original order to maintain coherence
            summary_sentences = sorted(
                top_sentences,
                key=lambda x: sentences.index(x[0])
            )
            
            summary = ' '.join([s[0] for s in summary_sentences])
            return summary
            
        except Exception as e:
            logger.error(f"Extractive summarization failed: {e}")
            # Return first few sentences as last resort
            sentences = text.split('.')[:num_sentences]
            return '. '.join(sentences) + '.'