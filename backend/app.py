from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from summarizer import TextSummarizer
from file_handler import FileHandler
from multilingual_summarizer import MultilingualSummarizer
from language_detector import LanguageDetector
from translator import TextTranslator
import logging
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize components
summarizer = TextSummarizer()
file_handler = FileHandler()
multilingual_summarizer = MultilingualSummarizer()
language_detector = LanguageDetector()
translator = TextTranslator()

logging.basicConfig(level=logging.INFO)

@app.route('/api/summarize', methods=['POST'])
def summarize():
    """Summarize text with multilingual support"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        method = data.get('method', 'transformer')
        max_length = data.get('max_length', 150)
        min_length = data.get('min_length', 50)
        target_lang = data.get('target_lang', 'auto')  # NEW: target language
        multilingual_mode = data.get('multilingual_mode', 'translate')  # NEW
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Detect language
        detected_lang = language_detector.detect_language(text)
        detected_lang_name = language_detector.get_language_name(detected_lang)
        
        # If target language is auto, use detected language
        if target_lang == 'auto':
            target_lang = detected_lang
        
        # Use multilingual summarizer if needed
        if detected_lang != 'en' or target_lang != 'en':
            result = multilingual_summarizer.summarize_multilingual(
                text,
                target_lang=target_lang,
                method=multilingual_mode,
                max_length=max_length,
                min_length=min_length
            )
            
            return jsonify({
                'summary': result['summary'],
                'original_length': result['original_length'],
                'summary_length': result['summary_length'],
                'compression_ratio': f"{(result['summary_length'] / result['original_length'] * 100):.1f}%",
                'source_language': result['source_language'],
                'source_language_name': result['source_language_name'],
                'target_language': result['target_language'],
                'target_language_name': result['target_language_name'],
                'detected_language': detected_lang,
                'detected_language_name': detected_lang_name
            })
        else:
            # Standard English summarization
            summary = summarizer.summarize(
                text, 
                method=method,
                max_length=max_length,
                min_length=min_length
            )
            
            return jsonify({
                'summary': summary,
                'original_length': len(text.split()),
                'summary_length': len(summary.split()),
                'compression_ratio': f"{(len(summary) / len(text) * 100):.1f}%",
                'detected_language': detected_lang,
                'detected_language_name': detected_lang_name,
                'source_language': 'en',
                'target_language': 'en'
            })
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    """Translate text between languages"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'en')
        source_lang = data.get('source_lang', 'auto')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        translated = translator.translate(text, target_lang, source_lang)
        
        # Detect source if auto
        if source_lang == 'auto':
            source_lang = translator.detect_language(text)
        
        return jsonify({
            'translated_text': translated,
            'source_language': source_lang,
            'target_language': target_lang
        })
    
    except Exception as e:
        logging.error(f"Translation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/detect-language', methods=['POST'])
def detect_language():
    """Detect language of input text"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        lang_code = language_detector.detect_language(text)
        lang_name = language_detector.get_language_name(lang_code)
        
        return jsonify({
            'language_code': lang_code,
            'language_name': lang_name,
            'is_supported': language_detector.is_supported(lang_code)
        })
    
    except Exception as e:
        logging.error(f"Detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages"""
    try:
        languages = language_detector.get_all_languages()
        return jsonify({
            'languages': languages,
            'total': len(languages)
        })
    except Exception as e:
        logging.error(f"Error fetching languages: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and extract text from file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        file_handler.validate_file(file)
        text = file_handler.extract_text(file, file.filename)
        
        if not text or len(text.strip()) == 0:
            return jsonify({'error': 'No text could be extracted from the file'}), 400
        
        # Detect language
        detected_lang = language_detector.detect_language(text)
        detected_lang_name = language_detector.get_language_name(detected_lang)
        
        return jsonify({
            'text': text,
            'filename': file.filename,
            'word_count': len(text.split()),
            'detected_language': detected_lang,
            'detected_language_name': detected_lang_name
        })
    
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/summarize-file', methods=['POST'])
def summarize_file():
    """Upload file, extract text, and summarize in one step"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        method = request.form.get('method', 'transformer')
        max_length = int(request.form.get('max_length', 150))
        min_length = int(request.form.get('min_length', 50))
        target_lang = request.form.get('target_lang', 'auto')
        
        file_handler.validate_file(file)
        text = file_handler.extract_text(file, file.filename)
        
        if not text or len(text.strip()) == 0:
            return jsonify({'error': 'No text could be extracted from the file'}), 400
        
        # Detect language
        detected_lang = language_detector.detect_language(text)
        
        # Use appropriate summarizer
        if detected_lang != 'en' or target_lang != 'auto':
            if target_lang == 'auto':
                target_lang = detected_lang
                
            result = multilingual_summarizer.summarize_multilingual(
                text,
                target_lang=target_lang,
                max_length=max_length,
                min_length=min_length
            )
            summary = result['summary']
        else:
            summary = summarizer.summarize(
                text,
                method=method,
                max_length=max_length,
                min_length=min_length
            )
        
        return jsonify({
            'summary': summary,
            'original_text': text,
            'original_length': len(text.split()),
            'summary_length': len(summary.split()),
            'compression_ratio': f"{(len(summary) / len(text) * 100):.1f}%",
            'filename': file.filename,
            'detected_language': detected_lang
        })
    
    except Exception as e:
        logging.error(f"Summarize file error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    """Generate and download PDF with summary"""
    try:
        data = request.get_json()
        original_text = data.get('original_text', '')
        summary = data.get('summary', '')
        stats = data.get('stats', {})
        
        if not summary:
            return jsonify({'error': 'No summary provided'}), 400
        
        pdf_data = file_handler.generate_pdf(original_text, summary, stats)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'summary_{timestamp}.pdf'
        
        return send_file(
            BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        logging.error(f"PDF generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)