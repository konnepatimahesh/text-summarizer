# 🤖 AI-Powered Text Summarization

A modern web application that uses Natural Language Processing and Machine Learning to automatically generate concise summaries from long texts.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

- **Two Summarization Methods**
  - 🤖 **AI-Powered (BART)**: Advanced transformer-based abstractive summarization
  - ⚡ **Extractive**: Fast keyword-based sentence extraction

- **Customizable Output**
  - Choose summary length (Short, Medium, Long)
  - Adjustable compression ratios
  - Word count statistics

- **Modern UI**
  - Clean, responsive design
  - Real-time processing feedback
  - Copy-to-clipboard functionality
  - Mobile-friendly interface

- **Robust Backend**
  - RESTful API design
  - Error handling and validation
  - Health check endpoint

## 🏗️ Project Structure

```
text-summarizer/
├── backend/
│   ├── app.py                 # Flask application
│   ├── summarizer.py          # Summarization logic
│   ├── requirements.txt       # Python dependencies
│   └── models/               # Model storage
├── frontend/
│   ├── index.html            # Main HTML page
│   ├── style.css             # Styling
│   └── script.js             # Frontend logic
├── tests/
│   ├── test_summarizer.py    # Unit tests
│   └── sample_texts.txt      # Test data
├── config.py                 # Configuration
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Modern web browser

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd text-summarizer
```

2. **Create virtual environment**
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Download NLTK data**
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Running the Application

1. **Start the backend server**
```bash
cd backend
python app.py
```
Server runs on `http://localhost:5000`

2. **Open the frontend**
   - Simply open `frontend/index.html` in your browser
   - Or use a local server:
```bash
cd frontend
python -m http.server 8000
```
Then visit `http://localhost:8000`

## 📖 Usage

1. **Paste or type** your text into the input area
2. **Select** the summarization method:
   - AI (BART) for high-quality abstractive summaries
   - Extractive for quick keyword-based summaries
3. **Choose** the desired summary length
4. **Click** "Summarize" and wait for the result
5. **Copy** the summary using the copy button

## 🧪 Testing

Run the test suite:

```bash
cd tests
python test_summarizer.py
```

## 🛠️ API Documentation

### Endpoints

#### `POST /api/summarize`
Generate a summary from input text.

**Request Body:**
```json
{
  "text": "Your long text here...",
  "method": "transformer",
  "max_length": 150,
  "min_length": 50
}
```

**Response:**
```json
{
  "summary": "Generated summary...",
  "original_length": 500,
  "summary_length": 120,
  "compression_ratio": "24.0%"
}
```

#### `GET /api/health`
Check API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

## ⚙️ Configuration

Edit `config.py` to customize:

- API host and port
- Model selection
- Summary length limits
- Rate limiting
- Logging levels

## 🔧 Technology Stack

**Backend:**
- Flask - Web framework
- Transformers (Hugging Face) - BART model
- NLTK - Natural language processing
- NumPy - Numerical operations

**Frontend:**
- HTML5 - Structure
- CSS3 - Styling with gradients and animations
- Vanilla JavaScript - Interactivity

**Model:**
- facebook/bart-large-cnn - Pre-trained summarization model

## 📊 Performance

- **Extractive Method**: ~0.5-1 seconds per summary
- **Transformer Method**: ~2-5 seconds per summary (first load may take longer)
- Supports texts up to 5000 words efficiently

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Known Issues

- First summarization with BART model may be slow (model loading)
- Very long texts (>5000 words) may need chunking
- Internet connection required for initial model download

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] PDF and DOCX upload
- [ ] Summary history and saved summaries
- [ ] User authentication
- [ ] Batch processing
- [ ] Custom model fine-tuning
- [ ] Export summaries (PDF, TXT)
- [ ] API key management
- [ ] Docker containerization

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Your Name - [Your GitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Hugging Face for the Transformers library
- Facebook AI for the BART model
- NLTK team for natural language processing tools

## 📧 Contact

For questions or feedback, please open an issue or contact [your-email@example.com]

---

**Note**: Make sure the Flask backend is running before using the frontend interface!