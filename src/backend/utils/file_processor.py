"""
File processing utilities for extracting text from documents.

Supports PDF and DOCX formats for CVs and job postings.
"""

from typing import Tuple, Optional, List
import PyPDF2
from docx import Document
import io
import logging

logger = logging.getLogger(__name__)


class FileProcessor:
    """
    Utility class for processing uploaded files.
    
    Responsibilities:
    - Extract text from PDF files
    - Extract text from DOCX files
    - Validate file types and sizes
    """
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract text from PDF file.
        
        Args:
            file_content: Binary content of PDF file
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            extracted_text = "\n\n".join(text_parts)
            
            if not extracted_text.strip():
                return False, None, "No text could be extracted from PDF"
            
            logger.info(f"Extracted {len(extracted_text)} characters from PDF")
            return True, extracted_text, None
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return False, None, str(e)
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract text from DOCX file.
        
        Args:
            file_content: Binary content of DOCX file
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            extracted_text = "\n\n".join(text_parts)
            
            if not extracted_text.strip():
                return False, None, "No text could be extracted from DOCX"
            
            logger.info(f"Extracted {len(extracted_text)} characters from DOCX")
            return True, extracted_text, None
            
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return False, None, str(e)
    
    @staticmethod
    def extract_text(
        file_content: bytes,
        filename: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract text from file based on extension.
        
        Args:
            file_content: Binary content of file
            filename: Original filename with extension
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        file_lower = filename.lower()
        
        if file_lower.endswith('.pdf'):
            return FileProcessor.extract_text_from_pdf(file_content)
        elif file_lower.endswith('.docx'):
            return FileProcessor.extract_text_from_docx(file_content)
        elif file_lower.endswith('.doc'):
            # For older .doc files, try DOCX parser (may not always work)
            return FileProcessor.extract_text_from_docx(file_content)
        elif file_lower.endswith('.txt'):
            # Plain text file
            try:
                text = file_content.decode('utf-8')
                return True, text, None
            except Exception as e:
                return False, None, str(e)
        else:
            return False, None, f"Unsupported file type: {filename}"
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate file type based on extension.
        
        Args:
            filename: Filename with extension
            allowed_types: List of allowed extensions (e.g., ['.pdf', '.docx'])
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if allowed_types is None:
            allowed_types = ['.pdf', '.docx', '.doc', '.txt']
        
        file_lower = filename.lower()
        
        for allowed_type in allowed_types:
            if file_lower.endswith(allowed_type):
                return True, None
        
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
    
    @staticmethod
    def validate_file_size(
        file_size: int,
        max_size_mb: int = 10
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate file size.
        
        Args:
            file_size: File size in bytes
            max_size_mb: Maximum allowed size in MB
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            return False, f"File too large. Maximum size: {max_size_mb}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, None

    @staticmethod
    def text_to_markdown(text: str) -> str:
        """
        Convert extracted plain text into lightweight Markdown to improve AI context.
        """
        if not text:
            return ""

        markdown_lines: List[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if not line:
                markdown_lines.append("")
                continue

            bullet_prefixes = ("-", "•", "*", "·", "–")
            if line.startswith(bullet_prefixes):
                content = line.lstrip("-•*·– \t")
                markdown_lines.append(f"- {content}")
                continue

            if ":" in line and line.endswith(":"):
                heading = line[:-1].strip()
                if heading:
                    markdown_lines.append(f"### {heading}")
                    continue

            if len(line.split()) <= 8 and line.upper() == line:
                markdown_lines.append(f"### {line.title()}")
                continue

            markdown_lines.append(line)

        return "\n".join(markdown_lines)

