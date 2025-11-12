"""
PDF Report Generator for Interviewer Results.

Generates comprehensive PDF reports with job details, candidate analysis, and recommendations.
Uses ShortlistAI branding (colors, logo, header, footer).
"""

import io
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

from .branding import get_branding, ShortlistAIBranding

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generate PDF reports for interviewer analysis results with ShortlistAI branding."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.branding = get_branding()
        self.branding.ensure_fonts_registered()
        self._setup_custom_styles()
    
    def _get_style(self, preferred_name: str, fallback_name: str):
        """Get style with fallback."""
        try:
            return self.styles[preferred_name]
        except KeyError:
            return self.styles[fallback_name]
    
    def _normalize_list_field(self, value):
        """Normalize a field that might be a list, dict, or None."""
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            # Try common keys for nested lists
            for key in ("items", "flags", "values", "value"):
                maybe = value.get(key)
                if isinstance(maybe, list):
                    return maybe
        if value is None:
            return []
        return [value]
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles with ShortlistAI branding."""
        # Get branded styles
        branded_styles = self.branding.get_custom_styles(self.styles)
        
        if self.branding.fonts_available():
            self.styles['Normal'].fontName = 'Inter-Regular'
            self.styles['BodyText'].fontName = 'Inter-Regular'
            self.styles['Title'].fontName = 'Inter-Bold'
            self.styles['Heading1'].fontName = 'Inter-Bold'
            self.styles['Heading2'].fontName = 'Inter-SemiBold'
            self.styles['Heading3'].fontName = 'Inter-SemiBold'
        
        # Add all branded styles to stylesheet
        for name, style in branded_styles.items():
            self.styles.add(style)
        
        # Add legacy style mappings for compatibility
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=branded_styles['BrandedTitle']
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=branded_styles['BrandedSectionHeader']
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=branded_styles['BrandedSubSection']
        ))
        
        # Body text justified
        self.styles.add(ParagraphStyle(
            name='BodyJustified',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
        
        # Highlight box (now using branded success color)
        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=branded_styles['SuccessBox']
        ))
    
    def generate_interviewer_report(
        self,
        session_data: Dict[str, Any],
        results: List[Dict[str, Any]],
        executive_recommendation: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Generate comprehensive PDF report for interviewer analysis.
        
        Args:
            session_data: Session data with job posting, weights, etc.
            results: List of candidate analysis results
            executive_recommendation: AI-generated executive recommendation
            
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        
        # Create PDF document with branded header/footer
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=self.branding.get_header_height() + self.branding.get_content_top_padding(),
            bottomMargin=inch
        )
        
        # Build content
        story = []
        
        # Title page
        story.extend(self._build_title_page(session_data))
        story.append(PageBreak())
        
        # Job description section
        story.extend(self._build_job_section(session_data))
        story.append(Spacer(1, 0.2*inch))
        
        # Evaluation criteria section
        story.extend(self._build_criteria_section(session_data))
        story.append(PageBreak())
        
        # Executive recommendation (if available)
        if executive_recommendation:
            story.extend(self._build_executive_recommendation(executive_recommendation))
            story.append(PageBreak())
        
        # Candidate rankings
        story.extend(self._build_rankings_section(results))
        story.append(PageBreak())
        
        # Detailed candidate profiles
        story.extend(self._build_candidate_details(results))
        
        # Build PDF with branded header and footer
        doc.build(
            story,
            onFirstPage=self._add_branded_page,
            onLaterPages=self._add_branded_page
        )
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _add_branded_page(self, canvas_obj, doc):
        """Add branded header and footer to page."""
        self.branding.create_header(canvas_obj, doc)
        self.branding.create_footer(canvas_obj, doc)
    
    def _build_title_page(self, session_data: Dict[str, Any]) -> List:
        """Build branded title page."""
        elements = []
        
        # Logo image (centered)
        elements.append(Spacer(1, 0.8*inch))
        
        # Try to add logo image
        logo_img = self.branding.get_logo_image(width=1.4*inch)
        show_wordmark = True
        if logo_img:
            # Center both Image and Paragraph fallback
            if hasattr(logo_img, "hAlign"):
                logo_img.hAlign = 'CENTER'
            if isinstance(logo_img, Paragraph):
                logo_img.style.alignment = TA_CENTER
                show_wordmark = False
            elements.append(logo_img)
        else:
            # Fallback to text logo
            elements.append(Paragraph(
                '<font size="34" color="#0066FF"><b>ShortlistAI</b></font>',
                ParagraphStyle(
                    name='LogoStyleFallback',
                    parent=self.styles['Normal'],
                    alignment=TA_CENTER,
                    spaceAfter=10
                )
            ))
            show_wordmark = False
        
        elements.append(Spacer(1, 0.15*inch))
        if show_wordmark:
            elements.append(Paragraph(
                '<font size="13" color="#111827"><b>ShortlistAI</b></font>',
                ParagraphStyle(
                    name='Wordmark',
                    parent=self.styles['Normal'],
                    alignment=TA_CENTER,
                    spaceAfter=4
                )
            ))
        elements.append(Paragraph(
            '<font size="11" color="#6B7280">AI-Powered CV Analysis Platform</font>',
            ParagraphStyle(
                name='TaglineStyle',
                parent=self.styles['Normal'],
                alignment=TA_CENTER,
                spaceAfter=20
            )
        ))
        
        # Main title
        elements.append(Spacer(1, 0.4*inch))
        elements.append(Paragraph(
            '<font color="#0066FF"><b>Candidate Analysis Report</b></font>',
            self.styles['CustomTitle']
        ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Report Code (if available) - with branded style
        interviewer_data = session_data.get('data', {})
        report_code = interviewer_data.get('report_code')
        if report_code:
            elements.append(Paragraph(
                f'<font face="Courier-Bold" size="13" color="#7C3AED">Report Code: {report_code}</font>',
                ParagraphStyle(
                    name='ReportCodeDisplay',
                    parent=self.styles['Normal'],
                    alignment=TA_CENTER,
                    backColor=colors.HexColor('#F3F4F6'),
                    borderPadding=8,
                    spaceAfter=15
                )
            ))
            elements.append(Spacer(1, 0.15*inch))
        
        # Subtitle with date
        date_str = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(
            f"<b>Generated:</b> {date_str}",
            ParagraphStyle(
                name='Subtitle',
                parent=self.styles['Normal'],
                fontSize=12,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#6b7280')
            )
        ))
        
        elements.append(Spacer(1, inch))
        
        # Report metadata
        if interviewer_data.get('interviewer_id'):
            elements.append(Paragraph(
                "<b>Report prepared for:</b>",
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 0.1*inch))
            
            # Company info (if available)
            company_id = interviewer_data.get('company_id')
            if company_id:
                elements.append(Paragraph(
                    f"Company ID: {company_id}",
                    self.styles['Normal']
                ))
            
            # Report ID
            report_id = interviewer_data.get('report_id')
            if report_id:
                elements.append(Paragraph(
                    f"Report ID: {report_id}",
                    ParagraphStyle(
                        name='ReportID',
                        parent=self.styles['Normal'],
                        fontSize=9,
                        textColor=colors.HexColor('#9ca3af')
                    )
                ))
        
        return elements
    
    def _build_job_section(self, session_data: Dict[str, Any]) -> List:
        """Build job description section."""
        elements = []
        data = session_data.get('data', {})
        
        elements.append(Paragraph("Job Position Details", self.styles['SectionHeader']))
        
        # Job posting text - COMPLETE and FORMATTED
        job_text = data.get('job_posting_text', 'Not provided')
        elements.append(Paragraph(
            f"<b>Job Description:</b>",
            self.styles['SubSection']
        ))
        
        # Format job description with structure detection
        formatted_elements = self._format_job_description(job_text)
        elements.extend(formatted_elements)
        
        # Key points
        key_points = data.get('key_points') or data.get('suggested_key_points', '')
        if key_points:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(
                "<b>Key Requirements:</b>",
                self.styles['SubSection']
            ))
            # Split by bullet points or newlines
            for line in key_points.split('\n'):
                if line.strip():
                    elements.append(Paragraph(
                        f"• {line.strip()}",
                        self.styles['BodyText']
                    ))
        
        return elements
    
    def _build_criteria_section(self, session_data: Dict[str, Any]) -> List:
        """Build evaluation criteria section."""
        elements = []
        data = session_data.get('data', {})
        
        elements.append(Paragraph("Evaluation Criteria", self.styles['SectionHeader']))
        
        # Weights table
        weights = data.get('weights', {})
        if weights:
            elements.append(Paragraph(
                "<b>Category Weights:</b>",
                self.styles['SubSection']
            ))
            
            weight_data = [['Category', 'Weight']]
            for category, weight in weights.items():
                weight_data.append([
                    category.replace('_', ' ').title(),
                    f"{weight}%"
                ])
            
            weight_table = Table(weight_data, colWidths=[3*inch, 1.5*inch])
            # Use branding colors for table
            weight_table.setStyle(self.branding.create_branded_table_style(has_header=True))
            
            elements.append(weight_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Hard blockers
        hard_blockers = data.get('hard_blockers', [])
        if hard_blockers:
            elements.append(Paragraph(
                "<b>Hard Blockers (Must-Have Requirements):</b>",
                self.styles['SubSection']
            ))
            for blocker in hard_blockers:
                elements.append(Paragraph(
                    f"⚠️ {blocker}",
                    ParagraphStyle(
                        name='Blocker',
                        parent=self.styles['BodyText'],
                        textColor=colors.HexColor('#dc2626')
                    )
                ))
        
        # Nice to have
        nice_to_have = data.get('nice_to_have', [])
        if nice_to_have:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(
                "<b>Nice to Have (Preferred):</b>",
                self.styles['SubSection']
            ))
            for item in nice_to_have:
                elements.append(Paragraph(
                    f"• {item}",
                    self.styles['BodyText']
                ))
        
        return elements
    
    def _build_executive_recommendation(self, recommendation: Dict[str, Any]) -> List:
        """Build executive recommendation section."""
        elements = []
        
        elements.append(Paragraph(
            "📊 Executive Recommendation",
            self.styles['SectionHeader']
        ))
        
        # Top candidate highlight
        top_rec = recommendation.get('top_recommendation')
        if top_rec:
            elements.append(Paragraph(
                f"<b>✅ Recommended Candidate:</b> {top_rec.get('candidate_name', 'N/A')}",
                ParagraphStyle(
                    name='TopCandidate',
                    parent=self.styles['BodyText'],
                    fontSize=14,
                    textColor=colors.HexColor('#16a34a'),
                    spaceAfter=8
                )
            ))
            
            elements.append(Paragraph(
                top_rec.get('summary', ''),
                self.styles['BodyJustified']
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # Executive summary
        exec_summary = recommendation.get('executive_summary')
        if exec_summary:
            elements.append(Paragraph(
                "<b>Summary:</b>",
                self.styles['SubSection']
            ))
            # Split into paragraphs
            for para in exec_summary.split('\n\n'):
                if para.strip():
                    elements.append(Paragraph(
                        para.strip(),
                        self.styles['BodyJustified']
                    ))
        
        # Key insights
        insights = recommendation.get('key_insights', [])
        if insights:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(
                "<b>Key Insights:</b>",
                self.styles['SubSection']
            ))
            for insight in insights:
                elements.append(Paragraph(
                    f"• {insight}",
                    self.styles['BodyText']
                ))
        
        return elements
    
    def _build_rankings_section(self, results: List[Dict[str, Any]]) -> List:
        """Build candidate rankings table."""
        elements = []
        
        elements.append(Paragraph(
            f"Candidate Rankings ({len(results)} Total)",
            self.styles['SectionHeader']
        ))
        
        # SORT candidates by global_score DESCENDING
        sorted_results = sorted(
            results, 
            key=lambda x: x.get('global_score', 0), 
            reverse=True
        )
        
        # Prepare table data
        table_data = [['Rank', 'Candidate', 'Score', 'Blockers']]
        
        for idx, result in enumerate(sorted_results, 1):
            name = self._get_candidate_name(result, idx)
            score = result.get('global_score', 0)
            blockers = result.get('hard_blocker_flags', [])
            blocker_text = '⚠️ Yes' if blockers else '✓ None'
            
            table_data.append([
                f"#{idx}",
                name,
                f"{score:.1f}/5",
                blocker_text
            ])
        
        # Create table with branded style
        table = Table(table_data, colWidths=[0.6*inch, 3*inch, 0.8*inch, 1*inch])
        table.setStyle(self.branding.create_branded_table_style(has_header=True))
        
        elements.append(table)
        
        return elements
    
    def _build_candidate_details(self, results: List[Dict[str, Any]]) -> List:
        """Build detailed candidate profiles."""
        elements = []
        
        elements.append(Paragraph(
            "Detailed Candidate Analysis",
            self.styles['SectionHeader']
        ))
        
        # SORT candidates by global_score DESCENDING (same as rankings)
        sorted_results = sorted(
            results, 
            key=lambda x: x.get('global_score', 0), 
            reverse=True
        )
        
        for idx, result in enumerate(sorted_results, 1):
            # Keep each candidate on same page if possible
            candidate_elements = []
            
            name = self._get_candidate_name(result, idx)
            candidate_elements.append(Paragraph(
                f"#{idx}: {name}",
                self.styles['SubSection']
            ))
            
            # Score and categories
            score = result.get('global_score', 0)
            candidate_elements.append(Paragraph(
                f"<b>Global Score:</b> {score:.1f}/5",
                self.styles['BodyText']
            ))
            
            # Categories table
            categories = result.get('categories', {})
            if categories:
                cat_data = [['Category', 'Score']]
                for cat, score in categories.items():
                    cat_data.append([
                        cat.replace('_', ' ').title(),
                        f"{score}/5"
                    ])
                
                cat_table = Table(cat_data, colWidths=[2.5*inch, inch])
                cat_table.setStyle(self.branding.create_branded_table_style(has_header=True))
                candidate_elements.append(cat_table)
                candidate_elements.append(Spacer(1, 0.1*inch))
            
            # Strengths
            strengths = result.get('strengths', [])
            if strengths:
                candidate_elements.append(Paragraph(
                    "<b>✓ Strengths:</b>",
                    self.styles['BodyText']
                ))
                for strength in strengths:
                    candidate_elements.append(Paragraph(
                        f"• {strength}",
                        ParagraphStyle(
                            name='Strength',
                            parent=self.styles['BodyText'],
                            leftIndent=15
                        )
                    ))
            
            # Risks
            risks = result.get('risks', [])
            if risks:
                candidate_elements.append(Paragraph(
                    "<b>⚠️ Risks & Gaps:</b>",
                    self.styles['BodyText']
                ))
                for risk in risks:
                    candidate_elements.append(Paragraph(
                        f"• {risk}",
                        ParagraphStyle(
                            name='Risk',
                            parent=self.styles['BodyText'],
                            leftIndent=15,
                            textColor=colors.HexColor('#d97706')
                        )
                    ))
            
            # Hard blocker violations (if any)
            blocker_flags = result.get('hard_blocker_flags', [])
            if blocker_flags:
                candidate_elements.append(Paragraph(
                    "<b>🔴 Hard Blocker Violations:</b>",
                    self.styles['BodyText']
                ))
                for blocker in blocker_flags:
                    candidate_elements.append(Paragraph(
                        f"⚠️ {blocker}",
                        ParagraphStyle(
                            name='Blocker',
                            parent=self.styles['BodyText'],
                            leftIndent=15,
                            textColor=colors.HexColor('#dc2626'),
                            fontName='Helvetica-Bold'
                        )
                    ))
            
            # Interview questions (ALL questions, not just top 3)
            questions = result.get('questions', [])
            if questions:
                candidate_elements.append(Paragraph(
                    f"<b>❓ Suggested Interview Questions ({len(questions)} total):</b>",
                    self.styles['BodyText']
                ))
                for i, q in enumerate(questions, 1):
                    candidate_elements.append(Paragraph(
                        f"{i}. {q}",
                        ParagraphStyle(
                            name='Question',
                            parent=self.styles['BodyText'],
                            leftIndent=15,
                            fontSize=10,
                            spaceAfter=4
                        )
                    ))
            
            # Wrap in KeepTogether to avoid page breaks in middle of candidate
            elements.append(KeepTogether(candidate_elements))
            
            # Add separator unless last candidate
            if idx < len(results):
                elements.append(Spacer(1, 0.3*inch))
                elements.append(Paragraph(
                    "─" * 80,
                    ParagraphStyle(
                        name='Separator',
                        parent=self.styles['Normal'],
                        textColor=colors.HexColor('#e5e7eb')
                    )
                ))
                elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _format_job_description(self, job_text: str) -> List:
        """
        Format job description with automatic structure detection.
        
        Detects and formats:
        - Section headers (CAPS or ending with :)
        - Bullet points (-, *, •)
        - Paragraphs
        - Empty lines
        """
        elements = []
        lines = job_text.split('\n')
        current_paragraph = []
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                # Flush current paragraph
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    elements.append(Paragraph(para_text, self.styles['BodyJustified']))
                    current_paragraph = []
                continue
            
            # Detect section header (all CAPS or ends with :)
            is_section = False
            if len(stripped) > 3:
                # Check if mostly uppercase (more than 70% caps)
                caps_ratio = sum(1 for c in stripped if c.isupper()) / len(stripped.replace(' ', ''))
                if caps_ratio > 0.7 or stripped.endswith(':'):
                    is_section = True
            
            if is_section:
                # Flush current paragraph
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    elements.append(Paragraph(para_text, self.styles['BodyJustified']))
                    current_paragraph = []
                
                # Add section header
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph(
                    f"<b>{stripped}</b>",
                    ParagraphStyle(
                        name='JobSection',
                        parent=self.styles['BodyText'],
                        fontSize=12,
                        textColor=colors.HexColor('#1e40af'),
                        spaceAfter=6,
                        fontName='Helvetica-Bold'
                    )
                ))
                continue
            
            # Detect bullet point (starts with -, *, •, or number.)
            is_bullet = False
            bullet_text = stripped
            for bullet_char in ['-', '*', '•', '–', '—']:
                if stripped.startswith(bullet_char):
                    is_bullet = True
                    bullet_text = stripped[1:].strip()
                    break
            
            # Also check for numbered bullets (1. 2. etc)
            if not is_bullet and len(stripped) > 2:
                if stripped[0].isdigit() and stripped[1] in ['.', ')', ':']:
                    is_bullet = True
                    bullet_text = stripped[2:].strip()
            
            if is_bullet:
                # Flush current paragraph
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    elements.append(Paragraph(para_text, self.styles['BodyJustified']))
                    current_paragraph = []
                
                # Add bullet point
                elements.append(Paragraph(
                    f"• {bullet_text}",
                    ParagraphStyle(
                        name='BulletPoint',
                        parent=self.styles['BodyText'],
                        leftIndent=15,
                        spaceAfter=4
                    )
                ))
                continue
            
            # Regular text - accumulate into paragraph
            current_paragraph.append(stripped)
        
        # Flush remaining paragraph
        if current_paragraph:
            para_text = ' '.join(current_paragraph)
            elements.append(Paragraph(para_text, self.styles['BodyJustified']))
        
        return elements
    
    def _get_candidate_name(self, result: Dict[str, Any], idx: int) -> str:
        """Extract candidate name from result."""
        summary = result.get('summary', {})
        if summary and summary.get('full_name'):
            name = summary['full_name']
            if summary.get('current_role'):
                name += f" ({summary['current_role']})"
            return name
        
        if result.get('candidate_label'):
            return result['candidate_label']
        
        return f"Candidate {idx}"
    
    def generate_candidate_report(
        self,
        session_data: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> bytes:
        """
        Generate comprehensive PDF preparation guide for candidate.
        
        Args:
            session_data: Session data with candidate info
            analysis: Analysis results with scores, strengths, gaps, strategies
            
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        
        # Create PDF document with branded header/footer
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=self.branding.get_header_height() + self.branding.get_content_top_padding(),
            bottomMargin=inch
        )
        
        # Build content
        story = []
        
        # Title page (same format as interviewer report)
        story.append(Paragraph(
            '<font color="#0066FF"><b>Interview Preparation Guide</b></font>',
            self.styles['CustomTitle']
        ))
        story.append(Spacer(1, 0.3 * inch))
        
        # Candidate info
        candidate_data = session_data.get("data", {})
        candidate_name = candidate_data.get("name", "Candidate")
        story.append(Paragraph(
            f"<b>Prepared for:</b> {candidate_name}",
            self.styles['Heading2']
        ))
        story.append(Spacer(1, 0.5 * inch))
        
        # Overall Score
        global_score = analysis.get("global_score", 0)
        story.append(Paragraph(
            f"<b>Overall Fit Score:</b> {global_score:.1f}/5.0",
            self._get_style('BrandedHeading', 'Heading1')
        ))
        story.append(Spacer(1, 0.3 * inch))
        
        # Category Scores
        story.append(Paragraph("Category Scores", self._get_style('BrandedHeading', 'Heading1')))
        story.append(Spacer(1, 0.1 * inch))
        
        categories = analysis.get("categories", {})
        if categories:
            cat_data = [["Category", "Score"]]
            for cat, score in categories.items():
                cat_data.append([cat.replace("_", " ").title(), f"{score}/5"])
            
            cat_table = Table(cat_data, colWidths=[4 * inch, 1.5 * inch])
            cat_table.setStyle(self.branding.create_branded_table_style())
            story.append(cat_table)
        
        story.append(Spacer(1, 0.4 * inch))
        
        # Your Strengths
        story.append(Paragraph("✓ Your Strengths", self._get_style('BrandedHeading', 'Heading1')))
        story.append(Spacer(1, 0.1 * inch))
        
        strengths = self._normalize_list_field(analysis.get("strengths"))
        for strength in strengths:
            story.append(Paragraph(
                f"• {strength}",
                self._get_style('BrandedBody', 'BodyText')
            ))
            story.append(Spacer(1, 0.05 * inch))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Areas to Address
        story.append(Paragraph("⚠ Areas to Address", self._get_style('BrandedHeading', 'Heading1')))
        story.append(Spacer(1, 0.1 * inch))
        
        gaps = self._normalize_list_field(analysis.get("risks"))
        for gap in gaps:
            story.append(Paragraph(
                f"• {gap}",
                self._get_style('BrandedBody', 'BodyText')
            ))
            story.append(Spacer(1, 0.05 * inch))
        
        story.append(Spacer(1, 0.3 * inch))
        story.append(PageBreak())
        
        # How to Address Gaps
        questions_data = analysis.get("questions") or {}
        gap_strategies = self._normalize_list_field(questions_data.get("gap_strategies"))
        
        if gap_strategies:
            story.append(Paragraph("💡 How to Address Your Gaps", self._get_style('BrandedHeading', 'Heading1')))
            story.append(Spacer(1, 0.1 * inch))
            
            for idx, strategy in enumerate(gap_strategies, 1):
                if isinstance(strategy, dict):
                    gap_name = strategy.get("gap", f"Gap {idx}")
                    how_to = strategy.get("how_to_address", "")
                    talking_points = self._normalize_list_field(strategy.get("talking_points"))
                    
                    story.append(Paragraph(
                        f"<b>{idx}. {gap_name}</b>",
                        self._get_style('BrandedSubheading', 'Heading2')
                    ))
                    story.append(Spacer(1, 0.05 * inch))
                    
                    if how_to:
                        story.append(Paragraph(how_to, self._get_style('BrandedBody', 'BodyText')))
                        story.append(Spacer(1, 0.05 * inch))
                    
                    if talking_points:
                        for point in talking_points:
                            story.append(Paragraph(
                                f"  → {point}",
                                self._get_style('BrandedBody', 'BodyText')
                            ))
                            story.append(Spacer(1, 0.03 * inch))
                    
                    story.append(Spacer(1, 0.15 * inch))
            
            story.append(PageBreak())
        
        # Likely Interview Questions
        story.append(Paragraph("❓ Likely Interview Questions", self._get_style('BrandedHeading', 'Heading1')))
        story.append(Spacer(1, 0.1 * inch))
        
        questions = self._normalize_list_field(questions_data.get("items") or analysis.get("questions"))
        
        # Try to get separate answers array (new format)
        answers_array = self._normalize_list_field(analysis.get("answers") or questions_data.get("answers") or [])
        
        for idx, question_item in enumerate(questions, 1):
            # Handle both dict and string formats
            if isinstance(question_item, dict):
                question_text = question_item.get("q") or question_item.get("question", "")
                suggested_answer = question_item.get("a") or question_item.get("answer") or question_item.get("suggested_answer", "")
                category = question_item.get("category", "")
            else:
                question_text = str(question_item)
                # Try to get answer from parallel answers array
                suggested_answer = answers_array[idx - 1] if (idx - 1) < len(answers_array) else ""
                category = ""
            
            # Question with category tag
            if category:
                story.append(Paragraph(
                    f"<b>{idx}. [{category.replace('_', ' ').title()}] {question_text}</b>",
                    self._get_style('BrandedSubheading', 'Heading2')
                ))
            else:
                story.append(Paragraph(
                    f"<b>{idx}. {question_text}</b>",
                    self._get_style('BrandedSubheading', 'Heading2')
                ))
            
            story.append(Spacer(1, 0.05 * inch))
            
            # Suggested answer if available
            if suggested_answer:
                story.append(Paragraph(
                    f"<i>Suggested approach:</i> {suggested_answer}",
                    self._get_style('BrandedBodySmall', 'Normal')
                ))
            else:
                story.append(Paragraph(
                    "<i>Use STAR method: Situation → Task → Action → Result. Quantify your impact.</i>",
                    self._get_style('BrandedBodySmall', 'Normal')
                ))
            
            story.append(Spacer(1, 0.2 * inch))
        
        story.append(Spacer(1, 0.2 * inch))
        story.append(PageBreak())
        
        # Intro Pitch
        intro_pitch = analysis.get("intro_pitch", "")
        if intro_pitch:
            story.append(Paragraph("🎯 Your Intro Pitch", self._get_style('BrandedHeading', 'Heading1')))
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph(
                f'"{intro_pitch}"',
                self._get_style('BrandedBodyItalic', 'BodyText')
            ))
            story.append(Spacer(1, 0.3 * inch))
        
        # Preparation Tips/Notes
        prep_tips = self._normalize_list_field(
            questions_data.get("notes") or
            questions_data.get("preparation_tips") or
            analysis.get("notes") or
            analysis.get("preparation_tips")
        )
        if prep_tips:
            story.append(Paragraph("📚 Preparation Checklist", self._get_style('BrandedHeading', 'Heading1')))
            story.append(Spacer(1, 0.1 * inch))
            
            for tip in prep_tips:
                story.append(Paragraph(
                    f"☐ {tip}",
                    self._get_style('BrandedBody', 'BodyText')
                ))
                story.append(Spacer(1, 0.08 * inch))
        
        # Build PDF with branded header/footer (same as interviewer report)
        doc.build(
            story,
            onFirstPage=self._add_branded_page,
            onLaterPages=self._add_branded_page
        )
        
        return buffer.getvalue()


# Global instance
_pdf_generator: Optional[PDFReportGenerator] = None


def get_pdf_report_generator() -> PDFReportGenerator:
    """Get global PDF report generator instance."""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = PDFReportGenerator()
    return _pdf_generator

