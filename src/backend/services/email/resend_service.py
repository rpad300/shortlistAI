"""
Email service using Resend.

Handles sending transactional emails to interviewers and candidates.
"""

import os
from typing import List, Optional, Dict, Any
import resend
import logging

logger = logging.getLogger(__name__)


class ResendEmailService:
    """
    Service for sending emails via Resend.
    """
    
    def __init__(self):
        """Initialize Resend email service."""
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            logger.warning("RESEND_API_KEY not set. Email sending will fail.")
        else:
            resend.api_key = api_key
        
        self.from_email = os.getenv("FROM_EMAIL", "noreply@shortlistai.com")
    
    async def send_interviewer_summary(
        self,
        to_email: str,
        interviewer_name: str,
        job_title: str,
        candidate_count: int,
        top_candidates: List[Dict[str, Any]],
        language: str = "en"
    ) -> bool:
        """
        Send analysis summary to interviewer.
        
        Args:
            to_email: Recipient email
            interviewer_name: Name of the interviewer
            job_title: Title of the job posting
            candidate_count: Total number of candidates analyzed
            top_candidates: List of top 3-5 candidates with scores
            language: Email language (en, pt, fr, es)
            
        Returns:
            True if sent successfully
        """
        try:
            # TODO: Get localized email template
            subject = self._get_subject("interviewer_summary", language)
            html_content = self._build_interviewer_email_html(
                interviewer_name,
                job_title,
                candidate_count,
                top_candidates,
                language
            )
            
            response = resend.Emails.send({
                "from": self.from_email,
                "to": to_email,
                "subject": subject,
                "html": html_content
            })
            
            logger.info(f"Interviewer summary email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send interviewer email: {e}")
            return False
    
    async def send_candidate_preparation(
        self,
        to_email: str,
        candidate_name: str,
        job_title: str,
        scores: Dict[str, int],
        questions: List[str],
        intro_pitch: str,
        language: str = "en"
    ) -> bool:
        """
        Send preparation guide to candidate.
        
        Args:
            to_email: Recipient email
            candidate_name: Name of the candidate
            job_title: Title of the job posting
            scores: Dict of category scores
            questions: List of interview questions
            intro_pitch: Suggested intro pitch
            language: Email language
            
        Returns:
            True if sent successfully
        """
        try:
            subject = self._get_subject("candidate_preparation", language)
            html_content = self._build_candidate_email_html(
                candidate_name,
                job_title,
                scores,
                questions,
                intro_pitch,
                language
            )
            
            response = resend.Emails.send({
                "from": self.from_email,
                "to": to_email,
                "subject": subject,
                "html": html_content
            })
            
            logger.info(f"Candidate preparation email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send candidate email: {e}")
            return False
    
    def _get_subject(self, email_type: str, language: str) -> str:
        """Get localized email subject."""
        subjects = {
            "interviewer_summary": {
                "en": "Your CV Analysis Results",
                "pt": "Resultados da Análise de CVs",
                "fr": "Résultats de l'Analyse de CV",
                "es": "Resultados del Análisis de CVs"
            },
            "candidate_preparation": {
                "en": "Your Interview Preparation Guide",
                "pt": "Seu Guia de Preparação para Entrevista",
                "fr": "Votre Guide de Préparation à l'Entretien",
                "es": "Su Guía de Preparación para la Entrevista"
            }
        }
        return subjects.get(email_type, {}).get(language, subjects[email_type]["en"])
    
    def _build_interviewer_email_html(
        self,
        name: str,
        job_title: str,
        candidate_count: int,
        top_candidates: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Build HTML email for interviewer."""
        # TODO: Use proper email template
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #2563eb;">CV Analysis Complete</h1>
            <p>Hi {name},</p>
            <p>We've analyzed <strong>{candidate_count} candidates</strong> for your <strong>{job_title}</strong> position.</p>
            
            <h2>Top Candidates:</h2>
            <ul>
                {''.join([f'<li>{c.get("name", "Candidate")} - Score: {c.get("score", 0)}/5</li>' for c in top_candidates[:5]])}
            </ul>
            
            <p>View full results in your dashboard.</p>
            <p>Best regards,<br>ShortlistAI Team</p>
        </body>
        </html>
        """
    
    def _build_candidate_email_html(
        self,
        name: str,
        job_title: str,
        scores: Dict[str, int],
        questions: List[str],
        intro_pitch: str,
        language: str
    ) -> str:
        """Build HTML email for candidate."""
        # TODO: Use proper email template
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #2563eb;">Interview Preparation Guide</h1>
            <p>Hi {name},</p>
            <p>Here's your personalized preparation guide for <strong>{job_title}</strong>.</p>
            
            <h2>Your Scores:</h2>
            <ul>
                {''.join([f'<li>{category}: {score}/5</li>' for category, score in scores.items()])}
            </ul>
            
            <h2>Likely Interview Questions:</h2>
            <ol>
                {''.join([f'<li>{q}</li>' for q in questions[:10]])}
            </ol>
            
            <h2>Suggested Intro Pitch:</h2>
            <p><em>{intro_pitch}</em></p>
            
            <p>Good luck!<br>ShortlistAI Team</p>
        </body>
        </html>
        """


# Global email service instance
_email_service: Optional[ResendEmailService] = None


def get_email_service() -> ResendEmailService:
    """
    Get global email service instance.
    
    Returns:
        ResendEmailService singleton
    """
    global _email_service
    if _email_service is None:
        _email_service = ResendEmailService()
    return _email_service

