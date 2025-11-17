"""
File processing utilities for extracting text from documents.

Supports PDF and DOCX formats for CVs and job postings.
Prioritizes PDF.co as primary extraction method with multiple strategies:
1. Document Parser (structured JSON with templates)
2. PDF to JSON (document structure)
3. PDF to Text (with OCR support)
4. PyPDF2 (fallback if PDF.co unavailable)
"""

from typing import Tuple, Optional, List, Dict, Any
import PyPDF2
from docx import Document
import io
import logging
import asyncio

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
        
        PRIORITY STRATEGY (PDF.co first, PyPDF2 as fallback):
        1. PDF.co with multiple strategies (Document Parser -> PDF to JSON -> PDF to Text)
        2. PyPDF2 (only if PDF.co unavailable or all strategies fail)
        
        PDF.co advantages:
        - OCR support for scanned PDFs
        - Structured JSON extraction (better for AI processing)
        - Handles complex layouts better
        
        Args:
            file_content: Binary content of PDF file
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        # Step 1: Try PDF.co first (prioridade - melhor para AI)
        pdfco_result = FileProcessor._extract_with_pdfco(file_content)
        if pdfco_result[0]:  # Success
            return pdfco_result
        
        # Step 2: PDF.co failed or unavailable - fallback to PyPDF2
        logger.info("PDF.co extraction failed/unavailable, attempting PyPDF2 fallback...")
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            extracted_text = "\n\n".join(text_parts)
            
            if extracted_text.strip():
                logger.info(f"Extracted {len(extracted_text)} characters from PDF using PyPDF2 (fallback)")
                return True, extracted_text, None
            else:
                error_msg = pdfco_result[2] or "PyPDF2 returned empty text"
                return False, None, f"{error_msg} (PyPDF2 fallback also failed)"
            
        except Exception as e:
            error_msg = pdfco_result[2] or str(e)
            logger.error(f"PyPDF2 fallback failed: {e}")
            return False, None, f"{error_msg} (PyPDF2 fallback also failed)"
    
    @staticmethod
    def _extract_with_pdfco(file_content: bytes, template_id: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract PDF content using PDF.co with multiple strategies (prioritized).
        
        Strategies (in order):
        1. Document Parser (if template provided) - returns structured JSON
        2. PDF to JSON - returns document structure  
        3. PDF to Text - returns plain text (with OCR)
        
        Args:
            file_content: Binary content of PDF file
            template_id: Optional template ID for Document Parser
            
        Returns:
            Tuple of (success, extracted_text, error_message)
            Note: Structured data is converted to text for compatibility
        """
        try:
            from services.pdfco.service import get_pdfco_service
            
            pdfco_service = get_pdfco_service()
            
            if not pdfco_service.is_available():
                return False, None, "PDF.co API not configured"
            
            # Run async function in sync context
            try:
                try:
                    loop = asyncio.get_running_loop()
                    import nest_asyncio
                    nest_asyncio.apply()
                    result = loop.run_until_complete(
                        pdfco_service.extract_pdf_structured(file_content, "file.pdf", template_id)
                    )
                except RuntimeError:
                    result = asyncio.run(
                        pdfco_service.extract_pdf_structured(file_content, "file.pdf", template_id)
                    )
            except ImportError:
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        pdfco_service.extract_pdf_structured(file_content, "file.pdf", template_id)
                    )
                    result = future.result(timeout=90)
            
            success, structured_data, plain_text, error_msg = result
            
            if success:
                # Prefer structured data converted to text, fallback to plain text
                extracted_text = plain_text or (FileProcessor._structured_to_text(structured_data) if structured_data else None)
                
                if extracted_text and extracted_text.strip():
                    logger.info(f"Extracted {len(extracted_text)} characters from PDF using PDF.co (structured: {structured_data is not None})")
                    return True, extracted_text, None
                else:
                    return False, None, error_msg or "PDF.co extracted but no text content"
            else:
                return False, None, error_msg or "PDF.co extraction failed"
            
        except ImportError:
            logger.warning("PDF.co service not available")
            return False, None, "PDF.co service not available"
        except Exception as e:
            logger.error(f"Error in PDF.co extraction: {e}", exc_info=True)
            return False, None, f"PDF.co error: {str(e)}"
    
    @staticmethod
    def _structured_to_text(structured_data: Optional[Dict]) -> str:
        """
        Convert structured JSON data to plain text.
        
        Args:
            structured_data: JSON dict from PDF.co Document Parser or PDF to JSON
            
        Returns:
            Plain text representation
        """
        if not structured_data:
            return ""
        
        text_parts = []
        
        def extract_text(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        extract_text(value, f"{prefix}{key}: ")
                    elif value:
                        text_parts.append(f"{prefix}{key}: {value}")
            elif isinstance(obj, list):
                for item in obj:
                    extract_text(item, prefix)
            elif obj:
                text_parts.append(f"{prefix}{obj}")
        
        extract_text(structured_data)
        return "\n".join(text_parts)
    
    @staticmethod
    def _extract_image_with_pdfco_ocr(file_content: bytes, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract text from image using PDF.co OCR.
        
        Args:
            file_content: Binary content of image file
            filename: Original filename
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        try:
            from services.pdfco.service import get_pdfco_service
            
            pdfco_service = get_pdfco_service()
            
            if not pdfco_service.is_available():
                return False, None, "PDF.co API not configured (OCR unavailable for images)"
            
            # Run async function in sync context
            try:
                try:
                    loop = asyncio.get_running_loop()
                    import nest_asyncio
                    nest_asyncio.apply()
                    return loop.run_until_complete(
                        pdfco_service.image_to_text_with_ocr(file_content, filename)
                    )
                except RuntimeError:
                    return asyncio.run(
                        pdfco_service.image_to_text_with_ocr(file_content, filename)
                    )
            except ImportError:
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        pdfco_service.image_to_text_with_ocr(file_content, filename)
                    )
                    return future.result(timeout=90)
            
        except ImportError:
            logger.warning("PDF.co service not available, image OCR disabled")
            return False, None, "PDF.co service not available"
        except Exception as e:
            logger.error(f"Error in PDF.co image OCR: {e}", exc_info=True)
            return False, None, f"Image OCR error: {str(e)}"
    
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
        elif file_lower.endswith(('.jpg', '.jpeg', '.png')):
            # Images - use PDF.co OCR directly
            return FileProcessor._extract_image_with_pdfco_ocr(file_content, filename)
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

