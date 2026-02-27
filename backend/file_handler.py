"""
File handling utilities for PDF and DOCX files
"""

import PyPDF2
from docx import Document
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from io import BytesIO
import os

class FileHandler:
    """Handle file operations for text extraction and PDF generation"""
    
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileHandler.ALLOWED_EXTENSIONS
    
    @staticmethod
    def extract_text_from_pdf(file):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file):
        """Extract text from DOCX file"""
        try:
            doc = Document(file)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file):
        """Extract text from TXT file"""
        try:
            text = file.read().decode('utf-8')
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
    
    @staticmethod
    def extract_text(file, filename):
        """Extract text from file based on extension"""
        ext = filename.rsplit('.', 1)[1].lower()
        
        if ext == 'pdf':
            return FileHandler.extract_text_from_pdf(file)
        elif ext == 'docx':
            return FileHandler.extract_text_from_docx(file)
        elif ext == 'txt':
            return FileHandler.extract_text_from_txt(file)
        else:
            raise Exception("Unsupported file type")
    
    @staticmethod
    def generate_pdf(original_text, summary, stats):
        """Generate PDF with original text and summary"""
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for PDF elements
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#667eea',
            spaceAfter=30,
            alignment=TA_LEFT
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor='#764ba2',
            spaceAfter=12,
            spaceBefore=12
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16
        )
        
        stats_style = ParagraphStyle(
            'StatsStyle',
            parent=styles['BodyText'],
            fontSize=10,
            textColor='#666666',
            spaceAfter=6
        )
        
        # Add title
        elements.append(Paragraph("📄 Text Summarization Report", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add statistics
        elements.append(Paragraph("📊 Summary Statistics", heading_style))
        elements.append(Paragraph(f"<b>Original Length:</b> {stats['original_length']} words", stats_style))
        elements.append(Paragraph(f"<b>Summary Length:</b> {stats['summary_length']} words", stats_style))
        elements.append(Paragraph(f"<b>Compression Ratio:</b> {stats['compression_ratio']}", stats_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Add summary
        elements.append(Paragraph("✨ Summary", heading_style))
        summary_text = summary.replace('\n', '<br/>')
        elements.append(Paragraph(summary_text, body_style))
        elements.append(Spacer(1, 0.4*inch))
        
        # Add original text
        elements.append(Paragraph("📝 Original Text", heading_style))
        
        # Split original text into paragraphs for better formatting
        original_paragraphs = original_text.split('\n')
        for para in original_paragraphs:
            if para.strip():
                para_text = para.replace('\n', '<br/>')
                elements.append(Paragraph(para_text, body_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    @staticmethod
    def validate_file(file):
        """Validate uploaded file"""
        if not file:
            raise Exception("No file provided")
        
        if file.filename == '':
            raise Exception("No file selected")
        
        if not FileHandler.allowed_file(file.filename):
            raise Exception(f"File type not allowed. Allowed types: {', '.join(FileHandler.ALLOWED_EXTENSIONS)}")
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > FileHandler.MAX_FILE_SIZE:
            raise Exception(f"File size exceeds maximum allowed size of 10MB")
        
        return True