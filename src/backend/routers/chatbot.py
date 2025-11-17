"""
API router for Chatbot CV Preparation endpoints.

Handles conversational chatbot flow for CV preparation:
- Welcome and consent
- Profile collection
- CV upload and analysis
- Job opportunity analysis
- Digital footprint analysis
- Adaptive questions
- CV generation (ATS and human friendly)
- Interview preparation
- Employability scoring
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
import logging

from models.chatbot import (
    ChatbotWelcomeRequest,
    ChatbotWelcomeResponse,
    ChatbotMessageRequest,
    ChatbotBotMessageResponse,
    ChatbotProfileDataRequest,
    ChatbotCVUploadRequest,
    ChatbotJobOpportunityRequest,
    ChatbotAnswerQuestionRequest,
    ChatbotCVRegenerationRequest,
    ChatbotCVPreviewResponse,
    ChatbotInterviewPrepResponse,
    ChatbotEmployabilityScoreResponse,
    ChatbotJobRiskAssessmentResponse,
    ChatbotDigitalFootprintResponse,
    ChatbotCompletionResponse,
)

from services.chatbot_service import get_chatbot_service
from services.database.chatbot_service import get_chatbot_database_service
from services.database.candidate_service import get_candidate_service
from utils.file_processor import FileProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chatbot", tags=["chatbot"])


# =============================================================================
# Helper Functions
# =============================================================================

def _generate_cv_extraction_summary(
    structured_data: Optional[Dict[str, Any]],
    profile_data: Dict[str, Any],
    language: str,
    session_id: Optional[str] = None
) -> str:
    """
    Generate formatted summary message showing ALL extracted CV data with complete details.
    Also detects missing required data and asks for it intelligently.
    
    Required fields:
    - name (obrigatório)
    - email (obrigatório para recuperação de sessão)
    
    Recommended fields:
    - phone
    - location
    - work_experience (pelo menos 1)
    - skills
    """
    from typing import Dict, Any
    
    if not structured_data:
        messages = {
            "en": "I've received your CV, but I had difficulty extracting structured information. Please review the data below and let me know if anything needs to be corrected or added.",
            "pt": "Recebi o seu CV, mas tive dificuldade em extrair informações estruturadas. Por favor, revise os dados abaixo e diga-me se algo precisa ser corrigido ou adicionado.",
            "fr": "J'ai reçu votre CV, mais j'ai eu des difficultés à extraire des informations structurées. Veuillez examiner les données ci-dessous et me dire si quelque chose doit être corrigé ou ajouté.",
            "es": "He recibido tu CV, pero tuve dificultades para extrair información estructurada. Por favor, revisa los datos a continuación y dime si algo necesita ser corregido o agregado."
        }
        return messages.get(language, messages["en"])
    
    # Build summary with extracted information - show ALL details
    summary_parts = []
    
    intro_messages = {
        "en": "Perfect! I've analyzed your CV and extracted the following information:\n\n",
        "pt": "Perfeito! Analisei o seu CV e extraí as seguintes informações:\n\n",
        "fr": "Parfait ! J'ai analysé votre CV et extrait les informations suivantes :\n\n",
        "es": "¡Perfecto! He analizado tu CV y extraído la siguiente información:\n\n"
    }
    summary_parts.append(intro_messages.get(language, intro_messages["en"]))
    
    # Personal Information - check both structured_data and profile_data
    personal_info = []
    
    # Name - check multiple possible fields
    name = (
        structured_data.get("name") or 
        structured_data.get("full_name") or 
        profile_data.get("name") or
        (structured_data.get("personal_info", {}).get("name") if isinstance(structured_data.get("personal_info"), dict) else None)
    )
    if name:
        label_map = {"en": "**Name:**", "pt": "**Nome:**", "fr": "**Nom :**", "es": "**Nombre:**"}
        personal_info.append(f"{label_map.get(language, '**Name:**')} {name}")
    
    # Email - check multiple sources
    email = (
        profile_data.get("email") or
        structured_data.get("email") or
        (structured_data.get("personal_info", {}).get("email") if isinstance(structured_data.get("personal_info"), dict) else None)
    )
    if email:
        personal_info.append(f"**Email:** {email}")
    
    # Phone - check multiple sources
    phone = (
        profile_data.get("phone") or
        structured_data.get("phone") or
        structured_data.get("phone_number") or
        (structured_data.get("personal_info", {}).get("phone") if isinstance(structured_data.get("personal_info"), dict) else None)
    )
    if phone:
        label_map = {"en": "**Phone:**", "pt": "**Telefone:**", "fr": "**Téléphone :**", "es": "**Teléfono:**"}
        personal_info.append(f"{label_map.get(language, '**Phone:**')} {phone}")
    
    # Location - check multiple sources
    location = (
        profile_data.get("location") or
        structured_data.get("location") or
        structured_data.get("address") or
        (structured_data.get("personal_info", {}).get("location") if isinstance(structured_data.get("personal_info"), dict) else None)
    )
    if location:
        label_map = {"en": "**Location:**", "pt": "**Localização:**", "fr": "**Localisation :**", "es": "**Ubicación:**"}
        personal_info.append(f"{label_map.get(language, '**Location:**')} {location}")
    
    if personal_info:
        label_messages = {
            "en": "**Personal Information:**\n",
            "pt": "**Informações Pessoais:**\n",
            "fr": "**Informations personnelles :**\n",
            "es": "**Información Personal:**\n"
        }
        summary_parts.append(label_messages.get(language, label_messages["en"]))
        summary_parts.append("\n".join(f"- {info}" for info in personal_info))
        summary_parts.append("\n\n")
    
    # Professional Summary
    summary_text = (
        structured_data.get("summary") or 
        structured_data.get("professional_summary") or
        structured_data.get("objective")
    )
    if summary_text:
        label_messages = {
            "en": "**Professional Summary:**\n",
            "pt": "**Resumo Profissional:**\n",
            "fr": "**Résumé professionnel :**\n",
            "es": "**Resumen Profesional:**\n"
        }
        summary_parts.append(label_messages.get(language, label_messages["en"]))
        # Limit summary to first 500 characters for display
        summary_display = summary_text[:500] + ("..." if len(summary_text) > 500 else "")
        summary_parts.append(f"{summary_display}\n\n")
    
    # Social Media Links
    links = profile_data.get("links", {})
    # Also check structured_data for links
    if not links:
        links = structured_data.get("links", {}) or {}
        # Check personal_info for links
        if isinstance(structured_data.get("personal_info"), dict):
            links = links or structured_data["personal_info"].get("links", {})
    
    if links:
        links_list = []
        if links.get("linkedin"):
            links_list.append(f"**LinkedIn:** {links['linkedin']}")
        if links.get("github"):
            links_list.append(f"**GitHub:** {links['github']}")
        if links.get("portfolio") or links.get("website"):
            portfolio_url = links.get("portfolio") or links.get("website")
            links_list.append(f"**Portfolio/Website:** {portfolio_url}")
        
        if links_list:
            label_messages = {
                "en": "**Social Media Links:**\n",
                "pt": "**Links de Redes Sociais:**\n",
                "fr": "**Liens de réseaux sociaux :**\n",
                "es": "**Enlaces de Redes Sociales:**\n"
            }
            summary_parts.append(label_messages.get(language, label_messages["en"]))
            summary_parts.append("\n".join(f"- {link}" for link in links_list))
            summary_parts.append("\n\n")
    
    # Detect missing personal links (LinkedIn, GitHub, Portfolio)
    missing_personal_links = []
    if not links.get("linkedin"):
        missing_personal_links.append({
            "field": "linkedin",
            "label": {"en": "LinkedIn profile", "pt": "Perfil LinkedIn", "fr": "Profil LinkedIn", "es": "Perfil de LinkedIn"}.get(language, "LinkedIn profile")
        })
    if not links.get("github"):
        missing_personal_links.append({
            "field": "github",
            "label": {"en": "GitHub profile", "pt": "Perfil GitHub", "fr": "Profil GitHub", "es": "Perfil de GitHub"}.get(language, "GitHub profile")
        })
    if not links.get("portfolio") and not links.get("website"):
        missing_personal_links.append({
            "field": "portfolio",
            "label": {"en": "Portfolio/Website", "pt": "Portfólio/Website", "fr": "Portfolio/Site web", "es": "Portafolio/Sitio web"}.get(language, "Portfolio/Website")
        })
    
    if missing_personal_links:
        summary_parts.append("\n")
        personal_links_label = {
            "en": "**Personal Links Missing:**\n",
            "pt": "**Links Pessoais em Falta:**\n",
            "fr": "**Liens Personnels Manquants :**\n",
            "es": "**Enlaces Personales Faltantes:**\n"
        }
        summary_parts.append(personal_links_label.get(language, personal_links_label["en"]))
        
        personal_links_help = {
            "en": "To help me better understand your professional profile and provide more accurate recommendations, please provide your:\n",
            "pt": "Para me ajudar a compreender melhor o seu perfil profissional e fornecer recomendações mais precisas, por favor forneça o seu:\n",
            "fr": "Pour m'aider à mieux comprendre votre profil professionnel et fournir des recommandations plus précises, veuillez fournir votre :\n",
            "es": "Para ayudarme a comprender mejor su perfil profesional y proporcionar recomendaciones más precisas, por favor proporcione su:\n"
        }
        summary_parts.append(personal_links_help.get(language, personal_links_help["en"]))
        
        for link_info in missing_personal_links:
            summary_parts.append(f"- {link_info['label']}\n")
        
        summary_parts.append("\n")
    
    # Work Experience - show DETAILS, not just count
    experience = structured_data.get("experience") or structured_data.get("work_experience") or []
    if experience and isinstance(experience, list) and len(experience) > 0:
        label_messages = {
            "en": "**Work Experience:**\n",
            "pt": "**Experiência Profissional:**\n",
            "fr": "**Expérience professionnelle :**\n",
            "es": "**Experiencia Laboral:**\n"
        }
        summary_parts.append(label_messages.get(language, label_messages["en"]))
        
        company_map = {
            "en": "Company:",
            "pt": "Empresa:",
            "fr": "Entreprise :",
            "es": "Empresa:"
        }
        duration_map = {
            "en": "Duration:",
            "pt": "Duração:",
            "fr": "Durée :",
            "es": "Duración:"
        }
        
        for idx, exp in enumerate(experience, 1):
            if isinstance(exp, dict):
                exp_parts = []
                position = exp.get("position") or exp.get("title") or exp.get("job_title")
                if position:
                    exp_parts.append(f"  {idx}. **{position}**")
                
                company = exp.get("company") or exp.get("employer") or exp.get("organization")
                if company:
                    exp_parts.append(f"     {company_map.get(language, 'Company:')} {company}")
                
                duration = exp.get("duration")
                if not duration:
                    start_date = exp.get("start_date") or exp.get("from") or exp.get("start")
                    end_date = exp.get("end_date") or exp.get("to") or exp.get("end") or "Present"
                    if start_date:
                        duration = f"{start_date} - {end_date}"
                
                if duration:
                    exp_parts.append(f"     {duration_map.get(language, 'Duration:')} {duration}")
                
                if exp_parts:
                    summary_parts.append("\n".join(exp_parts))
                    summary_parts.append("\n")
        
        summary_parts.append("\n")
    
    # Education - show details
    education = structured_data.get("education") or []
    if education and isinstance(education, list) and len(education) > 0:
        label_messages = {
            "en": "**Education:**\n",
            "pt": "**Formação:**\n",
            "fr": "**Formation :**\n",
            "es": "**Formación:**\n"
        }
        summary_parts.append(label_messages.get(language, label_messages["en"]))
        
        institution_map = {
            "en": "Institution:",
            "pt": "Instituição:",
            "fr": "Établissement :",
            "es": "Institución:"
        }
        year_map = {
            "en": "Year:",
            "pt": "Ano:",
            "fr": "Année :",
            "es": "Año:"
        }
        
        for idx, edu in enumerate(education, 1):
            if isinstance(edu, dict):
                edu_parts = []
                degree = edu.get("degree") or edu.get("qualification") or edu.get("field_of_study")
                if degree:
                    edu_parts.append(f"  {idx}. {degree}")
                
                institution = edu.get("institution") or edu.get("school") or edu.get("university")
                if institution:
                    edu_parts.append(f"     {institution_map.get(language, 'Institution:')} {institution}")
                
                year = edu.get("year") or edu.get("graduation_year") or edu.get("end_date")
                if year:
                    edu_parts.append(f"     {year_map.get(language, 'Year:')} {year}")
                
                if edu_parts:
                    summary_parts.append("\n".join(edu_parts))
                    summary_parts.append("\n")
        
        summary_parts.append("\n")
    
    # Skills - show all skills, organized by type if available
    skills_data = structured_data.get("skills", {})
    if isinstance(skills_data, dict):
        # Skills organized by type (technical, soft, languages, etc.)
        all_skills = []
        
        if skills_data.get("technical") or skills_data.get("hard_skills"):
            tech_skills = skills_data.get("technical") or skills_data.get("hard_skills")
            if tech_skills and isinstance(tech_skills, list):
                skills_label = {"en": "Technical Skills", "pt": "Competências Técnicas", "fr": "Compétences techniques", "es": "Habilidades Técnicas"}
                skills_display = ', '.join(str(s) for s in tech_skills[:20])
                if len(tech_skills) > 20:
                    skills_display += f" (+{len(tech_skills) - 20} more)"
                all_skills.append(f"**{skills_label.get(language, 'Technical Skills')}:** {skills_display}")
        
        if skills_data.get("soft") or skills_data.get("soft_skills"):
            soft_skills = skills_data.get("soft") or skills_data.get("soft_skills")
            if soft_skills and isinstance(soft_skills, list):
                skills_label = {"en": "Soft Skills", "pt": "Competências Interpessoais", "fr": "Compétences douces", "es": "Habilidades Blandas"}
                skills_display = ', '.join(str(s) for s in soft_skills[:15])
                if len(soft_skills) > 15:
                    skills_display += f" (+{len(soft_skills) - 15} more)"
                all_skills.append(f"**{skills_label.get(language, 'Soft Skills')}:** {skills_display}")
        
        if skills_data.get("languages"):
            languages = skills_data.get("languages")
            if languages and isinstance(languages, list):
                skills_label = {"en": "Languages", "pt": "Idiomas", "fr": "Langues", "es": "Idiomas"}
                all_skills.append(f"**{skills_label.get(language, 'Languages')}:** {', '.join(str(l) for l in languages)}")
        
        if all_skills:
            label_messages = {
                "en": "**Skills:**\n",
                "pt": "**Competências:**\n",
                "fr": "**Compétences :**\n",
                "es": "**Habilidades:**\n"
            }
            summary_parts.append(label_messages.get(language, label_messages["en"]))
            summary_parts.append("\n".join(f"- {skill}" for skill in all_skills))
            summary_parts.append("\n\n")
    elif isinstance(skills_data, list) and len(skills_data) > 0:
        # Skills as simple list
        skills_count = len(skills_data)
        top_skills = ", ".join(str(s) for s in skills_data[:20])
        if skills_count > 20:
            top_skills += f" (+{skills_count - 20} more)"
        label_messages = {
            "en": f"**Skills:** {top_skills}\n",
            "pt": f"**Competências:** {top_skills}\n",
            "fr": f"**Compétences :** {top_skills}\n",
            "es": f"**Habilidades:** {top_skills}\n"
        }
        summary_parts.append(label_messages.get(language, label_messages["en"]))
        summary_parts.append("\n\n")
    
    # Certifications
    certifications = structured_data.get("certifications") or []
    if certifications and isinstance(certifications, list) and len(certifications) > 0:
        label_messages = {
            "en": "**Certifications:**\n",
            "pt": "**Certificações:**\n",
            "fr": "**Certifications :**\n",
            "es": "**Certificaciones:**\n"
        }
        summary_parts.append(label_messages.get(language, label_messages["en"]))
        summary_parts.append("\n".join(f"- {cert}" for cert in certifications[:10]))
        if len(certifications) > 10:
            summary_parts.append(f"\n(+ {len(certifications) - 10} more)")
        summary_parts.append("\n\n")
    
    # Detect companies without links/contact info
    companies_missing_links = []
    if experience and isinstance(experience, list):
        for exp in experience:
            if isinstance(exp, dict):
                company_name = exp.get("company") or exp.get("employer") or exp.get("organization")
                if company_name:
                    # Check if company has links/contact info
                    company_website = exp.get("website") or exp.get("company_website") or exp.get("url")
                    company_linkedin = exp.get("linkedin") or exp.get("company_linkedin")
                    company_email = exp.get("email") or exp.get("company_email")
                    
                    if not company_website and not company_linkedin and not company_email:
                        # Company missing links
                        companies_missing_links.append({
                            "company_name": company_name,
                            "position": exp.get("position") or exp.get("title") or exp.get("job_title") or "N/A"
                        })
    
    # Detect missing required/recommended data
    missing_required = []
    missing_recommended = []
    
    # Required fields
    if not name:
        missing_required.append({"field": "name", "label": {
            "en": "Name", "pt": "Nome", "fr": "Nom", "es": "Nombre"
        }.get(language, "Name")})
    
    if not email:
        missing_required.append({"field": "email", "label": {
            "en": "Email", "pt": "Email", "fr": "Email", "es": "Email"
        }.get(language, "Email")})
    
    # Recommended fields
    if not phone:
        missing_recommended.append({"field": "phone", "label": {
            "en": "Phone number", "pt": "Número de telefone", "fr": "Numéro de téléphone", "es": "Número de teléfono"
        }.get(language, "Phone")})
    
    if not location:
        missing_recommended.append({"field": "location", "label": {
            "en": "Location", "pt": "Localização", "fr": "Localisation", "es": "Ubicación"
        }.get(language, "Location")})
    
    # Reuse experience variable already computed above
    if not experience or len(experience) == 0:
        missing_recommended.append({"field": "work_experience", "label": {
            "en": "Work experience", "pt": "Experiência profissional", "fr": "Expérience professionnelle", "es": "Experiencia laboral"
        }.get(language, "Work experience")})
    
    # Reuse skills_data variable already computed above
    has_skills = False
    if isinstance(skills_data, dict):
        has_skills = bool(
            skills_data.get("technical") or 
            skills_data.get("soft") or 
            skills_data.get("languages")
        )
    elif isinstance(skills_data, list):
        has_skills = len(skills_data) > 0
    
    if not has_skills:
        missing_recommended.append({"field": "skills", "label": {
            "en": "Skills", "pt": "Competências", "fr": "Compétences", "es": "Habilidades"
        }.get(language, "Skills")})
    
    # Add companies missing links section
    if companies_missing_links:
        summary_parts.append("\n")
        companies_label_messages = {
            "en": "**Companies Missing Links/Contact Information:**\n",
            "pt": "**Empresas sem Links/Informações de Contacto:**\n",
            "fr": "**Entreprises sans Liens/Informations de Contact :**\n",
            "es": "**Empresas sin Enlaces/Información de Contacto:**\n"
        }
        summary_parts.append(companies_label_messages.get(language, companies_label_messages["en"]))
        
        companies_help_messages = {
            "en": "To help me better understand these companies and provide you with more accurate information, please provide:\n- Website URL\n- LinkedIn company page URL\n- Company email (optional)\n\n",
            "pt": "Para me ajudar a compreender melhor estas empresas e fornecer-lhe informações mais precisas, por favor forneça:\n- URL do website\n- URL da página LinkedIn da empresa\n- Email da empresa (opcional)\n\n",
            "fr": "Pour m'aider à mieux comprendre ces entreprises et vous fournir des informations plus précises, veuillez fournir :\n- URL du site web\n- URL de la page LinkedIn de l'entreprise\n- E-mail de l'entreprise (optionnel)\n\n",
            "es": "Para ayudarme a comprender mejor estas empresas y proporcionarle información más precisa, por favor proporcione:\n- URL del sitio web\n- URL de la página de LinkedIn de la empresa\n- Correo electrónico de la empresa (opcional)\n\n"
        }
        summary_parts.append(companies_help_messages.get(language, companies_help_messages["en"]))
        
        for company_info in companies_missing_links:
            company_line = f"- **{company_info['company_name']}** ({company_info['position']})\n"
            summary_parts.append(company_line)
        
        summary_parts.append("\n")
    
    # Add missing data section if needed
    if missing_required or missing_recommended:
        summary_parts.append("\n")
        missing_messages = {
            "en": "**Missing Information:**\n",
            "pt": "**Informações em Falta:**\n",
            "fr": "**Informations manquantes :**\n",
            "es": "**Información Faltante:**\n"
        }
        summary_parts.append(missing_messages.get(language, missing_messages["en"]))
        
        if missing_required:
            required_label = {
                "en": "**Required:**",
                "pt": "**Obrigatório:**",
                "fr": "**Obligatoire :**",
                "es": "**Obligatorio:**"
            }.get(language, "**Required:**")
            summary_parts.append(f"{required_label} ")
            required_fields = ", ".join([item["label"] for item in missing_required])
            summary_parts.append(f"{required_fields}\n")
        
        if missing_recommended:
            recommended_label = {
                "en": "**Recommended:**",
                "pt": "**Recomendado:**",
                "fr": "**Recommandé :**",
                "es": "**Recomendado:**"
            }.get(language, "**Recommended:**")
            summary_parts.append(f"{recommended_label} ")
            recommended_fields = ", ".join([item["label"] for item in missing_recommended])
            summary_parts.append(f"{recommended_fields}\n")
        
        summary_parts.append("\n")
        ask_missing_messages = {
            "en": "Please provide the missing information above so I can create a complete profile for you.\n\n",
            "pt": "Por favor, forneça as informações em falta acima para que eu possa criar um perfil completo para si.\n\n",
            "fr": "Veuillez fournir les informations manquantes ci-dessus afin que je puisse créer un profil complet pour vous.\n\n",
            "es": "Por favor, proporcione la información faltante anterior para que pueda crear un perfil completo para usted.\n\n"
        }
        summary_parts.append(ask_missing_messages.get(language, ask_missing_messages["en"]))
    
    # Add session ID for recovery
    if session_id:
        session_id_messages = {
            "en": f"**💾 Session ID:** `{session_id}`\n\nYou can use this ID to recover and continue your session later.\n\n",
            "pt": f"**💾 ID da Sessão:** `{session_id}`\n\nPode usar este ID para recuperar e continuar a sua sessão mais tarde.\n\n",
            "fr": f"**💾 ID de session :** `{session_id}`\n\nVous pouvez utiliser cet ID pour récupérer et continuer votre session plus tard.\n\n",
            "es": f"**💾 ID de Sesión:** `{session_id}`\n\nPuede usar este ID para recuperar y continuar su sesión más tarde.\n\n"
        }
        summary_parts.append(session_id_messages.get(language, session_id_messages["en"]))
    
    # Confirmation question
    confirmation_messages = {
        "en": "**Is this information correct?** You can:\n- Confirm if everything looks good\n- Tell me what to change\n- Provide any missing information above",
        "pt": "**Esta informação está correta?** Pode:\n- Confirmar se está tudo bem\n- Dizer-me o que alterar\n- Fornecer qualquer informação em falta acima",
        "fr": "**Ces informations sont-elles correctes ?** Vous pouvez :\n- Confirmer si tout semble bon\n- Me dire ce qu'il faut modifier\n- Fournir les informations manquantes ci-dessus",
        "es": "**¿Esta información es correcta?** Puedes:\n- Confirmar si todo se ve bien\n- Decirme qué cambiar\n- Proporcionar cualquier información faltante anterior"
    }
    summary_parts.append(confirmation_messages.get(language, confirmation_messages["en"]))
    
    return "".join(summary_parts)


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/welcome", response_model=ChatbotWelcomeResponse)
async def welcome(request: ChatbotWelcomeRequest):
    """
    Start a new chatbot session.
    
    Creates a new conversation session after collecting consents.
    Returns session_id and welcome message.
    """
    try:
        chatbot_service = get_chatbot_service()
        
        session = await chatbot_service.start_session(
            language=request.language,
            consent_read_cv=request.consent_read_cv,
            consent_read_job_opportunity=request.consent_read_job_opportunity,
            consent_analyze_links=request.consent_analyze_links,
            consent_store_data=request.consent_store_data
        )
        
        if not session:
            raise HTTPException(
                status_code=500,
                detail="Failed to start chatbot session"
            )
        
        return ChatbotWelcomeResponse(
            session_id=session["session_id"],
            message=session["message"],
            current_step=session["current_step"],
            next_actions=session.get("next_actions", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chatbot welcome: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error starting chatbot session"
        )


@router.post("/message", response_model=ChatbotBotMessageResponse)
async def send_message(request: ChatbotMessageRequest):
    """
    Send a message to the chatbot and get response.
    
    Handles user messages and generates appropriate bot responses
    based on current conversation step.
    """
    try:
        chatbot_service = get_chatbot_service()
        
        bot_response = await chatbot_service.handle_message(
            session_id=request.session_id,
            user_message=request.message,
            message_type=request.message_type
        )
        
        if not bot_response:
            raise HTTPException(
                status_code=500,
                detail="Failed to process message"
            )
        
        # Get latest messages to construct response
        db_service = get_chatbot_database_service()
        messages = db_service.get_messages(request.session_id, limit=1)
        
        bot_message = None
        if messages and messages[-1]["role"] == "bot":
            bot_message = messages[-1]
        
        if not bot_message:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve bot response"
            )
        
        from models.chatbot import ChatbotMessage
        from datetime import datetime
        
        return ChatbotBotMessageResponse(
            message=ChatbotMessage(
                id=UUID(bot_message["id"]),
                role=bot_message["role"],
                content=bot_message["content"],
                message_type=bot_message.get("message_type", "text"),
                metadata=bot_message.get("metadata", {}),
                created_at=datetime.fromisoformat(bot_message["created_at"].replace("Z", "+00:00"))
            ),
            current_step=bot_response.get("current_step", "unknown"),
            next_suggested_actions=bot_response.get("next_suggested_actions"),
            progress_indicator=bot_response.get("progress_indicator")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chatbot message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing message"
        )


@router.post("/profile")
async def update_profile(request: ChatbotProfileDataRequest):
    """
    Update profile data during conversation.
    
    Extracts and stores profile information from user input.
    Creates or updates candidate record if email is provided.
    """
    try:
        db_service = get_chatbot_database_service()
        
        # Get session
        session = db_service.get_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        # Update profile data
        profile_data = {
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "location": request.location,
            "links": request.links
        }
        
        current_profile = session.get("profile_data", {})
        current_profile.update(profile_data)
        
        # Create or update candidate record
        candidate_service = get_candidate_service()
        candidate = await candidate_service.find_or_create(
            email=request.email,
            name=request.name,
            phone=request.phone,
            country=request.location,
            consent_given=True
        )
        
        candidate_id = None
        if candidate:
            candidate_id = UUID(candidate["id"])
        
        # Update session
        db_service.update_session(request.session_id, {
            "profile_data": current_profile,
            "candidate_id": str(candidate_id) if candidate_id else None,
            "current_step": "cv_upload"
        })
        
        return JSONResponse({
            "status": "success",
            "message": "Profile updated successfully",
            "current_step": "cv_upload"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error updating profile"
        )


@router.post("/cv/upload")
async def upload_cv(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload CV in chatbot context.
    
    Accepts PDF or DOCX files.
    Extracts text and structured data from CV.
    """
    try:
        session_uuid = UUID(session_id)
        db_service = get_chatbot_database_service()
        
        # Get session
        session = db_service.get_session(session_uuid)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        # Validate file type
        if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF and DOCX are supported."
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract text
        success, extracted_text, error = FileProcessor.extract_text(
            file_content=file_content,
            filename=file.filename or "cv.pdf"
        )
        
        if not success or not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract text from CV"
            )
        
        # IMPORTANT: Convert to Markdown before sending to AI
        # This ensures all information is preserved and properly formatted for AI processing
        cv_markdown = FileProcessor.text_to_markdown(extracted_text)
        
        # Extract structured data from CV using AI
        from services.ai_analysis import get_ai_analysis_service
        ai_service = get_ai_analysis_service()
        language = session.get("language", "en")
        
        logger.info(f"[Chatbot] Extracting structured data from CV (Markdown format) for session {session_uuid}")
        structured_cv_data = await ai_service.extract_cv_data(
            cv_text=cv_markdown,  # Send Markdown, not raw text
            language=language
        )
        
        # Update session with CV data
        from datetime import datetime as dt
        cv_data = {
            "filename": file.filename,
            "content_type": file.content_type,
            "extracted_text": extracted_text,
            "structured_data": structured_cv_data or {},
            "uploaded_at": dt.utcnow().isoformat()
        }
        
        # Extract profile information from structured CV data
        profile_data = {}
        if structured_cv_data:
            # Map CV extraction fields to profile fields
            # Check both top level and personal_info nested
            personal_info = structured_cv_data.get("personal_info", {})
            if isinstance(personal_info, dict):
                if "name" in personal_info:
                    profile_data["name"] = personal_info["name"]
                if "email" in personal_info:
                    profile_data["email"] = personal_info["email"]
                if "phone" in personal_info or "phone_number" in personal_info:
                    profile_data["phone"] = personal_info.get("phone") or personal_info.get("phone_number")
                if "location" in personal_info or "address" in personal_info:
                    profile_data["location"] = personal_info.get("location") or personal_info.get("address")
            
            # Also check top level fields
            if "name" in structured_cv_data and "name" not in profile_data:
                profile_data["name"] = structured_cv_data["name"]
            if "email" in structured_cv_data and "email" not in profile_data:
                profile_data["email"] = structured_cv_data["email"]
            if ("phone" in structured_cv_data or "phone_number" in structured_cv_data) and "phone" not in profile_data:
                profile_data["phone"] = structured_cv_data.get("phone") or structured_cv_data.get("phone_number")
            if ("location" in structured_cv_data or "address" in structured_cv_data) and "location" not in profile_data:
                profile_data["location"] = structured_cv_data.get("location") or structured_cv_data.get("address")
            
            # Extract social media links
            links = {}
            if isinstance(personal_info, dict):
                if "linkedin" in personal_info:
                    links["linkedin"] = personal_info["linkedin"]
                if "github" in personal_info:
                    links["github"] = personal_info["github"]
                if "portfolio" in personal_info or "website" in personal_info:
                    links["portfolio"] = personal_info.get("portfolio") or personal_info.get("website")
            
            # Also check top level
            if "linkedin" in structured_cv_data or "github" in structured_cv_data:
                if "linkedin" not in links and "linkedin" in structured_cv_data:
                    links["linkedin"] = structured_cv_data["linkedin"]
                if "github" not in links and "github" in structured_cv_data:
                    links["github"] = structured_cv_data["github"]
                if ("portfolio" in structured_cv_data or "website" in structured_cv_data) and "portfolio" not in links:
                    links["portfolio"] = structured_cv_data.get("portfolio") or structured_cv_data.get("website")
            
            if links:
                profile_data["links"] = links
        
        # Merge with existing profile data
        existing_profile = session.get("profile_data", {})
        existing_profile.update(profile_data)
        profile_data = existing_profile
        
        # Update session with both CV data and profile data
        db_service.update_session(session_uuid, {
            "cv_data": cv_data,
            "profile_data": profile_data,
            "current_step": "cv_review"  # Changed to review step
        })
        
        # Generate formatted summary message showing extracted data
        # Include session ID for recovery
        summary_message = _generate_cv_extraction_summary(
            structured_cv_data, 
            profile_data, 
            language,
            session_id=str(session_uuid)
        )
        
        # Add bot message with extracted information summary
        db_service.add_message(
            session_id=session_uuid,
            role="bot",
            content=summary_message,
            message_type="text",
            metadata={
                "extracted_data": structured_cv_data,
                "profile_data": profile_data,
                "step": "cv_review"
            }
        )
        
        return JSONResponse({
            "status": "success",
            "message": "CV uploaded and processed successfully",
            "current_step": "cv_review",
            "extracted_data": structured_cv_data,
            "profile_data": profile_data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading CV: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error uploading CV"
        )


@router.get("/session/{session_id}/messages")
async def get_messages(session_id: UUID, limit: Optional[int] = None):
    """
    Get conversation messages for a session.
    
    Returns all messages ordered by creation time.
    """
    try:
        db_service = get_chatbot_database_service()
        
        # Get session
        session = db_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        # Get messages
        messages = db_service.get_messages(session_id, limit=limit)
        
        if not messages:
            return JSONResponse({
                "status": "success",
                "messages": [],
                "total": 0
            })
        
        # Convert messages to response format
        message_list = []
        for msg in messages:
            try:
                # Handle created_at - Supabase returns it as string or datetime
                created_at_str = msg.get("created_at")
                if isinstance(created_at_str, str):
                    # Parse ISO format string
                    if created_at_str.endswith("Z"):
                        created_at_str = created_at_str.replace("Z", "+00:00")
                    elif "+" not in created_at_str and len(created_at_str) > 10:
                        # Check if it looks like ISO format without timezone
                        try:
                            from dateutil import parser
                            created_at_str = parser.isoparse(created_at_str).isoformat()
                        except:
                            # Fallback: assume UTC
                            if created_at_str.endswith("Z"):
                                created_at_str = created_at_str.replace("Z", "+00:00")
                            else:
                                created_at_str = created_at_str + "+00:00"
                elif hasattr(created_at_str, "isoformat"):
                    # It's a datetime object
                    created_at_str = created_at_str.isoformat()
                
                message_list.append({
                    "id": str(msg["id"]),
                    "role": msg["role"],
                    "content": msg["content"],
                    "message_type": msg.get("message_type", "text"),
                    "metadata": msg.get("metadata", {}),
                    "created_at": created_at_str
                })
            except Exception as e:
                logger.warning(f"Skipping malformed message {msg.get('id')}: {e}")
                continue
        
        return JSONResponse({
            "status": "success",
            "messages": message_list,
            "total": len(message_list)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error getting messages"
        )


@router.get("/session/{session_id}")
async def get_session(session_id: UUID):
    """
    Get chatbot session details.
    
    Returns session information including current step and metadata.
    Can be used to recover and continue an existing session.
    """
    try:
        db_service = get_chatbot_database_service()
        
        session = db_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        # Get messages for this session
        messages = db_service.get_messages(session_id)
        
        # Convert messages to response format
        message_list = []
        for msg in messages:
            try:
                created_at_str = msg.get("created_at")
                if isinstance(created_at_str, str):
                    if created_at_str.endswith("Z"):
                        created_at_str = created_at_str.replace("Z", "+00:00")
                    elif "+" not in created_at_str and len(created_at_str) > 10:
                        try:
                            from dateutil import parser
                            created_at_str = parser.isoparse(created_at_str).isoformat()
                        except:
                            if created_at_str.endswith("Z"):
                                created_at_str = created_at_str.replace("Z", "+00:00")
                            else:
                                created_at_str = created_at_str + "+00:00"
                elif hasattr(created_at_str, "isoformat"):
                    created_at_str = created_at_str.isoformat()
                
                message_list.append({
                    "id": str(msg["id"]),
                    "role": msg["role"],
                    "content": msg["content"],
                    "message_type": msg.get("message_type", "text"),
                    "metadata": msg.get("metadata", {}),
                    "created_at": created_at_str
                })
            except Exception as e:
                logger.warning(f"Skipping malformed message {msg.get('id')}: {e}")
                continue
        
        return JSONResponse({
            "status": "success",
            "session": session,
            "messages": message_list,
            "total_messages": len(message_list)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error getting session"
        )
