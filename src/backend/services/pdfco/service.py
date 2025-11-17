"""
PDF.co API Service for OCR and advanced PDF processing.

Prioritizes PDF.co as the primary extraction method with multiple strategies:
1. Document Parser (with custom template for structured JSON extraction)
2. PDF to JSON (for document structure)
3. PDF to Text (with OCR support)
4. Image to Text (OCR)

All methods return structured data when possible for better AI processing.
"""

import logging
import base64
import httpx
import json
from typing import Tuple, Optional, Dict, Any
from config import settings

logger = logging.getLogger(__name__)


class PDFCoService:
    """
    Service for PDF.co API integration.
    
    Provides multiple extraction strategies:
    - Document Parser (structured JSON with templates)
    - PDF to JSON (document structure)
    - PDF to Text (with OCR support)
    - Image to Text (OCR)
    
    All methods prioritize structured data extraction for better AI processing.
    """
    
    API_BASE_URL = "https://api.pdf.co/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize PDF.co service.
        
        Args:
            api_key: PDF.co API key (if None, uses settings.pdfco_api_key)
        """
        self.api_key = api_key or settings.pdfco_api_key
        
        if not self.api_key:
            logger.warning("PDFCO_API_KEY not configured. PDF.co extraction will be unavailable.")
        
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        } if self.api_key else {}
    
    def is_available(self) -> bool:
        """Check if PDF.co service is available (API key configured)."""
        return bool(self.api_key)
    
    async def extract_pdf_structured(
        self,
        file_content: bytes,
        filename: str,
        use_template: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str], Optional[str]]:
        """
        Extract PDF content using PDF.co with multiple strategies, prioritizing structured data.
        
        Strategy order:
        1. Document Parser (if template provided) - returns structured JSON
        2. PDF to JSON - returns document structure
        3. PDF to Text - returns plain text (with OCR)
        
        Args:
            file_content: Binary content of PDF file
            filename: Original filename
            use_template: Optional template ID for Document Parser
            
        Returns:
            Tuple of (success, structured_data_dict, plain_text, error_message)
            - structured_data_dict: JSON dict if available, None otherwise
            - plain_text: Plain text fallback if structured data unavailable
        """
        if not self.is_available():
            return False, None, None, "PDF.co API key not configured"
        
        # Upload file first to get URL (PDF.co requires file upload, not inline base64)
        file_url = await self._upload_file(file_content, filename)
        if not file_url:
            # If upload fails, fallback to PyPDF2 will happen in FileProcessor
            return False, None, None, "Failed to upload file to PDF.co"
        
        # Strategy 1: Try Document Parser if template provided
        if use_template:
            success, structured_data, error = await self._parse_document_with_template(
                file_url, use_template
            )
            if success and structured_data:
                logger.info("Extracted structured data using Document Parser")
                # Extract plain text from structured data if possible
                plain_text = self._structured_to_text(structured_data)
                return True, structured_data, plain_text, None
        
        # Strategy 2: Try PDF to JSON for document structure
        success, json_data, error = await self._pdf_to_json(file_url)
        if success and json_data:
            logger.info("Extracted document structure using PDF to JSON")
            # Convert JSON structure to plain text
            plain_text = self._json_structure_to_text(json_data)
            return True, json_data, plain_text, None
        
        # Strategy 3: Fallback to PDF to Text (with OCR)
        success, plain_text, error = await self._pdf_to_text_from_url(file_url)
        if success:
            logger.info("Extracted text using PDF to Text (with OCR)")
            return True, None, plain_text, None
        
        return False, None, None, error or "All PDF.co extraction strategies failed"
    
    async def _upload_file(
        self,
        file_content: bytes,
        filename: str
    ) -> Optional[str]:
        """
        Upload file to PDF.co and get file URL.
        
        PDF.co requires files to be uploaded first before processing.
        
        Args:
            file_content: Binary content of file
            filename: Original filename
            
        Returns:
            File URL from PDF.co or None if upload failed
        """
        try:
            url = f"{self.API_BASE_URL}/file/upload"
            
            # Determine content type from filename
            file_lower = filename.lower()
            if file_lower.endswith('.pdf'):
                content_type = "application/pdf"
            elif file_lower.endswith(('.jpg', '.jpeg')):
                content_type = "image/jpeg"
            elif file_lower.endswith('.png'):
                content_type = "image/png"
            else:
                content_type = "application/octet-stream"
            
            # Use multipart/form-data for file upload
            files = {
                'file': (filename, file_content, content_type)
            }
            
            headers = {
                "x-api-key": self.api_key
            }
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    files=files
                )
                response.raise_for_status()
                result = response.json()
            
            # Get file URL from response
            file_url = result.get("url") or result.get("fileUrl")
            if file_url:
                logger.info(f"File uploaded to PDF.co: {file_url}")
                return file_url
            
            # Check for error
            if result.get("error"):
                error_msg = result.get("message", result.get("error", "Unknown error"))
                logger.error(f"PDF.co file upload error: {error_msg}")
                return None
            
            logger.warning("File upload succeeded but no URL returned")
            return None
            
        except Exception as e:
            logger.error(f"Error uploading file to PDF.co: {e}", exc_info=True)
            return None
    
    async def _parse_document_with_template(
        self,
        file_url: str,
        template_id: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Parse document using Document Parser with a template.
        
        This returns structured JSON based on the template definition.
        
        Args:
            file_url: URL of uploaded file in PDF.co
            template_id: Template ID for Document Parser
            
        Returns:
            Tuple of (success, structured_json_dict, error_message)
        """
        try:
            url = f"{self.API_BASE_URL}/pdf/documentparser/parse"
            
            payload = {
                "url": file_url,
                "templateId": template_id,
                "inline": True
            }
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
            
            # Handle async job
            if result.get("jobId"):
                job_id = result.get("jobId")
                structured_data = await self._poll_parser_job_result(job_id)
                if structured_data:
                    return True, structured_data, None
            
            # Check for direct result
            if result.get("body"):
                # body can be string (JSON) or dict
                body = result.get("body")
                if isinstance(body, str):
                    try:
                        structured_data = json.loads(body)
                        return True, structured_data, None
                    except json.JSONDecodeError:
                        return False, None, "Invalid JSON in Document Parser response"
                elif isinstance(body, dict):
                    return True, body, None
            
            if result.get("error"):
                error_msg = result.get("message", result.get("error", "Unknown error"))
                return False, None, f"Document Parser error: {error_msg}"
            
            return False, None, "No structured data found in Document Parser response"
            
        except Exception as e:
            logger.error(f"Error in Document Parser: {e}", exc_info=True)
            return False, None, str(e)
    
    async def _pdf_to_json(
        self,
        file_url: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Convert PDF to JSON to extract document structure.
        
        This provides a structured representation of the PDF content,
        which can be better for AI processing than plain text.
        
        Args:
            file_url: URL of uploaded file in PDF.co
            
        Returns:
            Tuple of (success, json_dict, error_message)
        """
        try:
            url = f"{self.API_BASE_URL}/pdf/convert/to/json"
            
            payload = {
                "url": file_url,
                "inline": True
            }
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
            
            # Handle async job
            if result.get("jobId"):
                job_id = result.get("jobId")
                json_data = await self._poll_json_job_result(job_id)
                if json_data:
                    return True, json_data, None
            
            # Check for direct result
            json_str = result.get("body") or result.get("text")
            if json_str:
                if isinstance(json_str, str):
                    try:
                        json_data = json.loads(json_str)
                        return True, json_data, None
                    except json.JSONDecodeError:
                        return False, None, "Invalid JSON in PDF to JSON response"
                elif isinstance(json_str, dict):
                    return True, json_str, None
            
            if result.get("error"):
                error_msg = result.get("message", result.get("error", "Unknown error"))
                return False, None, f"PDF to JSON error: {error_msg}"
            
            return False, None, "No JSON data found in PDF to JSON response"
            
        except Exception as e:
            logger.error(f"Error in PDF to JSON: {e}", exc_info=True)
            return False, None, str(e)
    
    async def _pdf_to_text_from_url(
        self,
        file_url: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract text from PDF URL using PDF.co with OCR support.
        
        This works for both regular PDFs and scanned PDFs (images).
        Falls back to OCR automatically if text extraction fails.
        
        Args:
            file_url: URL of uploaded file in PDF.co
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        if not self.is_available():
            return False, None, "PDF.co API key not configured"
        
        try:
            # Use PDF to Text endpoint (automatically uses OCR if needed)
            # Documentation: https://docs.pdf.co/pdf-to-text
            url = f"{self.API_BASE_URL}/pdf/convert/to/text"
            
            payload = {
                "url": file_url,
                "inline": True  # Return text inline (not as file URL)
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
            
            # Check response structure
            # PDF.co can return:
            # 1. Direct result with "body" or "text" field
            # 2. Async job with "jobId" that needs polling
            # 3. Error with "error" field
            
            # Check for error first
            if result.get("error"):
                error_msg = result.get("message", result.get("error", "Unknown error"))
                logger.error(f"PDF.co API error: {error_msg}")
                return False, None, f"PDF.co API error: {error_msg}"
            
            # Check for async job
            job_id = result.get("jobId")
            if job_id:
                # Async job - poll for completion
                logger.info(f"PDF.co job {job_id} started, polling for results...")
                text = await self._poll_job_result(job_id, max_attempts=10)
                if text:
                    logger.info(f"Extracted {len(text)} characters from PDF using PDF.co OCR")
                    return True, text, None
                else:
                    return False, None, "PDF.co job did not complete in time"
            
            # Check for direct result
            # Try multiple possible response fields
            text = (
                result.get("body") or 
                result.get("text") or 
                result.get("content") or
                result.get("data") or
                ""
            )
            
            if text and isinstance(text, str) and text.strip():
                logger.info(f"Extracted {len(text)} characters from PDF using PDF.co")
                return True, text.strip(), None
            
            # If no text found but status is success, might be empty PDF
            if result.get("status") == "success":
                return False, None, "PDF extracted but no text content found"
            
            return False, None, "No text extracted from PDF - unknown response format"
                    
        except httpx.TimeoutException:
            logger.error("PDF.co API request timed out")
            return False, None, "PDF.co API request timed out"
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}"
            try:
                error_data = e.response.json()
                error_msg = error_data.get("message", error_data.get("error", error_msg))
            except:
                pass
            logger.error(f"PDF.co API HTTP error: {error_msg}")
            return False, None, f"PDF.co API error: {error_msg}"
        except Exception as e:
            logger.error(f"Error calling PDF.co API: {e}", exc_info=True)
            return False, None, str(e)
    
    async def pdf_to_text_with_ocr(
        self,
        file_content: bytes,
        filename: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract text from PDF using PDF.co with OCR support (wrapper for compatibility).
        
        This method uploads the file first and then calls _pdf_to_text_from_url.
        
        Args:
            file_content: Binary content of PDF file
            filename: Original filename
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        # Upload file first
        file_url = await self._upload_file(file_content, filename)
        if not file_url:
            return False, None, "Failed to upload file to PDF.co"
        
        # Extract text from uploaded file URL
        return await self._pdf_to_text_from_url(file_url)
    
    async def image_to_text_with_ocr(
        self,
        file_content: bytes,
        filename: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract text from image (JPG, PNG) using OCR.
        
        Uses PDF.co's image OCR capability to extract text directly from images.
        
        Args:
            file_content: Binary content of image file
            filename: Original filename
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        if not self.is_available():
            return False, None, "PDF.co API key not configured"
        
        try:
            # Upload image file first
            file_url = await self._upload_file(file_content, filename)
            if not file_url:
                return False, None, "Failed to upload image to PDF.co"
            
            # Determine MIME type from filename
            file_lower = filename.lower()
            if file_lower.endswith('.jpg') or file_lower.endswith('.jpeg'):
                mime_type = "image/jpeg"
            elif file_lower.endswith('.png'):
                mime_type = "image/png"
            else:
                return False, None, f"Unsupported image format: {filename}"
            
            # Use PDF from Image with OCR, then extract text from resulting PDF
            # Documentation: https://docs.pdf.co/pdf-from-image
            url = f"{self.API_BASE_URL}/pdf/convert/from/image"
            
            payload = {
                "url": file_url,  # Use uploaded file URL
                "ocrMode": "auto",  # Enable OCR
                "ocrLanguages": "eng,por,spa,fra",  # Support multiple languages
                "inline": True
            }
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
            
            # Handle async job if needed
            if result.get("status") == "working":
                job_id = result.get("jobId")
                if job_id:
                    # Poll for completion
                    pdf_data = await self._poll_image_job_result(job_id)
                    if pdf_data:
                        # Extract text from PDF
                        return await self.pdf_to_text_with_ocr(pdf_data, "temp.pdf")
            
            # Check if we got a PDF
            pdf_url = result.get("url")
            pdf_base64 = result.get("body") or result.get("pdf")
            
            if pdf_base64 and isinstance(pdf_base64, str) and pdf_base64.startswith("data:"):
                # Inline PDF data - extract base64
                pdf_base64_data = pdf_base64.split(",")[1] if "," in pdf_base64 else pdf_base64
                try:
                    pdf_bytes = base64.b64decode(pdf_base64_data)
                    return await self.pdf_to_text_with_ocr(pdf_bytes, "temp.pdf")
                except Exception as e:
                    logger.error(f"Error decoding PDF from image: {e}")
            
            if pdf_url:
                # URL to PDF - extract text
                return await self._extract_text_from_url(pdf_url)
            
            return False, None, "Failed to convert image to PDF with OCR"
            
        except Exception as e:
            logger.error(f"Error processing image with PDF.co: {e}", exc_info=True)
            return False, None, str(e)
    
    async def _poll_parser_job_result(self, job_id: str, max_attempts: int = 15) -> Optional[Dict[str, Any]]:
        """Poll for Document Parser job completion."""
        import asyncio
        
        url = f"{self.API_BASE_URL}/job/check"
        
        for attempt in range(max_attempts):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        url,
                        headers=self.headers,
                        json={"jobId": job_id}
                    )
                    response.raise_for_status()
                    result = response.json()
                
                status = result.get("status")
                
                if status == "success":
                    body = result.get("body")
                    if isinstance(body, str):
                        try:
                            return json.loads(body)
                        except json.JSONDecodeError:
                            return None
                    elif isinstance(body, dict):
                        return body
                    return None
                
                elif status == "working":
                    await asyncio.sleep(2)
                    continue
                
                else:
                    logger.warning(f"PDF.co parser job {job_id} status: {status}")
                    return None
                    
            except Exception as e:
                logger.warning(f"Error polling PDF.co parser job {job_id}: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(2)
                    continue
                return None
        
        return None
    
    async def _poll_json_job_result(self, job_id: str, max_attempts: int = 15) -> Optional[Dict[str, Any]]:
        """Poll for PDF to JSON job completion."""
        import asyncio
        
        url = f"{self.API_BASE_URL}/job/check"
        
        for attempt in range(max_attempts):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        url,
                        headers=self.headers,
                        json={"jobId": job_id}
                    )
                    response.raise_for_status()
                    result = response.json()
                
                status = result.get("status")
                
                if status == "success":
                    body = result.get("body") or result.get("text")
                    if isinstance(body, str):
                        try:
                            return json.loads(body)
                        except json.JSONDecodeError:
                            return None
                    elif isinstance(body, dict):
                        return body
                    return None
                
                elif status == "working":
                    await asyncio.sleep(2)
                    continue
                
                else:
                    logger.warning(f"PDF.co JSON job {job_id} status: {status}")
                    return None
                    
            except Exception as e:
                logger.warning(f"Error polling PDF.co JSON job {job_id}: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(2)
                    continue
                return None
        
        return None
    
    async def _poll_image_job_result(self, job_id: str, max_attempts: int = 15) -> Optional[bytes]:
        """
        Poll for async image-to-PDF job completion.
        
        Args:
            job_id: Job ID from PDF.co
            max_attempts: Maximum polling attempts
            
        Returns:
            PDF bytes or None
        """
        import asyncio
        
        url = f"{self.API_BASE_URL}/job/check"
        
        for attempt in range(max_attempts):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        url,
                        headers=self.headers,
                        json={"jobId": job_id}
                    )
                    response.raise_for_status()
                    result = response.json()
                
                if result.get("status") == "success":
                    # Job completed - get PDF
                    pdf_url = result.get("url")
                    pdf_base64 = result.get("body") or result.get("pdf")
                    
                    if pdf_base64 and isinstance(pdf_base64, str):
                        if pdf_base64.startswith("data:"):
                            pdf_base64_data = pdf_base64.split(",")[1] if "," in pdf_base64 else pdf_base64
                        else:
                            pdf_base64_data = pdf_base64
                        
                        try:
                            return base64.b64decode(pdf_base64_data)
                        except:
                            pass
                    
                    if pdf_url:
                        # Download PDF from URL
                        async with httpx.AsyncClient(timeout=30.0) as client:
                            pdf_response = await client.get(pdf_url)
                            pdf_response.raise_for_status()
                            return pdf_response.content
                
                elif result.get("status") == "working":
                    # Still processing, wait and retry
                    await asyncio.sleep(3)  # Wait longer for image processing
                    continue
                
                else:
                    # Job failed or unknown status
                    logger.warning(f"PDF.co image job {job_id} status: {result.get('status')}")
                    return None
                    
            except Exception as e:
                logger.warning(f"Error polling PDF.co image job {job_id}: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(3)
                    continue
                return None
        
        logger.warning(f"PDF.co image job {job_id} did not complete after {max_attempts} attempts")
        return None
    
    async def _poll_job_result(self, job_id: str, max_attempts: int = 10) -> Optional[str]:
        """
        Poll for async job completion.
        
        Args:
            job_id: Job ID from PDF.co
            max_attempts: Maximum polling attempts
            
        Returns:
            Extracted text or None
        """
        import asyncio
        
        url = f"{self.API_BASE_URL}/job/check"
        
        for attempt in range(max_attempts):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        url,
                        headers=self.headers,
                        json={"jobId": job_id}
                    )
                    response.raise_for_status()
                    result = response.json()
                
                status = result.get("status")
                
                if status == "success":
                    # Job completed - extract text from various possible fields
                    text = (
                        result.get("body") or 
                        result.get("text") or 
                        result.get("content") or
                        result.get("data") or
                        ""
                    )
                    if text and isinstance(text, str) and text.strip():
                        return text.strip()
                    else:
                        logger.warning(f"PDF.co job {job_id} completed but no text found")
                        return None
                
                elif status == "working":
                    # Still processing, wait and retry
                    await asyncio.sleep(2)
                    continue
                
                else:
                    # Job failed or unknown status
                    error_msg = result.get("error") or result.get("message", f"Unknown status: {status}")
                    logger.warning(f"PDF.co job {job_id} status: {status}, error: {error_msg}")
                    return None
                    
            except Exception as e:
                logger.warning(f"Error polling PDF.co job {job_id}: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(2)
                    continue
                return None
        
        logger.warning(f"PDF.co job {job_id} did not complete after {max_attempts} attempts")
        return None
    
    async def _extract_text_from_url(self, pdf_url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extract text from PDF URL.
        
        Args:
            pdf_url: URL to PDF file
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        try:
            url = f"{self.API_BASE_URL}/pdf/convert/to/text"
            
            payload = {
                "url": pdf_url,
                "inline": True
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
            
            text = result.get("body") or result.get("text") or ""
            if text and text.strip():
                return True, text.strip(), None
            else:
                return False, None, "No text extracted from PDF URL"
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF URL: {e}")
            return False, None, str(e)
    
    def _structured_to_text(self, structured_data: Dict[str, Any]) -> str:
        """
        Convert structured JSON data to plain text for fallback.
        
        Args:
            structured_data: JSON dict from Document Parser
            
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
                    else:
                        text_parts.append(f"{prefix}{key}: {value}")
            elif isinstance(obj, list):
                for item in obj:
                    extract_text(item, prefix)
            else:
                text_parts.append(f"{prefix}{obj}")
        
        extract_text(structured_data)
        return "\n".join(text_parts)
    
    def _json_structure_to_text(self, json_data: Dict[str, Any]) -> str:
        """
        Convert PDF to JSON structure to plain text.
        
        Args:
            json_data: JSON dict from PDF to JSON
            
        Returns:
            Plain text representation
        """
        if not json_data:
            return ""
        
        # PDF.co JSON structure typically has pages, text, etc.
        text_parts = []
        
        if "pages" in json_data and isinstance(json_data["pages"], list):
            for page in json_data["pages"]:
                if "text" in page:
                    text_parts.append(page["text"])
        elif "text" in json_data:
            text_parts.append(json_data["text"])
        elif "body" in json_data:
            # Try to extract text from body
            body = json_data["body"]
            if isinstance(body, str):
                text_parts.append(body)
            elif isinstance(body, dict):
                return self._structured_to_text(body)
        
        return "\n".join(text_parts)


# Singleton instance
_pdfco_service: Optional[PDFCoService] = None


def get_pdfco_service() -> PDFCoService:
    """Get singleton PDF.co service instance."""
    global _pdfco_service
    if _pdfco_service is None:
        _pdfco_service = PDFCoService()
    return _pdfco_service
