"""
PDF Branding Module for ShortlistAI.

Provides consistent branding elements (colors, logo, header, footer) for all PDF reports.
"""

from pathlib import Path
from typing import Optional, Tuple
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Image, Table, TableStyle
from reportlab.pdfgen import canvas
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ShortlistAIBranding:
    """
    ShortlistAI brand identity for PDF documents.
    
    Brand Colors:
    - AI Blue: #0066FF (primary)
    - Neural Purple: #7C3AED (secondary)
    - Success Green: #10B981
    - Warning Orange: #F59E0B
    - Error Red: #EF4444
    """
    
    # Brand Colors
    AI_BLUE = colors.HexColor('#0066FF')
    AI_BLUE_DARK = colors.HexColor('#3388FF')
    NEURAL_PURPLE = colors.HexColor('#7C3AED')
    NEURAL_PURPLE_LIGHT = colors.HexColor('#9F7AEA')
    
    # Semantic Colors
    SUCCESS_GREEN = colors.HexColor('#10B981')
    WARNING_ORANGE = colors.HexColor('#F59E0B')
    ERROR_RED = colors.HexColor('#EF4444')
    
    # Neutrals
    TEXT_PRIMARY_LIGHT = colors.HexColor('#111827')
    TEXT_SECONDARY_LIGHT = colors.HexColor('#6B7280')
    BG_LIGHT = colors.HexColor('#F8F9FA')
    BORDER_LIGHT = colors.HexColor('#E5E7EB')
    
    # Logo path
    _LOGO_PATH = None
    
    @classmethod
    def get_logo_path(cls) -> Optional[Path]:
        """Get path to ShortlistAI logo PNG."""
        if cls._LOGO_PATH is None:
            # Try multiple possible locations for the logo
            backend_root = Path(__file__).parent.parent.parent.parent
            
            # Try project root public/assets first (updated paths for correct logos)
            logo_paths = [
                backend_root / "public" / "icons" / "icon-512x512.png",
                backend_root / "public" / "assets" / "logos" / "app-icon-512.png",
                backend_root / "src" / "frontend" / "public" / "icons" / "icon-512x512.png",
                backend_root / "src" / "frontend" / "public" / "assets" / "logos" / "app-icon-512.png",
                backend_root / "src" / "backend" / "assets" / "logo.png",
            ]
            
            for logo_path in logo_paths:
                if logo_path.exists():
                    cls._LOGO_PATH = logo_path
                    logger.info(f"Logo found at: {logo_path}")
                    break
            else:
                logger.warning(f"Logo not found. Tried: {', '.join(str(p) for p in logo_paths)}")
        
        return cls._LOGO_PATH
    
    @classmethod
    def get_logo_image(cls, width: float = 0.7*inch, height: Optional[float] = None) -> Optional[Image]:
        """
        Get ShortlistAI logo as ReportLab Image.
        
        Args:
            width: Logo width in inches (default 0.7")
            height: Logo height (auto if None, maintains aspect ratio)
        
        Returns:
            Image object or None if logo not found
        """
        logo_path = cls.get_logo_path()
        
        if not logo_path:
            # Fallback to text logo
            from reportlab.platypus import Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            
            styles = getSampleStyleSheet()
            logo_style = ParagraphStyle(
                name='LogoStyle',
                parent=styles['Normal'],
                fontSize=20,
                fontName='Helvetica-Bold',
                textColor=cls.AI_BLUE,
                alignment=TA_LEFT
            )
            
            return Paragraph('<font color="#0066FF"><b>ShortlistAI</b></font>', logo_style)
        
        try:
            # Load PNG logo
            # If height not specified, maintain aspect ratio (logo is square)
            if height is None:
                height = width
            
            img = Image(str(logo_path), width=width, height=height)
            return img
            
        except Exception as e:
            logger.error(f"Error loading logo from {logo_path}: {e}")
            # Fallback to text
            from reportlab.platypus import Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            
            styles = getSampleStyleSheet()
            logo_style = ParagraphStyle(
                name='LogoStyle',
                parent=styles['Normal'],
                fontSize=20,
                fontName='Helvetica-Bold',
                textColor=cls.AI_BLUE,
                alignment=TA_LEFT
            )
            
            return Paragraph('<font color="#0066FF"><b>ShortlistAI</b></font>', logo_style)
    
    @classmethod
    def create_header(cls, canvas_obj, doc):
        """
        Create branded header for PDF pages.
        
        Args:
            canvas_obj: ReportLab canvas
            doc: Document object
        """
        # Save state
        canvas_obj.saveState()
        
        header_top = doc.height + doc.topMargin
        logo_size = 0.65 * inch
        logo_y = header_top - logo_size - 0.2 * inch
        logo_x = doc.leftMargin
        logo_path = cls.get_logo_path()

        if logo_path:
            canvas_obj.drawImage(
                str(logo_path),
                logo_x,
                logo_y,
                width=logo_size,
                height=logo_size,
                mask="auto"
            )
            text_x = logo_x + logo_size + 0.2 * inch
        else:
            # Text fallback for logo
            canvas_obj.setFont("Helvetica-Bold", 18)
            canvas_obj.setFillColor(cls.AI_BLUE)
            canvas_obj.drawString(logo_x, logo_y + logo_size / 2, "ShortlistAI")
            text_x = logo_x + 1.6 * inch

        # Brand name (text) and tagline
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.setFillColor(cls.AI_BLUE)
        canvas_obj.drawString(text_x, logo_y + logo_size - 10, "ShortlistAI")

        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.setFillColor(cls.TEXT_SECONDARY_LIGHT)
        canvas_obj.drawString(text_x, logo_y + logo_size - 25, "AI-Powered CV Analysis Platform")

        # Draw header accent line
        line_y = logo_y - 0.1 * inch
        canvas_obj.setStrokeColor(cls.AI_BLUE)
        canvas_obj.setLineWidth(2)
        canvas_obj.line(
            doc.leftMargin,
            line_y,
            doc.width + doc.leftMargin,
            line_y
        )
        
        # Restore state
        canvas_obj.restoreState()
    
    @classmethod
    def create_footer(cls, canvas_obj, doc):
        """
        Create branded footer for PDF pages.
        
        Args:
            canvas_obj: ReportLab canvas
            doc: Document object
        """
        # Save state
        canvas_obj.saveState()
        
        footer_top = 0.85 * inch

        # Draw footer line
        canvas_obj.setStrokeColor(cls.BORDER_LIGHT)
        canvas_obj.setLineWidth(1)
        canvas_obj.line(
            doc.leftMargin,
            footer_top,
            doc.width + doc.leftMargin,
            footer_top
        )
        
        # Page number (center)
        page_num = canvas_obj.getPageNumber()
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(cls.TEXT_SECONDARY_LIGHT)
        canvas_obj.drawCentredString(
            doc.width / 2 + doc.leftMargin,
            footer_top - 0.2*inch,
            f"Page {page_num}"
        )
        
        # Confidential notice (left)
        canvas_obj.setFont('Helvetica-Oblique', 8)
        canvas_obj.drawString(
            doc.leftMargin,
            footer_top - 0.2*inch,
            "Confidential — For internal hiring use only"
        )
        
        # ShortlistAI branding (right)
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.drawRightString(
            doc.width + doc.leftMargin,
            footer_top - 0.2*inch,
            "shortlistai.com · privacy@shortlistai.com"
        )
        
        # Restore state
        canvas_obj.restoreState()
    
    @classmethod
    def get_custom_styles(cls, base_styles):
        """
        Get ShortlistAI branded paragraph styles.
        
        Args:
            base_styles: ReportLab StyleSheet
        
        Returns:
            Dict of custom styles
        """
        styles = {}
        
        # Branded Title
        styles['BrandedTitle'] = ParagraphStyle(
            name='BrandedTitle',
            parent=base_styles['Heading1'],
            fontSize=26,
            textColor=cls.AI_BLUE,
            spaceAfter=25,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Section Header with brand color
        styles['BrandedSectionHeader'] = ParagraphStyle(
            name='BrandedSectionHeader',
            parent=base_styles['Heading2'],
            fontSize=16,
            textColor=cls.AI_BLUE,
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=cls.AI_BLUE,
            borderPadding=0
        )
        
        # Subsection with purple accent
        styles['BrandedSubSection'] = ParagraphStyle(
            name='BrandedSubSection',
            parent=base_styles['Heading3'],
            fontSize=14,
            textColor=cls.NEURAL_PURPLE,
            spaceBefore=12,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        # Highlight box (success)
        styles['SuccessBox'] = ParagraphStyle(
            name='SuccessBox',
            parent=base_styles['BodyText'],
            fontSize=11,
            textColor=colors.white,
            backColor=cls.SUCCESS_GREEN,
            borderPadding=10,
            spaceAfter=15,
            borderRadius=4
        )
        
        # Warning box
        styles['WarningBox'] = ParagraphStyle(
            name='WarningBox',
            parent=base_styles['BodyText'],
            fontSize=11,
            textColor=colors.white,
            backColor=cls.WARNING_ORANGE,
            borderPadding=10,
            spaceAfter=15,
            borderRadius=4
        )
        
        # Info box (AI Blue)
        styles['InfoBox'] = ParagraphStyle(
            name='InfoBox',
            parent=base_styles['BodyText'],
            fontSize=11,
            backColor=colors.HexColor('#E6F0FF'),  # Light blue
            borderColor=cls.AI_BLUE,
            borderWidth=1,
            borderPadding=10,
            spaceAfter=15,
            leftIndent=10,
            rightIndent=10
        )
        
        # Metadata style
        styles['Metadata'] = ParagraphStyle(
            name='Metadata',
            parent=base_styles['Normal'],
            fontSize=10,
            textColor=cls.TEXT_SECONDARY_LIGHT,
            alignment=TA_CENTER,
            spaceAfter=6
        )
        
        # Report code style
        styles['ReportCode'] = ParagraphStyle(
            name='ReportCode',
            parent=base_styles['Normal'],
            fontSize=14,
            fontName='Courier-Bold',
            textColor=cls.NEURAL_PURPLE,
            alignment=TA_CENTER,
            spaceAfter=20,
            backColor=colors.HexColor('#F3F4F6')
        )
        
        return styles
    
    @classmethod
    def create_branded_table_style(cls, has_header: bool = True) -> TableStyle:
        """
        Create branded table style.
        
        Args:
            has_header: Whether table has header row
        
        Returns:
            TableStyle with brand colors
        """
        style_commands = [
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, cls.BORDER_LIGHT),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        
        if has_header:
            # Header row styling
            style_commands.extend([
                ('BACKGROUND', (0, 0), (-1, 0), cls.AI_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ])
            
            # Alternating row colors
            style_commands.append(
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, cls.BG_LIGHT])
            )
        
        return TableStyle(style_commands)
    
    @classmethod
    def get_score_color(cls, score: float) -> colors.Color:
        """
        Get color for score based on value.
        
        Args:
            score: Score from 0-100
        
        Returns:
            Color object
        """
        if score >= 80:
            return cls.SUCCESS_GREEN
        elif score >= 60:
            return cls.WARNING_ORANGE
        else:
            return cls.ERROR_RED


# Singleton instance
_branding: Optional[ShortlistAIBranding] = None


def get_branding() -> ShortlistAIBranding:
    """Get global branding instance."""
    global _branding
    if _branding is None:
        _branding = ShortlistAIBranding()
    return _branding

