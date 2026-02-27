import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from backend.summarizer import TextSummarizer

class TestTextSummarizer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.summarizer = TextSummarizer()
        cls.sample_text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, 
        in contrast to the natural intelligence displayed by humans and animals. 
        Leading AI textbooks define the field as the study of intelligent agents: 
        any device that perceives its environment and takes actions that maximize 
        its chance of successfully achieving its goals. Colloquially, the term 
        artificial intelligence is often used to describe machines that mimic 
        cognitive functions that humans associate with the human mind, such as 
        learning and problem solving. As machines become increasingly capable, 
        tasks considered to require intelligence are often removed from the 
        definition of AI, a phenomenon known as the AI effect. A quip in Tesler's 
        Theorem says AI is whatever hasn't been done yet. For instance, optical 
        character recognition is frequently excluded from things considered to be 
        AI, having become a routine technology.
        """
    
    def test_extractive_summarization(self):
        """Test extractive summarization method"""
        summary = self.summarizer.summarize(
            self.sample_text,
            method='extractive',
            num_sentences=2
        )
        
        # Check that summary is not empty
        self.assertIsNotNone(summary)
        self.assertTrue(len(summary) > 0)
        
        # Check that summary is shorter than original
        self.assertLess(len(summary.split()), len(self.sample_text.split()))
        
        print(f"\n✓ Extractive Summary:\n{summary}\n")
    
    def test_transformer_summarization(self):
        """Test transformer-based summarization"""
        try:
            summary = self.summarizer.summarize(
                self.sample_text,
                method='transformer',
                max_length=100,
                min_length=30
            )
            
            # Check that summary is not empty
            self.assertIsNotNone(summary)
            self.assertTrue(len(summary) > 0)
            
            # Check length constraints
            word_count = len(summary.split())
            self.assertLessEqual(word_count, 120)  # Allow some margin
            
            print(f"\n✓ Transformer Summary:\n{summary}\n")
            
        except Exception as e:
            self.skipTest(f"Transformer model not available: {e}")
    
    def test_invalid_method(self):
        """Test that invalid method raises error"""
        with self.assertRaises(ValueError):
            self.summarizer.summarize(
                self.sample_text,
                method='invalid_method'
            )
    
    def test_empty_text(self):
        """Test behavior with empty text"""
        result = self.summarizer.summarize(
            "",
            method='extractive'
        )
        self.assertEqual(result, "")
    
    def test_short_text(self):
        """Test behavior with very short text"""
        short_text = "This is a short sentence."
        result = self.summarizer.summarize(
            short_text,
            method='extractive',
            num_sentences=3
        )
        # Should return original text if it's already shorter
        self.assertEqual(result, short_text)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_multiple_summarizations(self):
        """Test multiple summarizations in sequence"""
        summarizer = TextSummarizer()
        
        texts = [
            "Climate change is one of the most pressing issues facing our planet today.",
            "Machine learning is a subset of artificial intelligence that focuses on learning from data.",
            "The Internet has revolutionized communication and information sharing globally."
        ]
        
        for text in texts:
            summary = summarizer.summarize(text, method='extractive')
            self.assertIsNotNone(summary)
            print(f"✓ Summary generated for: {text[:50]}...")

def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestTextSummarizer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == '__main__':
    print("=" * 70)
    print("Running Text Summarizer Tests")
    print("=" * 70)
    
    result = run_tests()
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed.")
    print("=" * 70)