"""
PDF.co service module.

Provides OCR and advanced PDF processing capabilities as fallback.
"""

from .service import PDFCoService, get_pdfco_service

__all__ = ["PDFCoService", "get_pdfco_service"]

