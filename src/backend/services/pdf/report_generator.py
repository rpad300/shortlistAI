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

# Translation dictionary for PDF reports
PDF_TRANSLATIONS = {
    'en': {
        'title': 'Candidate Analysis Report',
        'table_of_contents': 'Table of Contents',
        'job_position_details': 'Job Position Details',
        'job_description': 'Job Description',
        'key_requirements': 'Key Requirements',
        'evaluation_criteria': 'Evaluation Criteria',
        'category_weights': 'Category Weights',
        'hard_blockers': 'Hard Blockers (Must-Have Requirements)',
        'nice_to_have': 'Nice to Have (Preferred)',
        'executive_recommendation': 'Executive Recommendation',
        'recommended_candidate': 'Recommended Candidate',
        'summary': 'Summary',
        'key_insights': 'Key Insights',
        'candidate_rankings': 'Candidate Rankings',
        'total': 'Total',
        'rank': 'Rank',
        'candidate': 'Candidate',
        'score': 'Score',
        'blockers': 'Blockers',
        'yes': 'Yes',
        'none': 'None',
        'detailed_analysis': 'Detailed Candidate Analysis',
        'global_score': 'Global Score',
        'profile_summary': 'Profile Summary',
        'category_scores': 'Category Scores',
        'category': 'Category',
        'swot_analysis': 'SWOT Analysis',
        'strengths': 'Strengths',
        'weaknesses': 'Weaknesses',
        'opportunities': 'Opportunities',
        'threats': 'Threats',
        'and_more': '... and {count} more',
        'technical_skills': 'Technical Skills Evaluation (Hard Skills)',
        'technical_skills_legend': 'Legend: 1 = Basic, 2 = Intermediate, 3 = Advanced, 4 = Proficient, 5 = Expert',
        'competency': 'Competency',
        'justification': 'Justification',
        'missing_technical_skills': 'Missing Critical Technical Skills',
        'soft_skills': 'Interpersonal Skills Evaluation (Soft Skills)',
        'soft_skills_legend': 'Legend: 1 = Little evident, 2 = Partially demonstrated, 3 = Adequately demonstrated, 4 = Well demonstrated, 5 = Strongly demonstrated',
        'missing_soft_skills': 'Missing Important Interpersonal Skills',
        'professional_experience': 'Professional Experience Analysis',
        'relevance_to_position': 'Relevance to Position',
        'career_progression': 'Career Progression',
        'professional_stability': 'Professional Stability',
        'education_certifications': 'Academic Background and Certifications',
        'relevance_adequacy': 'Relevance and Adequacy',
        'evaluation': 'Evaluation',
        'certifications': 'Certifications',
        'notable_achievements': 'Notable Achievements and Relevant Projects',
        'impact': 'Impact',
        'culture_fit': 'Organizational Culture Fit',
        'culture_fit_legend': 'Legend: 1 = Poorly suited, 2 = Partially suited, 3 = Suited, 4 = Well suited, 5 = Highly suited',
        'culture_fit_score': 'Score',
        'score_breakdown': 'Score Breakdown',
        'global_score_100': 'Global Score',
        'criterion': 'Criterion',
        'weight_percent': 'Weight (%)',
        'technical_skills_label': 'Technical Skills',
        'soft_skills_label': 'Interpersonal Skills',
        'professional_experience_label': 'Professional Experience',
        'education_certifications_label': 'Education & Certifications',
        'culture_fit_label': 'Cultural Fit',
        'global_score_justification': 'Global Score Justification',
        'strengths_section': 'Strengths',
        'risks_gaps': 'Risks & Gaps',
        'hard_blocker_violations': 'Hard Blocker Violations',
        'suggested_questions': 'Suggested Interview Questions',
        'intro_pitch': 'Intro Pitch',
        'gap_strategies': 'Strategies to Address Gaps & Risks',
        'preparation_tips': 'Study Topics for Interview',
        'ai_recommendation': 'AI Recommendation',
        'enrichment_data': 'Enrichment Data (Brave Search)',
        'company_information': 'Company Information',
        'candidate_professional_profile': 'Candidate Professional Profile',
        'name': 'Name',
        'website': 'Website',
        'industry': 'Industry',
        'size': 'Size',
        'linkedin': 'LinkedIn',
        'github': 'GitHub',
        'portfolio': 'Portfolio',
        'generated': 'Generated',
        'report_prepared_for': 'Report prepared for',
        'company_id': 'Company ID',
        'report_id': 'Report ID',
        'report_code': 'Report Code',
        'detailed_analysis_and_evaluation': 'Detailed analysis and evaluation',
        'overview_job_posting': 'Overview of the job posting and key requirements',
        'weights_hard_blockers': 'Weights, hard blockers, and nice-to-have requirements',
        'ai_generated_summary': 'AI-generated summary and top candidate recommendation',
        'ranked_list_candidates': 'Ranked list of all {count} candidates',
    },
    'pt': {
        'title': 'Relatório de Análise de Candidatos',
        'table_of_contents': 'Índice',
        'job_position_details': 'Detalhes da Posição',
        'job_description': 'Descrição da Posição',
        'key_requirements': 'Requisitos Principais',
        'evaluation_criteria': 'Critérios de Avaliação',
        'category_weights': 'Pesos por Categoria',
        'hard_blockers': 'Bloqueadores Obrigatórios (Requisitos Essenciais)',
        'nice_to_have': 'Desejável (Preferencial)',
        'executive_recommendation': 'Recomendação Executiva',
        'recommended_candidate': 'Candidato Recomendado',
        'summary': 'Resumo',
        'key_insights': 'Insights Principais',
        'candidate_rankings': 'Classificação de Candidatos',
        'total': 'Total',
        'rank': 'Posição',
        'candidate': 'Candidato',
        'score': 'Pontuação',
        'blockers': 'Bloqueadores',
        'yes': 'Sim',
        'none': 'Nenhum',
        'detailed_analysis': 'Análise Detalhada de Candidatos',
        'global_score': 'Pontuação Global',
        'profile_summary': 'Resumo do Perfil',
        'category_scores': 'Pontuações por Categoria',
        'category': 'Categoria',
        'swot_analysis': 'Análise SWOT',
        'strengths': 'Forças',
        'weaknesses': 'Fraquezas',
        'opportunities': 'Oportunidades',
        'threats': 'Ameaças',
        'and_more': '... e mais {count}',
        'technical_skills': 'Avaliação de Competências Técnicas (Hard Skills)',
        'technical_skills_legend': 'Legenda: 1 = Básico, 2 = Intermediário, 3 = Avançado, 4 = Proficiente, 5 = Especialista',
        'competency': 'Competência',
        'justification': 'Justificação',
        'missing_technical_skills': 'Competências Técnicas em Falta',
        'soft_skills': 'Avaliação de Competências Interpessoais (Soft Skills)',
        'soft_skills_legend': 'Legenda: 1 = Pouco evidente, 2 = Parcialmente demonstrada, 3 = Adequadamente demonstrada, 4 = Bem demonstrada, 5 = Fortemente demonstrada',
        'missing_soft_skills': 'Competências Interpessoais em Falta',
        'professional_experience': 'Análise de Experiência Profissional',
        'relevance_to_position': 'Relevância para a Posição',
        'career_progression': 'Progressão de Carreira',
        'professional_stability': 'Estabilidade Profissional',
        'education_certifications': 'Formação Académica e Certificações',
        'relevance_adequacy': 'Relevância e Adequação',
        'evaluation': 'Avaliação',
        'certifications': 'Certificações',
        'notable_achievements': 'Realizações e Projetos Notáveis',
        'impact': 'Impacto',
        'culture_fit': 'Adequação à Cultura Organizacional',
        'culture_fit_legend': 'Legenda: 1 = Pouco adequado, 2 = Parcialmente adequado, 3 = Adequado, 4 = Bem adequado, 5 = Altamente adequado',
        'culture_fit_score': 'Pontuação',
        'score_breakdown': 'Decomposição da Pontuação',
        'global_score_100': 'Pontuação Global',
        'criterion': 'Critério',
        'weight_percent': 'Peso (%)',
        'technical_skills_label': 'Competências Técnicas',
        'soft_skills_label': 'Competências Interpessoais',
        'professional_experience_label': 'Experiência Profissional',
        'education_certifications_label': 'Formação e Certificações',
        'culture_fit_label': 'Adequação Cultural',
        'global_score_justification': 'Justificação da Pontuação Global',
        'strengths_section': 'Forças',
        'risks_gaps': 'Riscos e Lacunas',
        'hard_blocker_violations': 'Violações de Bloqueadores Obrigatórios',
        'suggested_questions': 'Questões Sugeridas para Entrevista',
        'intro_pitch': 'Apresentação Inicial',
        'gap_strategies': 'Estratégias para Abordar Lacunas e Riscos',
        'preparation_tips': 'Tópicos de Estudo para Entrevista',
        'ai_recommendation': 'Recomendação da IA',
        'enrichment_data': 'Dados de Enriquecimento (Brave Search)',
        'company_information': 'Informação da Empresa',
        'candidate_professional_profile': 'Perfil Profissional do Candidato',
        'name': 'Nome',
        'website': 'Website',
        'industry': 'Indústria',
        'size': 'Dimensão',
        'linkedin': 'LinkedIn',
        'github': 'GitHub',
        'portfolio': 'Portfólio',
        'generated': 'Gerado',
        'report_prepared_for': 'Relatório preparado para',
        'company_id': 'ID da Empresa',
        'report_id': 'ID do Relatório',
        'report_code': 'Código do Relatório',
        'detailed_analysis_and_evaluation': 'Análise detalhada e avaliação',
        'overview_job_posting': 'Visão geral da posição e requisitos principais',
        'weights_hard_blockers': 'Pesos, bloqueadores obrigatórios e requisitos desejáveis',
        'ai_generated_summary': 'Resumo gerado por IA e recomendação do melhor candidato',
        'ranked_list_candidates': 'Lista classificada de todos os {count} candidatos',
    },
    'fr': {
        'title': 'Rapport d\'Analyse des Candidats',
        'table_of_contents': 'Table des Matières',
        'job_position_details': 'Détails du Poste',
        'job_description': 'Description du Poste',
        'key_requirements': 'Exigences Principales',
        'evaluation_criteria': 'Critères d\'Évaluation',
        'category_weights': 'Pondérations par Catégorie',
        'hard_blockers': 'Bloqueurs Obligatoires (Exigences Essentielles)',
        'nice_to_have': 'Souhaitable (Préférentiel)',
        'executive_recommendation': 'Recommandation Exécutive',
        'recommended_candidate': 'Candidat Recommandé',
        'summary': 'Résumé',
        'key_insights': 'Insights Principaux',
        'candidate_rankings': 'Classement des Candidats',
        'total': 'Total',
        'rank': 'Rang',
        'candidate': 'Candidat',
        'score': 'Score',
        'blockers': 'Bloqueurs',
        'yes': 'Oui',
        'none': 'Aucun',
        'detailed_analysis': 'Analyse Détaillée des Candidats',
        'global_score': 'Score Global',
        'profile_summary': 'Résumé du Profil',
        'category_scores': 'Scores par Catégorie',
        'category': 'Catégorie',
        'swot_analysis': 'Analyse SWOT',
        'strengths': 'Forces',
        'weaknesses': 'Faiblesses',
        'opportunities': 'Opportunités',
        'threats': 'Menaces',
        'and_more': '... et {count} de plus',
        'technical_skills': 'Évaluation des Compétences Techniques (Hard Skills)',
        'technical_skills_legend': 'Légende: 1 = Basique, 2 = Intermédiaire, 3 = Avancé, 4 = Compétent, 5 = Expert',
        'competency': 'Compétence',
        'justification': 'Justification',
        'missing_technical_skills': 'Compétences Techniques Manquantes',
        'soft_skills': 'Évaluation des Compétences Interpersonnelles (Soft Skills)',
        'soft_skills_legend': 'Légende: 1 = Peu évident, 2 = Partiellement démontré, 3 = Adéquatement démontré, 4 = Bien démontré, 5 = Fortement démontré',
        'missing_soft_skills': 'Compétences Interpersonnelles Manquantes',
        'professional_experience': 'Analyse de l\'Expérience Professionnelle',
        'relevance_to_position': 'Pertinence pour le Poste',
        'career_progression': 'Progression de Carrière',
        'professional_stability': 'Stabilité Professionnelle',
        'education_certifications': 'Formation Académique et Certifications',
        'relevance_adequacy': 'Pertinence et Adéquation',
        'evaluation': 'Évaluation',
        'certifications': 'Certifications',
        'notable_achievements': 'Réalisations et Projets Notables',
        'impact': 'Impact',
        'culture_fit': 'Adéquation à la Culture Organisationnelle',
        'culture_fit_legend': 'Légende: 1 = Peu adapté, 2 = Partiellement adapté, 3 = Adapté, 4 = Bien adapté, 5 = Très adapté',
        'culture_fit_score': 'Score',
        'score_breakdown': 'Décomposition du Score',
        'global_score_100': 'Score Global',
        'criterion': 'Critère',
        'weight_percent': 'Poids (%)',
        'technical_skills_label': 'Compétences Techniques',
        'soft_skills_label': 'Compétences Interpersonnelles',
        'professional_experience_label': 'Expérience Professionnelle',
        'education_certifications_label': 'Formation et Certifications',
        'culture_fit_label': 'Adéquation Culturelle',
        'global_score_justification': 'Justification du Score Global',
        'strengths_section': 'Forces',
        'risks_gaps': 'Risques et Lacunes',
        'hard_blocker_violations': 'Violations des Bloqueurs Obligatoires',
        'suggested_questions': 'Questions Suggérées pour l\'Entretien',
        'intro_pitch': 'Présentation Initiale',
        'gap_strategies': 'Stratégies pour Aborder les Lacunes et Risques',
        'preparation_tips': 'Sujets d\'Étude pour l\'Entretien',
        'ai_recommendation': 'Recommandation de l\'IA',
        'enrichment_data': 'Données d\'Enrichissement (Brave Search)',
        'company_information': 'Informations sur l\'Entreprise',
        'candidate_professional_profile': 'Profil Professionnel du Candidat',
        'name': 'Nom',
        'website': 'Site Web',
        'industry': 'Industrie',
        'size': 'Taille',
        'linkedin': 'LinkedIn',
        'github': 'GitHub',
        'portfolio': 'Portfolio',
        'generated': 'Généré',
        'report_prepared_for': 'Rapport préparé pour',
        'company_id': 'ID de l\'Entreprise',
        'report_id': 'ID du Rapport',
        'report_code': 'Code du Rapport',
        'detailed_analysis_and_evaluation': 'Analyse détaillée et évaluation',
        'overview_job_posting': 'Vue d\'ensemble du poste et exigences principales',
        'weights_hard_blockers': 'Pondérations, bloqueurs obligatoires et exigences souhaitables',
        'ai_generated_summary': 'Résumé généré par IA et recommandation du meilleur candidat',
        'ranked_list_candidates': 'Liste classée de tous les {count} candidats',
    },
    'es': {
        'title': 'Informe de Análisis de Candidatos',
        'table_of_contents': 'Índice',
        'job_position_details': 'Detalles del Puesto',
        'job_description': 'Descripción del Puesto',
        'key_requirements': 'Requisitos Principales',
        'evaluation_criteria': 'Criterios de Evaluación',
        'category_weights': 'Ponderaciones por Categoría',
        'hard_blockers': 'Bloqueadores Obligatorios (Requisitos Esenciales)',
        'nice_to_have': 'Deseable (Preferencial)',
        'executive_recommendation': 'Recomendación Ejecutiva',
        'recommended_candidate': 'Candidato Recomendado',
        'summary': 'Resumen',
        'key_insights': 'Insights Principales',
        'candidate_rankings': 'Clasificación de Candidatos',
        'total': 'Total',
        'rank': 'Posición',
        'candidate': 'Candidato',
        'score': 'Puntuación',
        'blockers': 'Bloqueadores',
        'yes': 'Sí',
        'none': 'Ninguno',
        'detailed_analysis': 'Análisis Detallado de Candidatos',
        'global_score': 'Puntuación Global',
        'profile_summary': 'Resumen del Perfil',
        'category_scores': 'Puntuaciones por Categoría',
        'category': 'Categoría',
        'swot_analysis': 'Análisis SWOT',
        'strengths': 'Fortalezas',
        'weaknesses': 'Debilidades',
        'opportunities': 'Oportunidades',
        'threats': 'Amenazas',
        'and_more': '... y {count} más',
        'technical_skills': 'Evaluación de Competencias Técnicas (Hard Skills)',
        'technical_skills_legend': 'Leyenda: 1 = Básico, 2 = Intermedio, 3 = Avanzado, 4 = Competente, 5 = Experto',
        'competency': 'Competencia',
        'justification': 'Justificación',
        'missing_technical_skills': 'Competencias Técnicas Faltantes',
        'soft_skills': 'Evaluación de Competencias Interpersonales (Soft Skills)',
        'soft_skills_legend': 'Leyenda: 1 = Poco evidente, 2 = Parcialmente demostrado, 3 = Adecuadamente demostrado, 4 = Bien demostrado, 5 = Fuertemente demostrado',
        'missing_soft_skills': 'Competencias Interpersonales Faltantes',
        'professional_experience': 'Análisis de Experiencia Profesional',
        'relevance_to_position': 'Relevancia para el Puesto',
        'career_progression': 'Progresión de Carrera',
        'professional_stability': 'Estabilidad Profesional',
        'education_certifications': 'Formación Académica y Certificaciones',
        'relevance_adequacy': 'Relevancia y Adecuación',
        'evaluation': 'Evaluación',
        'certifications': 'Certificaciones',
        'notable_achievements': 'Logros y Proyectos Notables',
        'impact': 'Impacto',
        'culture_fit': 'Adecuación a la Cultura Organizacional',
        'culture_fit_legend': 'Leyenda: 1 = Poco adecuado, 2 = Parcialmente adecuado, 3 = Adecuado, 4 = Bien adecuado, 5 = Altamente adecuado',
        'culture_fit_score': 'Puntuación',
        'score_breakdown': 'Desglose de Puntuación',
        'global_score_100': 'Puntuación Global',
        'criterion': 'Criterio',
        'weight_percent': 'Peso (%)',
        'technical_skills_label': 'Competencias Técnicas',
        'soft_skills_label': 'Competencias Interpersonales',
        'professional_experience_label': 'Experiencia Profesional',
        'education_certifications_label': 'Formación y Certificaciones',
        'culture_fit_label': 'Adecuación Cultural',
        'global_score_justification': 'Justificación de la Puntuación Global',
        'strengths_section': 'Fortalezas',
        'risks_gaps': 'Riesgos y Brechas',
        'hard_blocker_violations': 'Violaciones de Bloqueadores Obligatorios',
        'suggested_questions': 'Preguntas Sugeridas para la Entrevista',
        'intro_pitch': 'Presentación Inicial',
        'gap_strategies': 'Estrategias para Abordar Brechas y Riesgos',
        'preparation_tips': 'Temas de Estudio para la Entrevista',
        'ai_recommendation': 'Recomendación de la IA',
        'enrichment_data': 'Datos de Enriquecimiento (Brave Search)',
        'company_information': 'Información de la Empresa',
        'candidate_professional_profile': 'Perfil Profesional del Candidato',
        'name': 'Nombre',
        'website': 'Sitio Web',
        'industry': 'Industria',
        'size': 'Tamaño',
        'linkedin': 'LinkedIn',
        'github': 'GitHub',
        'portfolio': 'Portafolio',
        'generated': 'Generado',
        'report_prepared_for': 'Informe preparado para',
        'company_id': 'ID de la Empresa',
        'report_id': 'ID del Informe',
        'report_code': 'Código del Informe',
        'detailed_analysis_and_evaluation': 'Análisis detallado y evaluación',
        'overview_job_posting': 'Resumen del puesto y requisitos principales',
        'weights_hard_blockers': 'Ponderaciones, bloqueadores obligatorios y requisitos deseables',
        'ai_generated_summary': 'Resumen generado por IA y recomendación del mejor candidato',
        'ranked_list_candidates': 'Lista clasificada de todos los {count} candidatos',
    }
}


class PDFReportGenerator:
    """Generate PDF reports for interviewer analysis results with ShortlistAI branding."""
    
    def __init__(self):
        try:
            self.styles = getSampleStyleSheet()
            self.branding = get_branding()
            self.branding.ensure_fonts_registered()
            self._setup_custom_styles()
            logger.info("PDFReportGenerator initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing PDFReportGenerator: {e}", exc_info=True)
            raise
    
    def _get_style(self, preferred_name: str, fallback_name: str):
        """Get style with fallback."""
        try:
            return self.styles[preferred_name]
        except KeyError:
            return self.styles[fallback_name]
    
    def _get_language(self, session_data: Dict[str, Any]) -> str:
        """Get language from session data, default to 'en'."""
        return session_data.get('data', {}).get('language', 'en')
    
    def _t(self, key: str, language: str, **kwargs) -> str:
        """Translate a key to the specified language."""
        translations = PDF_TRANSLATIONS.get(language, PDF_TRANSLATIONS['en'])
        text = translations.get(key, PDF_TRANSLATIONS['en'].get(key, key))
        # Format with kwargs if provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass
        return text
    
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
        
        # Body text justified with larger font
        self.styles.add(ParagraphStyle(
            name='BodyJustified',
            parent=self.styles['BodyText'],
            fontSize=12,  # Increased from 11
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
        
        # Table of Contents
        story.extend(self._build_table_of_contents(session_data, results, executive_recommendation))
        story.append(PageBreak())
        
        # Job description section
        story.extend(self._build_job_section(session_data))
        story.append(Spacer(1, 0.2*inch))
        
        # Evaluation criteria section
        story.extend(self._build_criteria_section(session_data))
        story.append(PageBreak())
        
        # Get language for all sections
        language = self._get_language(session_data)
        
        # Executive recommendation (if available)
        if executive_recommendation:
            story.extend(self._build_executive_recommendation(executive_recommendation, language))
            story.append(PageBreak())
        
        # Candidate rankings
        story.extend(self._build_rankings_section(results, language))
        story.append(PageBreak())
        
        # Detailed candidate profiles
        story.extend(self._build_candidate_details(results, language))
        
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
        language = self._get_language(session_data)
        elements.append(Spacer(1, 0.4*inch))
        elements.append(Paragraph(
            f'<font color="#0066FF"><b>{self._t("title", language)}</b></font>',
            self.styles['CustomTitle']
        ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Report Code (if available) - with branded style
        interviewer_data = session_data.get('data', {})
        report_code = interviewer_data.get('report_code')
        if report_code:
            elements.append(Paragraph(
                f'<font face="Courier-Bold" size="13" color="#7C3AED">{self._t("report_code", language)}: {report_code}</font>',
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
            f"<b>{self._t('generated', language)}:</b> {date_str}",
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
                f"<b>{self._t('report_prepared_for', language)}:</b>",
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 0.1*inch))
            
            # Company info (if available)
            company_id = interviewer_data.get('company_id')
            if company_id:
                elements.append(Paragraph(
                    f"{self._t('company_id', language)}: {company_id}",
                    self.styles['Normal']
                ))
            
            # Report ID
            report_id = interviewer_data.get('report_id')
            if report_id:
                elements.append(Paragraph(
                    f"{self._t('report_id', language)}: {report_id}",
                    ParagraphStyle(
                        name='ReportID',
                        parent=self.styles['Normal'],
                        fontSize=9,
                        textColor=colors.HexColor('#9ca3af')
                    )
                ))
        
        return elements
    
    def _build_table_of_contents(self, session_data: Dict[str, Any], results: List[Dict[str, Any]], executive_recommendation: Optional[Dict[str, Any]]) -> List:
        """Build professional table of contents."""
        elements = []
        language = self._get_language(session_data)
        
        # Title
        elements.append(Paragraph(
            self._t("table_of_contents", language),
            ParagraphStyle(
                name='TOCTitle',
                parent=self.styles['Title'],
                fontSize=24,
                textColor=colors.HexColor('#0066FF'),
                spaceAfter=0.3*inch,
                alignment=TA_CENTER
            )
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # TOC entries with better spacing
        toc_style = ParagraphStyle(
            name='TOCEntry',
            parent=self.styles['Normal'],
            fontSize=12,
            leftIndent=0.3*inch,
            spaceAfter=0.15*inch,
            textColor=colors.HexColor('#111827')
        )
        
        toc_items = [
            (f"1. {self._t('job_position_details', language)}", self._t('overview_job_posting', language)),
            (f"2. {self._t('evaluation_criteria', language)}", self._t('weights_hard_blockers', language)),
        ]
        
        if executive_recommendation:
            toc_items.append((f"3. {self._t('executive_recommendation', language)}", self._t('ai_generated_summary', language)))
            start_num = 4
        else:
            start_num = 3
        
        toc_items.append((f"{start_num}. {self._t('candidate_rankings', language)}", self._t('ranked_list_candidates', language, count=len(results))))
        
        # Detailed candidate profiles
        sorted_results = sorted(results, key=lambda x: x.get('global_score', 0), reverse=True)
        for idx, result in enumerate(sorted_results, 1):
            name = self._get_candidate_name(result, idx)
            toc_items.append((f"{start_num + idx}. {name}", self._t('detailed_analysis_and_evaluation', language)))
        
        # Build TOC with dots
        for title, description in toc_items:
            # Title with dots
            elements.append(Paragraph(
                f'<b>{title}</b>',
                toc_style
            ))
            # Description in lighter color
            desc_style = ParagraphStyle(
                name='TOCDesc',
                parent=toc_style,
                fontSize=10,
                leftIndent=0.5*inch,
                textColor=colors.HexColor('#6B7280'),
                spaceAfter=0.1*inch
            )
            elements.append(Paragraph(
                description,
                desc_style
            ))
        
        return elements
    
    def _build_job_section(self, session_data: Dict[str, Any]) -> List:
        """Build job description section."""
        elements = []
        data = session_data.get('data', {})
        language = self._get_language(session_data)
        
        elements.append(Paragraph(self._t("job_position_details", language), self.styles['SectionHeader']))
        
        # Job posting text - COMPLETE and FORMATTED
        job_text = data.get('job_posting_text', 'Not provided')
        elements.append(Paragraph(
            f"<b>{self._t('job_description', language)}:</b>",
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
                f"<b>{self._t('key_requirements', language)}:</b>",
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
        language = self._get_language(session_data)
        
        elements.append(Paragraph(self._t("evaluation_criteria", language), self.styles['SectionHeader']))
        
        # Weights table
        weights = data.get('weights', {})
        if weights:
            elements.append(Paragraph(
                f"<b>{self._t('category_weights', language)}:</b>",
                self.styles['SubSection']
            ))
            
            weight_data = [[self._t('category', language), self._t('weight_percent', language)]]
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
                f"<b>{self._t('hard_blockers', language)}:</b>",
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
                f"<b>{self._t('nice_to_have', language)}:</b>",
                self.styles['SubSection']
            ))
            for item in nice_to_have:
                elements.append(Paragraph(
                    f"• {item}",
                    self.styles['BodyText']
                ))
        
        return elements
    
    def _build_executive_recommendation(self, recommendation: Dict[str, Any], language: str) -> List:
        """Build executive recommendation section."""
        elements = []
        
        elements.append(Paragraph(
            f"📊 {self._t('executive_recommendation', language)}",
            self.styles['SectionHeader']
        ))
        
        # Top candidate highlight
        top_rec = recommendation.get('top_recommendation')
        if top_rec:
            elements.append(Paragraph(
                f"<b>✅ {self._t('recommended_candidate', language)}:</b> {top_rec.get('candidate_name', 'N/A')}",
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
                f"<b>{self._t('summary', language)}:</b>",
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
                f"<b>{self._t('key_insights', language)}:</b>",
                self.styles['SubSection']
            ))
            for insight in insights:
                elements.append(Paragraph(
                    f"• {insight}",
                    self.styles['BodyText']
                ))
        
        return elements
    
    def _build_rankings_section(self, results: List[Dict[str, Any]], language: str) -> List:
        """Build candidate rankings table."""
        elements = []
        
        elements.append(Paragraph(
            f"{self._t('candidate_rankings', language)} ({len(results)} {self._t('total', language)})",
            self.styles['SectionHeader']
        ))
        
        # SORT candidates by global_score DESCENDING
        sorted_results = sorted(
            results, 
            key=lambda x: x.get('global_score', 0), 
            reverse=True
        )
        
        # Prepare table data with better column widths
        table_data = [[self._t('rank', language), self._t('candidate', language), self._t('score', language), self._t('blockers', language)]]
        
        for idx, result in enumerate(sorted_results, 1):
            name = self._get_candidate_name(result, idx)
            score = result.get('global_score', 0)
            blockers = result.get('hard_blocker_flags', [])
            blocker_text = f"⚠️ {self._t('yes', language)}" if blockers else f"✓ {self._t('none', language)}"
            
            table_data.append([
                f"#{idx}",
                name,
                f"{score:.1f}/5",
                blocker_text
            ])
        
        # Create table with branded style and improved column widths
        table = Table(table_data, colWidths=[0.7*inch, 3.2*inch, 0.9*inch, 1.2*inch])
        table.setStyle(self.branding.create_branded_table_style(has_header=True))
        
        elements.append(table)
        
        return elements
    
    def _build_candidate_details(self, results: List[Dict[str, Any]], language: str) -> List:
        """Build detailed candidate profiles with all sections from step 7."""
        elements = []
        
        elements.append(Paragraph(
            self._t("detailed_analysis", language),
            self.styles['SectionHeader']
        ))
        
        # SORT candidates by global_score DESCENDING (same as rankings)
        sorted_results = sorted(
            results, 
            key=lambda x: x.get('global_score', 0), 
            reverse=True
        )
        
        for idx, result in enumerate(sorted_results, 1):
            # Start new page for each candidate (except first)
            if idx > 1:
                elements.append(PageBreak())
            
            candidate_elements = []
            
            name = self._get_candidate_name(result, idx)
            # Improved candidate header with better styling
            candidate_elements.append(Paragraph(
                f"#{idx}: {name}",
                ParagraphStyle(
                    name='CandidateHeader',
                    parent=self.styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#0066FF'),
                    spaceAfter=0.2*inch,
                    spaceBefore=0.1*inch
                )
            ))
            
            # Global Score with better styling
            score = result.get('global_score', 0)
            score_color = colors.HexColor('#10B981') if score >= 4 else colors.HexColor('#F59E0B') if score >= 3 else colors.HexColor('#EF4444')
            candidate_elements.append(Paragraph(
                f"<b>{self._t('global_score', language)}:</b> <font color='{score_color.hexval()}'><b>{score:.1f}/5</b></font>",
                ParagraphStyle(
                    name='ScoreDisplay',
                    parent=self.styles['BodyText'],
                    fontSize=14,
                    spaceAfter=0.15*inch
                )
            ))
            candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Profile Summary with KeepTogether to avoid cuts
            profile_summary = result.get('profile_summary')
            if profile_summary:
                summary_section = [
                    Paragraph(
                        f"<b>📋 {self._t('profile_summary', language)}</b>",
                        ParagraphStyle(
                            name='SectionTitle',
                            parent=self.styles['Heading2'],
                            fontSize=14,
                            textColor=colors.HexColor('#111827'),
                            spaceAfter=0.1*inch
                        )
                    ),
                    Paragraph(
                        profile_summary,
                        ParagraphStyle(
                            name='SummaryText',
                            parent=self.styles['BodyJustified'],
                            fontSize=11,
                            spaceAfter=0.2*inch,
                            leading=14
                        )
                    )
                ]
                candidate_elements.append(KeepTogether(summary_section))
            
            # Categories table
            categories = result.get('categories', {})
            if categories:
                candidate_elements.append(Paragraph(
                    f"<b>{self._t('category_scores', language)}:</b>",
                    self.styles['SubSection']
                ))
                cat_data = [[self._t('category', language), self._t('score', language)]]
                for cat, score in categories.items():
                    cat_data.append([
                        cat.replace('_', ' ').title(),
                        f"{score}/5"
                    ])
                
                cat_table = Table(cat_data, colWidths=[2.5*inch, inch])
                cat_table.setStyle(self.branding.create_branded_table_style(has_header=True))
                candidate_elements.append(cat_table)
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # SWOT Analysis
            swot = result.get('swot_analysis', {})
            if swot:
                candidate_elements.append(Paragraph(
                    f"<b>📊 {self._t('swot_analysis', language)}</b>",
                    self.styles['SubSection']
                ))
                
                # Create SWOT table
                swot_data = [
                    [self._t('strengths', language), self._t('weaknesses', language)],
                    [self._t('opportunities', language), self._t('threats', language)]
                ]
                
                # Fill strengths
                strengths = swot.get('strengths', [])
                strengths_text = '\n'.join([f"• {s}" for s in strengths[:5]])  # Limit to 5 for table
                if len(strengths) > 5:
                    strengths_text += f"\n{self._t('and_more', language, count=len(strengths) - 5)}"
                
                # Fill weaknesses
                weaknesses = swot.get('weaknesses', [])
                weaknesses_text = '\n'.join([f"• {w}" for w in weaknesses[:5]])
                if len(weaknesses) > 5:
                    weaknesses_text += f"\n{self._t('and_more', language, count=len(weaknesses) - 5)}"
                
                # Fill opportunities
                opportunities = swot.get('opportunities', [])
                opp_text = '\n'.join([f"• {o}" for o in opportunities[:5]])
                if len(opportunities) > 5:
                    opp_text += f"\n{self._t('and_more', language, count=len(opportunities) - 5)}"
                
                # Fill threats
                threats = swot.get('threats', [])
                threats_text = '\n'.join([f"• {t}" for t in threats[:5]])
                if len(threats) > 5:
                    threats_text += f"\n{self._t('and_more', language, count=len(threats) - 5)}"
                
                swot_table = Table([
                    [
                        Paragraph(strengths_text, ParagraphStyle(
                            name='SWOTCell',
                            parent=self.styles['BodyText'],
                            fontSize=9,
                            leftIndent=0
                        )),
                        Paragraph(weaknesses_text, ParagraphStyle(
                            name='SWOTCell',
                            parent=self.styles['BodyText'],
                            fontSize=9,
                            leftIndent=0
                        ))
                    ],
                    [
                        Paragraph(opp_text, ParagraphStyle(
                            name='SWOTCell',
                            parent=self.styles['BodyText'],
                            fontSize=9,
                            leftIndent=0
                        )),
                        Paragraph(threats_text, ParagraphStyle(
                            name='SWOTCell',
                            parent=self.styles['BodyText'],
                            fontSize=9,
                            leftIndent=0
                        ))
                    ]
                ], colWidths=[3*inch, 3*inch], rowHeights=[2*inch, 2*inch])
                
                swot_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#16a34a')),  # Green for strengths
                    ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                    ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#dc2626')),  # Red for weaknesses
                    ('TEXTCOLOR', (1, 0), (1, 0), colors.white),
                    ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#3b82f6')),  # Blue for opportunities
                    ('TEXTCOLOR', (0, 1), (0, 1), colors.white),
                    ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#f59e0b')),  # Orange for threats
                    ('TEXTCOLOR', (1, 1), (1, 1), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
                    ('BOX', (0, 0), (-1, -1), 1, colors.white),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                
                candidate_elements.append(swot_table)
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Technical Skills Detailed
            tech_skills = result.get('technical_skills_detailed', [])
            if tech_skills:
                candidate_elements.append(Paragraph(
                    f"<b>🔧 {self._t('technical_skills', language)}</b>",
                    self.styles['SubSection']
                ))
                candidate_elements.append(Paragraph(
                    self._t('technical_skills_legend', language),
                    ParagraphStyle(
                        name='Legend',
                        parent=self.styles['BodyText'],
                        fontSize=9,
                        textColor=colors.HexColor('#6b7280'),
                        spaceAfter=6
                    )
                ))
                
                tech_data = [[self._t('competency', language), self._t('score', language), self._t('justification', language)]]
                for skill in tech_skills:
                    justification = skill.get('justification', '')
                    # Truncate justification but allow wrapping
                    justification_short = justification[:250] + ('...' if len(justification) > 250 else '')
                    tech_data.append([
                        skill.get('skill', ''),
                        f"{skill.get('score', 0)}/5",
                        justification_short
                    ])
                
                # Improved table widths for better formatting
                tech_table = Table(tech_data, colWidths=[1.8*inch, 0.9*inch, 3.3*inch])
                tech_table.setStyle(self.branding.create_branded_table_style(has_header=True))
                candidate_elements.append(tech_table)
                
                # Missing critical technical skills
                missing_tech = result.get('missing_critical_technical_skills', [])
                if missing_tech:
                    candidate_elements.append(Spacer(1, 0.1*inch))
                    candidate_elements.append(Paragraph(
                        f"<b>⚠️ {self._t('missing_technical_skills', language)}:</b>",
                        ParagraphStyle(
                            name='Warning',
                            parent=self.styles['BodyText'],
                            textColor=colors.HexColor('#f59e0b'),
                            spaceAfter=4
                        )
                    ))
                    for skill in missing_tech:
                        candidate_elements.append(Paragraph(
                            f"• {skill}",
                            ParagraphStyle(
                                name='MissingSkill',
                                parent=self.styles['BodyText'],
                                leftIndent=15,
                                fontSize=10
                            )
                        ))
                
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Soft Skills Detailed
            soft_skills = result.get('soft_skills_detailed', [])
            if soft_skills:
                candidate_elements.append(Paragraph(
                    f"<b>🤝 {self._t('soft_skills', language)}</b>",
                    self.styles['SubSection']
                ))
                candidate_elements.append(Paragraph(
                    self._t('soft_skills_legend', language),
                    ParagraphStyle(
                        name='Legend',
                        parent=self.styles['BodyText'],
                        fontSize=9,
                        textColor=colors.HexColor('#6b7280'),
                        spaceAfter=6
                    )
                ))
                
                soft_data = [[self._t('competency', language), self._t('score', language), self._t('justification', language)]]
                for skill in soft_skills:
                    justification = skill.get('justification', '')
                    # Truncate justification but allow wrapping
                    justification_short = justification[:250] + ('...' if len(justification) > 250 else '')
                    soft_data.append([
                        skill.get('skill', ''),
                        f"{skill.get('score', 0)}/5",
                        justification_short
                    ])
                
                # Improved table widths for better formatting
                soft_table = Table(soft_data, colWidths=[1.8*inch, 0.9*inch, 3.3*inch])
                soft_table.setStyle(self.branding.create_branded_table_style(has_header=True))
                candidate_elements.append(soft_table)
                
                # Missing important soft skills
                missing_soft = result.get('missing_important_soft_skills', [])
                if missing_soft:
                    candidate_elements.append(Spacer(1, 0.1*inch))
                    candidate_elements.append(Paragraph(
                        f"<b>⚠️ {self._t('missing_soft_skills', language)}:</b>",
                        ParagraphStyle(
                            name='Warning',
                            parent=self.styles['BodyText'],
                            textColor=colors.HexColor('#f59e0b'),
                            spaceAfter=4
                        )
                    ))
                    for skill in missing_soft:
                        candidate_elements.append(Paragraph(
                            f"• {skill}",
                            ParagraphStyle(
                                name='MissingSkill',
                                parent=self.styles['BodyText'],
                                leftIndent=15,
                                fontSize=10
                            )
                        ))
                
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Professional Experience Analysis
            exp_analysis = result.get('professional_experience_analysis', {})
            if exp_analysis:
                candidate_elements.append(Paragraph(
                    f"<b>💼 {self._t('professional_experience', language)}</b>",
                    self.styles['SubSection']
                ))
                
                if exp_analysis.get('relevance_to_position'):
                    candidate_elements.append(Paragraph(
                        f"<b>{self._t('relevance_to_position', language)}:</b>",
                        self.styles['BodyText']
                    ))
                    candidate_elements.append(Paragraph(
                        exp_analysis['relevance_to_position'],
                        self.styles['BodyJustified']
                    ))
                    candidate_elements.append(Spacer(1, 0.1*inch))
                
                if exp_analysis.get('career_progression'):
                    candidate_elements.append(Paragraph(
                        f"<b>{self._t('career_progression', language)}:</b>",
                        self.styles['BodyText']
                    ))
                    candidate_elements.append(Paragraph(
                        exp_analysis['career_progression'],
                        self.styles['BodyJustified']
                    ))
                    candidate_elements.append(Spacer(1, 0.1*inch))
                
                if exp_analysis.get('professional_stability'):
                    candidate_elements.append(Paragraph(
                        f"<b>{self._t('professional_stability', language)}:</b>",
                        self.styles['BodyText']
                    ))
                    candidate_elements.append(Paragraph(
                        exp_analysis['professional_stability'],
                        self.styles['BodyJustified']
                    ))
                
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Education and Certifications
            education = result.get('education_and_certifications', {})
            if education:
                candidate_elements.append(Paragraph(
                    f"<b>🎓 {self._t('education_certifications', language)}</b>",
                    self.styles['SubSection']
                ))
                
                if education.get('relevance'):
                    candidate_elements.append(Paragraph(
                        f"<b>{self._t('relevance_adequacy', language)}:</b>",
                        self.styles['BodyText']
                    ))
                    candidate_elements.append(Paragraph(
                        education['relevance'],
                        self.styles['BodyJustified']
                    ))
                    candidate_elements.append(Spacer(1, 0.1*inch))
                
                if education.get('adequacy'):
                    candidate_elements.append(Paragraph(
                        f"<b>{self._t('evaluation', language)}:</b>",
                        self.styles['BodyText']
                    ))
                    candidate_elements.append(Paragraph(
                        education['adequacy'],
                        self.styles['BodyJustified']
                    ))
                    candidate_elements.append(Spacer(1, 0.1*inch))
                
                certs = education.get('certifications', [])
                if certs:
                    candidate_elements.append(Paragraph(
                        f"<b>{self._t('certifications', language)}:</b>",
                        self.styles['BodyText']
                    ))
                    for cert in certs:
                        candidate_elements.append(Paragraph(
                            f"• {cert}",
                            ParagraphStyle(
                                name='Cert',
                                parent=self.styles['BodyText'],
                                leftIndent=15,
                                fontSize=10
                            )
                        ))
                
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Notable Achievements
            achievements = result.get('notable_achievements', [])
            if achievements:
                candidate_elements.append(Paragraph(
                    f"<b>🏆 {self._t('notable_achievements', language)}</b>",
                    self.styles['SubSection']
                ))
                for achievement in achievements:
                    candidate_elements.append(Paragraph(
                        f"<b>{achievement.get('achievement', '')}</b>",
                        self.styles['BodyText']
                    ))
                    candidate_elements.append(Paragraph(
                        f"<i>{self._t('impact', language)}:</i> {achievement.get('impact', '')}",
                        ParagraphStyle(
                            name='AchievementImpact',
                            parent=self.styles['BodyText'],
                            leftIndent=15,
                            fontSize=10,
                            spaceAfter=8
                        )
                    ))
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Culture Fit Assessment
            culture_fit = result.get('culture_fit_assessment', {})
            if culture_fit:
                candidate_elements.append(Paragraph(
                    f"<b>🌐 {self._t('culture_fit', language)}</b>",
                    self.styles['SubSection']
                ))
                candidate_elements.append(Paragraph(
                    self._t('culture_fit_legend', language),
                    ParagraphStyle(
                        name='Legend',
                        parent=self.styles['BodyText'],
                        fontSize=9,
                        textColor=colors.HexColor('#6b7280'),
                        spaceAfter=6
                    )
                ))
                
                culture_score = culture_fit.get('score', 0)
                candidate_elements.append(Paragraph(
                    f"<b>{self._t('culture_fit_score', language)}:</b> {culture_score}/5",
                    ParagraphStyle(
                        name='CultureScore',
                        parent=self.styles['BodyText'],
                        fontSize=14,
                        textColor=colors.HexColor('#0066FF'),
                        spaceAfter=8
                    )
                ))
                
                if culture_fit.get('justification'):
                    candidate_elements.append(Paragraph(
                        culture_fit['justification'],
                        self.styles['BodyJustified']
                    ))
                
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Score Breakdown
            score_breakdown = result.get('score_breakdown', {})
            if score_breakdown:
                candidate_elements.append(Paragraph(
                    f"<b>📊 {self._t('score_breakdown', language)}</b>",
                    self.styles['SubSection']
                ))
                
                global_score = score_breakdown.get('global_score')
                if global_score is not None:
                    candidate_elements.append(Paragraph(
                        f"<b>{self._t('global_score_100', language)}: {global_score}/100</b>",
                        ParagraphStyle(
                            name='GlobalScore',
                            parent=self.styles['BodyText'],
                            fontSize=16,
                            textColor=colors.HexColor('#0066FF'),
                            alignment=TA_CENTER,
                            spaceAfter=12,
                            backColor=colors.HexColor('#EFF6FF'),
                            borderPadding=8
                        )
                    ))
                
                # Score breakdown table
                breakdown_data = [[self._t('criterion', language), self._t('weight_percent', language), self._t('score', language)]]
                
                if score_breakdown.get('technical_skills'):
                    ts = score_breakdown['technical_skills']
                    breakdown_data.append([
                        self._t('technical_skills_label', language),
                        f"{ts.get('weight_percent', 0)}%",
                        f"{ts.get('score', 0)}/100"
                    ])
                
                if score_breakdown.get('soft_skills'):
                    ss = score_breakdown['soft_skills']
                    breakdown_data.append([
                        self._t('soft_skills_label', language),
                        f"{ss.get('weight_percent', 0)}%",
                        f"{ss.get('score', 0)}/100"
                    ])
                
                if score_breakdown.get('professional_experience'):
                    pe = score_breakdown['professional_experience']
                    breakdown_data.append([
                        self._t('professional_experience_label', language),
                        f"{pe.get('weight_percent', 0)}%",
                        f"{pe.get('score', 0)}/100"
                    ])
                
                if score_breakdown.get('education_certifications'):
                    ec = score_breakdown['education_certifications']
                    breakdown_data.append([
                        self._t('education_certifications_label', language),
                        f"{ec.get('weight_percent', 0)}%",
                        f"{ec.get('score', 0)}/100"
                    ])
                
                if score_breakdown.get('culture_fit'):
                    cf = score_breakdown['culture_fit']
                    breakdown_data.append([
                        self._t('culture_fit_label', language),
                        f"{cf.get('weight_percent', 0)}%",
                        f"{cf.get('score', 0)}/100"
                    ])
                
                if len(breakdown_data) > 1:  # Has data beyond header
                    # Improved table widths
                    breakdown_table = Table(breakdown_data, colWidths=[2.8*inch, 1.1*inch, 1.1*inch])
                    breakdown_table.setStyle(self.branding.create_branded_table_style(has_header=True))
                    candidate_elements.append(breakdown_table)
                
                # Global score justification
                if score_breakdown.get('global_score_justification'):
                    candidate_elements.append(Spacer(1, 0.1*inch))
                    candidate_elements.append(Paragraph(
                        f"<b>{self._t('global_score_justification', language)}:</b>",
                        self.styles['BodyText']
                    ))
                    candidate_elements.append(Paragraph(
                        score_breakdown['global_score_justification'],
                        self.styles['BodyJustified']
                    ))
                
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Strengths
            strengths = result.get('strengths', [])
            if strengths:
                candidate_elements.append(Paragraph(
                    f"<b>✓ {self._t('strengths_section', language)}:</b>",
                    self.styles['SubSection']
                ))
                for strength in strengths:
                    candidate_elements.append(Paragraph(
                        f"• {strength}",
                        ParagraphStyle(
                            name='Strength',
                            parent=self.styles['BodyText'],
                            leftIndent=15,
                            fontSize=10
                        )
                    ))
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Risks
            risks = result.get('risks', [])
            if risks:
                candidate_elements.append(Paragraph(
                    f"<b>⚠️ {self._t('risks_gaps', language)}:</b>",
                    self.styles['SubSection']
                ))
                for risk in risks:
                    candidate_elements.append(Paragraph(
                        f"• {risk}",
                        ParagraphStyle(
                            name='Risk',
                            parent=self.styles['BodyText'],
                            leftIndent=15,
                            textColor=colors.HexColor('#d97706'),
                            fontSize=10
                        )
                    ))
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Hard blocker violations (if any)
            blocker_flags = result.get('hard_blocker_flags', [])
            if blocker_flags:
                candidate_elements.append(Paragraph(
                    f"<b>🔴 {self._t('hard_blocker_violations', language)}:</b>",
                    self.styles['SubSection']
                ))
                for blocker in blocker_flags:
                    candidate_elements.append(Paragraph(
                        f"⚠️ {blocker}",
                        ParagraphStyle(
                            name='Blocker',
                            parent=self.styles['BodyText'],
                            leftIndent=15,
                            textColor=colors.HexColor('#dc2626'),
                            fontName='Helvetica-Bold',
                            fontSize=10
                        )
                    ))
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Interview questions (ALL questions)
            questions = result.get('questions', [])
            if questions:
                candidate_elements.append(Paragraph(
                    f"<b>❓ {self._t('suggested_questions', language)} ({len(questions)} {self._t('total', language).lower()}):</b>",
                    self.styles['SubSection']
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
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Intro Pitch
            intro_pitch = result.get('intro_pitch', '')
            if intro_pitch:
                candidate_elements.append(Paragraph(
                    f"<b>🎤 {self._t('intro_pitch', language)}:</b>",
                    self.styles['SubSection']
                ))
                candidate_elements.append(Paragraph(
                    intro_pitch,
                    ParagraphStyle(
                        name='IntroPitch',
                        parent=self.styles['BodyText'],
                        leftIndent=15,
                        fontSize=10,
                        spaceAfter=4,
                        textColor=colors.HexColor('#3b82f6')
                    )
                ))
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Gap Strategies
            gap_strategies = self._normalize_list_field(result.get('gap_strategies', []))
            if gap_strategies:
                candidate_elements.append(Paragraph(
                    f"<b>💡 {self._t('gap_strategies', language)}:</b>",
                    self.styles['SubSection']
                ))
                for strategy in gap_strategies:
                    candidate_elements.append(Paragraph(
                        f"• {strategy}",
                        ParagraphStyle(
                            name='GapStrategy',
                            parent=self.styles['BodyText'],
                            leftIndent=15,
                            fontSize=10,
                            spaceAfter=4
                        )
                    ))
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Preparation Tips
            preparation_tips = self._normalize_list_field(result.get('preparation_tips', []))
            if preparation_tips:
                candidate_elements.append(Paragraph(
                    f"<b>📚 {self._t('preparation_tips', language)}:</b>",
                    self.styles['SubSection']
                ))
                for tip in preparation_tips:
                    candidate_elements.append(Paragraph(
                        f"• {tip}",
                        ParagraphStyle(
                            name='PrepTip',
                            parent=self.styles['BodyText'],
                            leftIndent=15,
                            fontSize=10,
                            spaceAfter=4
                        )
                    ))
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # AI Recommendation
            recommendation = result.get('recommendation', '')
            if recommendation:
                candidate_elements.append(Paragraph(
                    f"<b>💡 {self._t('ai_recommendation', language)}:</b>",
                    self.styles['SubSection']
                ))
                candidate_elements.append(Paragraph(
                    recommendation,
                    ParagraphStyle(
                        name='Recommendation',
                        parent=self.styles['BodyText'],
                        leftIndent=15,
                        fontSize=10,
                        spaceAfter=4,
                        textColor=colors.HexColor('#059669')
                    )
                ))
                candidate_elements.append(Spacer(1, 0.15*inch))
            
            # Enrichment Data
            enrichment = result.get('enrichment', {})
            if enrichment and (enrichment.get('company') or enrichment.get('candidate')):
                candidate_elements.append(Paragraph(
                    f"<b>🔍 {self._t('enrichment_data', language)}:</b>",
                    self.styles['SubSection']
                ))
                
                # Company enrichment
                if enrichment.get('company'):
                    company = enrichment['company']
                    candidate_elements.append(Paragraph(
                        f"<b>{self._t('company_information', language)}:</b>",
                        ParagraphStyle(
                            name='EnrichmentSubHeader',
                            parent=self.styles['BodyText'],
                            leftIndent=15,
                            fontSize=10,
                            spaceAfter=4
                        )
                    ))
                    if company.get('name'):
                        candidate_elements.append(Paragraph(
                            f"• {self._t('name', language)}: {company['name']}",
                            ParagraphStyle(name='EnrichmentDetail', parent=self.styles['BodyText'], leftIndent=30, fontSize=9, spaceAfter=2)
                        ))
                    if company.get('website'):
                        candidate_elements.append(Paragraph(
                            f"• {self._t('website', language)}: {company['website']}",
                            ParagraphStyle(name='EnrichmentDetail', parent=self.styles['BodyText'], leftIndent=30, fontSize=9, spaceAfter=2)
                        ))
                    if company.get('industry'):
                        candidate_elements.append(Paragraph(
                            f"• {self._t('industry', language)}: {company['industry']}",
                            ParagraphStyle(name='EnrichmentDetail', parent=self.styles['BodyText'], leftIndent=30, fontSize=9, spaceAfter=2)
                        ))
                    if company.get('size'):
                        candidate_elements.append(Paragraph(
                            f"• {self._t('size', language)}: {company['size']}",
                            ParagraphStyle(name='EnrichmentDetail', parent=self.styles['BodyText'], leftIndent=30, fontSize=9, spaceAfter=2)
                        ))
                
                # Candidate enrichment
                if enrichment.get('candidate'):
                    cand = enrichment['candidate']
                    candidate_elements.append(Paragraph(
                        f"<b>{self._t('candidate_professional_profile', language)}:</b>",
                        ParagraphStyle(
                            name='EnrichmentSubHeader',
                            parent=self.styles['BodyText'],
                            leftIndent=15,
                            fontSize=10,
                            spaceAfter=4
                        )
                    ))
                    if cand.get('linkedin_profile'):
                        candidate_elements.append(Paragraph(
                            f"• {self._t('linkedin', language)}: {cand['linkedin_profile']}",
                            ParagraphStyle(name='EnrichmentDetail', parent=self.styles['BodyText'], leftIndent=30, fontSize=9, spaceAfter=2)
                        ))
                    if cand.get('github_profile'):
                        candidate_elements.append(Paragraph(
                            f"• {self._t('github', language)}: {cand['github_profile']}",
                            ParagraphStyle(name='EnrichmentDetail', parent=self.styles['BodyText'], leftIndent=30, fontSize=9, spaceAfter=2)
                        ))
                    if cand.get('portfolio_url'):
                        candidate_elements.append(Paragraph(
                            f"• {self._t('portfolio', language)}: {cand['portfolio_url']}",
                            ParagraphStyle(name='EnrichmentDetail', parent=self.styles['BodyText'], leftIndent=30, fontSize=9, spaceAfter=2)
                        ))
            
            # Add all candidate elements
            elements.extend(candidate_elements)
        
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

