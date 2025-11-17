"""
Chatbot CV Preparation Service.

Main service that orchestrates the conversational chatbot flow for CV preparation.
Separate from existing candidate/interviewer flows to avoid interference.

This service handles:
- Conversational flow management
- Dynamic question generation
- CV and job opportunity analysis
- CV generation (ATS friendly and human friendly)
- Digital footprint analysis
- Interview preparation
- Employability scoring
"""

import json
from typing import Dict, Any, List, Optional
from uuid import UUID
import logging

from services.database.chatbot_service import get_chatbot_database_service
from services.database.candidate_service import get_candidate_service
from services.database.cv_service import get_cv_service
from services.database.job_posting_service import get_job_posting_service
from services.database.company_profile_service import get_company_profile_service
from services.database.candidate_profile_service import get_candidate_profile_service
from services.ai import get_ai_manager, AIRequest, PromptType
from services.ai.prompts import get_prompt
from services.ai_analysis import get_ai_analysis_service
from services.search.brave_search import get_brave_search_service
from utils.file_processor import FileProcessor
import re

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    Main service for chatbot CV preparation feature.
    
    Orchestrates the complete conversational flow from welcome to completion.
    """
    
    # Flow steps in order
    FLOW_STEPS = [
        "welcome",
        "profile_collection",
        "cv_upload",
        "job_opportunity",
        "digital_footprint",
        "adaptive_questions",
        "cv_generation",
        "interview_prep",
        "score_and_recommendations",
        "completed"
    ]
    
    def __init__(self):
        self.db_service = get_chatbot_database_service()
        self.candidate_service = get_candidate_service()
        self.cv_service = get_cv_service()
        self.job_posting_service = get_job_posting_service()
        self.company_profile_service = get_company_profile_service()
        self.candidate_profile_service = get_candidate_profile_service()
        self.ai_manager = get_ai_manager()
        self.ai_analysis_service = get_ai_analysis_service()
        self.brave_service = get_brave_search_service()
    
    # =========================================================================
    # Session Management
    # =========================================================================
    
    async def start_session(
        self,
        language: str = "en",
        consent_read_cv: bool = False,
        consent_read_job_opportunity: bool = False,
        consent_analyze_links: bool = False,
        consent_store_data: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Start a new chatbot session.
        
        Args:
            language: Language for conversation
            consent_*: Various consent flags
            
        Returns:
            Session dict with session_id, or None if failed
        """
        try:
            if not all([consent_read_cv, consent_read_job_opportunity, 
                       consent_analyze_links, consent_store_data]):
                logger.warning("All consents must be given to start session")
                return None
            
            session = self.db_service.create_session(
                language=language,
                consent_given=True,
                profile_data={}
            )
            
            if not session:
                logger.error("Failed to create chatbot session")
                return None
            
            session_id = UUID(session["id"])
            
            # Add welcome message
            welcome_msg = await self._generate_welcome_message(language)
            self.db_service.add_message(
                session_id=session_id,
                role="bot",
                content=welcome_msg,
                message_type="text"
            )
            
            return {
                "session_id": session_id,
                "current_step": "welcome",
                "message": welcome_msg,
                "next_actions": [
                    "provide_profile_data",
                    "upload_cv"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error starting chatbot session: {e}")
            return None
    
    async def _generate_welcome_message(self, language: str) -> str:
        """Generate welcome message asking for CV upload first."""
        messages = {
            "en": "Hello! I'm your AI CV preparation assistant. I'll help you optimize your CV for a specific job opportunity.\n\nTo get started, please share your current CV (PDF or DOCX format). I'll extract all the information I need from it - your name, email, phone number, social media links, work experience, skills, and more. Then I'll show you what I found and you can confirm, edit, or add any additional information that's relevant but not in your CV.",
            "pt": "Olá! Sou o seu assistente de IA para preparação de currículos. Vou ajudá-lo a otimizar o seu CV para uma oportunidade de emprego específica.\n\nPara começar, por favor partilhe o seu CV atual (formato PDF ou DOCX). Vou extrair todas as informações necessárias dele - nome, email, telefone, links de redes sociais, experiência profissional, competências e muito mais. Depois mostro-lhe o que encontrei e pode confirmar, editar ou adicionar qualquer informação adicional que seja relevante mas que não esteja no seu CV.",
            "fr": "Bonjour ! Je suis votre assistant IA pour la préparation de CV. Je vais vous aider à optimiser votre CV pour une opportunité d'emploi spécifique.\n\nPour commencer, veuillez partager votre CV actuel (format PDF ou DOCX). J'extrairai toutes les informations nécessaires - nom, email, numéro de téléphone, liens de réseaux sociaux, expérience professionnelle, compétences et plus encore. Ensuite, je vous montrerai ce que j'ai trouvé et vous pourrez confirmer, modifier ou ajouter toute information supplémentaire pertinente qui ne se trouve pas dans votre CV.",
            "es": "¡Hola! Soy tu asistente de IA para la preparación de CV. Te ayudaré a optimizar tu CV para una oportunidad de trabajo específica.\n\nPara comenzar, por favor comparte tu CV actual (formato PDF o DOCX). Extraeré toda la información necesaria: nombre, email, teléfono, enlaces de redes sociales, experiencia laboral, habilidades y más. Luego te mostraré lo que encontré y podrás confirmar, editar o agregar cualquier información adicional relevante que no esté en tu CV."
        }
        
        return messages.get(language, messages["en"])
    
    # =========================================================================
    # Message Handling
    # =========================================================================
    
    async def handle_message(
        self,
        session_id: UUID,
        user_message: str,
        message_type: str = "text"
    ) -> Optional[Dict[str, Any]]:
        """
        Handle user message and generate conversational bot response using AI.
        
        Args:
            session_id: Session ID
            user_message: User's message
            message_type: Type of message
            
        Returns:
            Bot response dict or None if failed
        """
        try:
            # Get session
            session = self.db_service.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return None
            
            # Add user message
            self.db_service.add_message(
                session_id=session_id,
                role="user",
                content=user_message,
                message_type=message_type
            )
            
            # Check if user provided personal or company links/information
            # Process personal links if detected in message
            await self._process_personal_links(session_id, session, user_message)
            
            # Process company links ONLY if company-specific links are detected
            # (linkedin.com/company or explicit company websites)
            # Don't process companies automatically just because they're in the CV
            if re.search(r'linkedin\.com/company|(?:website|site|empresa|company)[\s:]*http', user_message, re.IGNORECASE):
                await self._process_company_links(session_id, session, user_message)
            
            # Get conversation history
            messages = self.db_service.get_messages(session_id, limit=20)
            language = session.get("language", "en")
            
            # Generate conversational response using AI
            bot_response_content = await self._generate_conversational_response(
                session=session,
                user_message=user_message,
                conversation_history=messages,
                language=language
            )
            
            if not bot_response_content:
                # Fallback to error message
                bot_response_content = await self._generate_error_message(language)
            
            # Detect if user provided specific information (CV, job, profile)
            detected_info = await self._detect_user_input(session, user_message, language)
            
            # Update session with detected information
            if detected_info:
                update_data = {}
                if detected_info.get("profile_data"):
                    current_profile = session.get("profile_data", {})
                    current_profile.update(detected_info["profile_data"])
                    update_data["profile_data"] = current_profile
                
                if detected_info.get("cv_data"):
                    update_data["cv_data"] = detected_info["cv_data"]
                
                if detected_info.get("job_opportunity_data"):
                    update_data["job_opportunity_data"] = detected_info["job_opportunity_data"]
                
                if update_data:
                    self.db_service.update_session(session_id, update_data)
            
            # Add bot response to messages
            bot_response = {
                "content": bot_response_content,
                "message_type": "text",
                "metadata": detected_info or {}
            }
            
            self.db_service.add_message(
                session_id=session_id,
                role="bot",
                content=bot_response_content,
                message_type="text",
                metadata=detected_info or {}
            )
            
            return bot_response
            
        except Exception as e:
            logger.error(f"Error handling message in session {session_id}: {e}", exc_info=True)
            return None
    
    async def _handle_welcome_step(self, session: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Handle welcome step - transition to profile collection."""
        language = session.get("language", "en")
        
        return {
            "content": await self._generate_profile_collection_message(language),
            "current_step": "profile_collection",
            "next_suggested_actions": ["provide_name_email"]
        }
    
    async def _generate_profile_collection_message(self, language: str) -> str:
        """Generate message asking for profile data."""
        messages = {
            "en": "Great! Let's start with your basic information. Please provide:\n- Full name\n- Email address\n- Phone number (optional)\n- Location (city and country, optional)\n\nYou can also share links to your LinkedIn, GitHub, portfolio, or other professional profiles.",
            "pt": "Ótimo! Vamos começar com as suas informações básicas. Por favor, forneça:\n- Nome completo\n- Endereço de email\n- Número de telefone (opcional)\n- Localização (cidade e país, opcional)\n\nTambém pode partilhar links para o seu LinkedIn, GitHub, portefólio ou outros perfis profissionais.",
            "fr": "Parfait ! Commençons par vos informations de base. Veuillez fournir :\n- Nom complet\n- Adresse e-mail\n- Numéro de téléphone (optionnel)\n- Localisation (ville et pays, optionnel)\n\nVous pouvez également partager des liens vers votre LinkedIn, GitHub, portfolio ou autres profils professionnels.",
            "es": "¡Genial! Comencemos con tu información básica. Por favor proporciona:\n- Nombre completo\n- Dirección de correo electrónico\n- Número de teléfono (opcional)\n- Ubicación (ciudad y país, opcional)\n\nTambién puedes compartir enlaces a tu LinkedIn, GitHub, portfolio u otros perfiles profesionales."
        }
        
        return messages.get(language, messages["en"])
    
    async def _handle_profile_collection_step(self, session: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Handle profile collection step - extract and store profile data."""
        # This is a simplified version - in production, would use NLP to extract structured data
        # For now, we'll use AI to extract profile information from user message
        
        language = session.get("language", "en")
        session_id = UUID(session["id"])
        
        try:
            # Use AI to extract profile data from message
            profile_data = await self._extract_profile_data(user_message, language)
            
            if profile_data:
                # Update session with profile data
                current_profile = session.get("profile_data", {})
                current_profile.update(profile_data)
                
                # Create or update candidate record if we have email
                candidate_id = None
                if "email" in profile_data:
                    candidate = await self.candidate_service.find_or_create(
                        email=profile_data["email"],
                        name=profile_data.get("name", "Unknown"),
                        phone=profile_data.get("phone"),
                        country=profile_data.get("location"),
                        consent_given=True
                    )
                    if candidate:
                        candidate_id = UUID(candidate["id"])
                
                self.db_service.update_session(session_id, {
                    "profile_data": current_profile,
                    "candidate_id": str(candidate_id) if candidate_id else None
                })
                
                # Move to CV upload step
                return {
                    "content": await self._generate_cv_upload_message(language),
                    "current_step": "cv_upload",
                    "next_suggested_actions": ["upload_cv"]
                }
            else:
                # Ask for clarification
                return {
                    "content": await self._generate_clarification_message(language, "profile"),
                    "current_step": "profile_collection"
                }
                
        except Exception as e:
            logger.error(f"Error handling profile collection: {e}")
            return {
                "content": await self._generate_error_message(language),
                "current_step": "profile_collection"
            }
    
    async def _extract_profile_data(self, text: str, language: str) -> Optional[Dict[str, Any]]:
        """Extract structured profile data from user message using AI."""
        try:
            # Get prompt for profile extraction
            template = await get_prompt("chatbot_profile_extraction", language)
            if not template:
                # Fallback: try to create a basic prompt
                template = """Extract profile information from the following message.
Return JSON with keys: name, email, phone, location, links (object with linkedin, github, portfolio, etc).
If information is missing, use null.
Message: {text}"""
            
            ai_request = AIRequest(
                prompt_type=PromptType.CHATBOT_PROFILE_EXTRACTION,
                template=template,
                variables={"text": text},
                language=language,
                temperature=0.3,
                max_tokens=500
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            if response.success and response.data:
                return response.data
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting profile data: {e}")
            return None
    
    async def _generate_cv_upload_message(self, language: str) -> str:
        """Generate message asking for CV upload."""
        messages = {
            "en": "Perfect! Now please upload your current CV. I accept PDF and DOCX formats. I'll analyze it and extract your experience, skills, education, and other relevant information.",
            "pt": "Perfeito! Agora, por favor, carregue o seu CV atual. Aceito formatos PDF e DOCX. Vou analisá-lo e extrair a sua experiência, competências, educação e outras informações relevantes.",
            "fr": "Parfait ! Veuillez maintenant télécharger votre CV actuel. J'accepte les formats PDF et DOCX. Je vais l'analyser et extraire votre expérience, compétences, formation et autres informations pertinentes.",
            "es": "¡Perfecto! Ahora por favor sube tu CV actual. Acepto formatos PDF y DOCX. Lo analizaré y extraeré tu experiencia, habilidades, educación y otra información relevante."
        }
        
        return messages.get(language, messages["en"])
    
    async def _handle_cv_upload_step(self, session: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Handle CV upload step - note that actual file upload is handled separately."""
        language = session.get("language", "en")
        
        return {
            "content": await self._generate_job_opportunity_message(language),
            "current_step": "job_opportunity",
            "next_suggested_actions": ["provide_job_opportunity"]
        }
    
    async def _generate_job_opportunity_message(self, language: str) -> str:
        """Generate message asking for job opportunity."""
        messages = {
            "en": "Excellent! Now I need the job opportunity you're applying for. You can:\n- Paste the job posting text\n- Provide a URL to the job posting\n- Upload a file with the job description\n\nOnce I have this, I'll analyze it and identify key requirements.",
            "pt": "Excelente! Agora preciso da oportunidade de emprego para a qual se está a candidatar. Pode:\n- Colar o texto da oferta de emprego\n- Fornecer um URL para a oferta de emprego\n- Carregar um ficheiro com a descrição do trabalho\n\nDepois de ter isto, vou analisá-la e identificar os requisitos-chave.",
            "fr": "Excellent ! J'ai maintenant besoin de l'opportunité d'emploi pour laquelle vous postulez. Vous pouvez :\n- Coller le texte de l'offre d'emploi\n- Fournir une URL vers l'offre d'emploi\n- Télécharger un fichier avec la description du poste\n\nUne fois que j'aurai ces informations, je les analyserai et identifierai les exigences clés.",
            "es": "¡Excelente! Ahora necesito la oportunidad de trabajo para la que estás postulando. Puedes:\n- Pegar el texto de la oferta de trabajo\n- Proporcionar una URL a la oferta de trabajo\n- Subir un archivo con la descripción del trabajo\n\nUna vez que tenga esto, lo analizaré e identificaré los requisitos clave."
        }
        
        return messages.get(language, messages["en"])
    
    async def _handle_job_opportunity_step(self, session: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Handle job opportunity step - analyze job posting."""
        language = session.get("language", "en")
        session_id = UUID(session["id"])
        
        try:
            # Process job opportunity
            job_data = await self._analyze_job_opportunity(user_message, language, session)
            
            if job_data:
                # Store job opportunity data
                company_name = job_data.get("company") or job_data.get("company_name")
                
                self.db_service.create_job_opportunity(
                    session_id=session_id,
                    raw_text=user_message,
                    structured_data=job_data,
                    company_name=company_name,
                    job_title=job_data.get("title"),
                    location=job_data.get("location"),
                    contract_type=job_data.get("type"),
                    requirements_obligatory=job_data.get("required_skills", []),
                    requirements_preferred=job_data.get("preferred_skills", []),
                    hard_skills=job_data.get("hard_skills", []),
                    soft_skills=job_data.get("soft_skills", []),
                    culture_keywords=job_data.get("culture_keywords", []),
                    language=language
                )
                
                # Update session
                self.db_service.update_session(session_id, {
                    "job_opportunity_data": job_data
                })
                
                # Enrich company information using Brave Search if company name found
                if company_name and self.brave_service and self.brave_service.is_enabled():
                    try:
                        logger.info(f"[Chatbot] Enriching company '{company_name}' from job posting with Brave Search")
                        
                        # Check if we already have company enrichment
                        companies_enrichment = session.get("companies_enrichment", {})
                        company_data = companies_enrichment.get(company_name, {}) if companies_enrichment else {}
                        
                        website = company_data.get("website")
                        linkedin = company_data.get("linkedin")
                        
                        # Enrich company
                        if website or linkedin:
                            enrichment = await self.brave_service.enrich_company_from_links(
                                company_name=company_name,
                                website_url=website,
                                linkedin_url=linkedin,
                                email=None
                            )
                        else:
                            # Try to enrich with just company name first
                            enrichment = await self.brave_service.enrich_company(
                                company_name=company_name,
                                additional_context=f"Job posting: {job_data.get('title', '')}"
                            )
                        
                        if enrichment:
                            if not companies_enrichment:
                                companies_enrichment = {}
                            if company_name not in companies_enrichment:
                                companies_enrichment[company_name] = {
                                    "company_name": company_name,
                                    "website": None,
                                    "linkedin": None,
                                    "email": None,
                                    "enrichment_data": None
                                }
                            
                            # Update company data
                            if enrichment.website:
                                companies_enrichment[company_name]["website"] = enrichment.website
                            if enrichment.social_media.get("linkedin"):
                                companies_enrichment[company_name]["linkedin"] = enrichment.social_media["linkedin"]
                            
                            companies_enrichment[company_name]["enrichment_data"] = {
                                "website": enrichment.website,
                                "description": enrichment.description,
                                "industry": enrichment.industry,
                                "size": enrichment.size,
                                "location": enrichment.location,
                                "recent_news": enrichment.recent_news[:3] if enrichment.recent_news else [],
                                "ai_summary": enrichment.ai_summary
                            }
                            
                            # Update session with company enrichment
                            self.db_service.update_session(session_id, {
                                "companies_enrichment": companies_enrichment
                            })
                            
                            logger.info(f"[Chatbot] Successfully enriched company '{company_name}' from job posting")
                    except Exception as e:
                        logger.warning(f"[Chatbot] Failed to enrich company '{company_name}': {e}")
                
                # Perform risk assessment
                risk_assessment = await self._assess_job_risk(job_data, language)
                
                # Check if we need to ask for company links
                companies_enrichment = session.get("companies_enrichment", {}) or {}
                company_data = companies_enrichment.get(company_name, {}) if company_name and companies_enrichment else {}
                
                if company_name and not company_data.get("website") and not company_data.get("linkedin"):
                    # Ask for company links
                    company_links_message = {
                        "en": f"\n\n**📋 Next Steps:**\n\nI've analyzed the job posting. I found that the company is **{company_name}**. To provide you with the best recommendations, I'd like to know more about this company.\n\n**Could you please provide:**\n- Website URL of {company_name}\n- LinkedIn company page URL (optional but helpful)\n\nThis will help me better understand the company culture, technologies they use, and recent developments.",
                        "pt": f"\n\n**📋 Próximos Passos:**\n\nAnalisei a oferta de emprego. Descobri que a empresa é **{company_name}**. Para fornecer as melhores recomendações, gostaria de saber mais sobre esta empresa.\n\n**Pode, por favor, fornecer:**\n- URL do website da {company_name}\n- URL da página LinkedIn da empresa (opcional mas útil)\n\nIsto ajudará-me a compreender melhor a cultura da empresa, as tecnologias que usam e os desenvolvimentos recentes.",
                        "fr": f"\n\n**📋 Prochaines Étapes :**\n\nJ'ai analysé l'offre d'emploi. J'ai découvert que l'entreprise est **{company_name}**. Pour vous fournir les meilleures recommandations, j'aimerais en savoir plus sur cette entreprise.\n\n**Pouvez-vous fournir :**\n- URL du site web de {company_name}\n- URL de la page LinkedIn de l'entreprise (optionnel mais utile)\n\nCela m'aidera à mieux comprendre la culture de l'entreprise, les technologies qu'elle utilise et les développements récents.",
                        "es": f"\n\n**📋 Próximos Pasos:**\n\nHe analizado la oferta de trabajo. Descubrí que la empresa es **{company_name}**. Para proporcionarle las mejores recomendaciones, me gustaría saber más sobre esta empresa.\n\n**¿Puede proporcionar?**\n- URL del sitio web de {company_name}\n- URL de la página de LinkedIn de la empresa (opcional pero útil)\n\nEsto me ayudará a comprender mejor la cultura de la empresa, las tecnologías que utilizan y los desarrollos recientes."
                    }
                    
                    message_content = await self._generate_digital_footprint_message(language)
                    message_content += company_links_message.get(language, company_links_message["en"])
                    
                    return {
                        "content": message_content,
                        "current_step": "digital_footprint",
                        "metadata": {
                            "job_analyzed": True,
                            "risk_assessment": risk_assessment,
                            "company_name": company_name,
                            "ask_company_links": True
                        }
                    }
                
                # Move to digital footprint
                return {
                    "content": await self._generate_digital_footprint_message(language),
                    "current_step": "digital_footprint",
                    "metadata": {"job_analyzed": True, "risk_assessment": risk_assessment}
                }
            else:
                return {
                    "content": await self._generate_clarification_message(language, "job opportunity"),
                    "current_step": "job_opportunity"
                }
                
        except Exception as e:
            logger.error(f"Error handling job opportunity: {e}")
            return {
                "content": await self._generate_error_message(language),
                "current_step": "job_opportunity"
            }
    
    async def _handle_digital_footprint_step(self, session: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Handle digital footprint analysis step."""
        language = session.get("language", "en")
        session_id = UUID(session["id"])
        
        try:
            # Extract links from message
            profile_data = session.get("profile_data", {})
            links = profile_data.get("links", {})
            
            # IMPORTANT: Convert CV to Markdown before sending to AI
            from utils.file_processor import FileProcessor
            cv_text = session.get("cv_data", {}).get("extracted_text", "")
            cv_markdown = FileProcessor.text_to_markdown(cv_text) if cv_text else ""
            
            # Analyze digital footprint
            analysis = await self._analyze_digital_footprint(
                session_id=session_id,
                cv_summary=cv_markdown,  # Send Markdown, not raw text
                links=links,
                language=language
            )
            
            if analysis:
                # Store analysis
                self.db_service.create_digital_footprint(
                    session_id=session_id,
                    linkedin_url=links.get("linkedin"),
                    github_url=links.get("github"),
                    portfolio_url=links.get("portfolio"),
                    linkedin_analysis=analysis.get("linkedin_analysis", {}),
                    github_analysis=analysis.get("github_analysis", {}),
                    inconsistencies=analysis.get("inconsistencies", []),
                    recommendations=analysis.get("recommendations", [])
                )
                
                # Move to adaptive questions
                return {
                    "content": await self._generate_adaptive_questions_intro(language, analysis),
                    "current_step": "adaptive_questions",
                    "metadata": {"footprint_analyzed": True}
                }
            else:
                # Skip digital footprint if no links provided
                return {
                    "content": await self._generate_adaptive_questions_intro(language, None),
                    "current_step": "adaptive_questions"
                }
                
        except Exception as e:
            logger.error(f"Error handling digital footprint: {e}")
            return {
                "content": await self._generate_adaptive_questions_intro(language, None),
                "current_step": "adaptive_questions"
            }
    
    async def _handle_adaptive_questions_step(self, session: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Handle adaptive questions step."""
        language = session.get("language", "en")
        session_id = UUID(session["id"])
        
        try:
            # Check if we need to generate questions
            additional_questions = session.get("additional_questions_data", {})
            questions_asked = additional_questions.get("questions_asked", 0)
            
            # If first time, generate questions
            if questions_asked == 0:
                questions = await self._generate_adaptive_questions(session, language)
                
                if questions and len(questions.get("questions", [])) > 0:
                    additional_questions["questions"] = questions.get("questions", [])
                    additional_questions["questions_asked"] = 0
                    
                    self.db_service.update_session(session_id, {
                        "additional_questions_data": additional_questions
                    })
                    
                    # Ask first question
                    first_question = questions["questions"][0]
                    return {
                        "content": f"{first_question['question']}\n\n{first_question.get('context', '')}",
                        "current_step": "adaptive_questions",
                        "metadata": {
                            "question_id": first_question["id"],
                            "total_questions": len(questions["questions"]),
                            "current_question": 1
                        }
                    }
            
            # Store answer and move to next question
            # For now, move to CV generation after first question answered
            return {
                "content": await self._generate_cv_generation_intro(language),
                "current_step": "cv_generation",
                "metadata": {"questions_completed": True}
            }
            
        except Exception as e:
            logger.error(f"Error handling adaptive questions: {e}")
            return {
                "content": await self._generate_cv_generation_intro(language),
                "current_step": "cv_generation"
            }
    
    async def _handle_cv_generation_step(self, session: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Handle CV generation step - generate optimized CVs."""
        language = session.get("language", "en")
        session_id = UUID(session["id"])
        
        try:
            # Get CV and job data
            cv_data = session.get("cv_data", {})
            job_data = session.get("job_opportunity_data", {})
            
            if not cv_data or not job_data:
                return {
                    "content": await self._generate_error_message(language),
                    "current_step": "cv_generation"
                }
            
            # IMPORTANT: Convert CV to Markdown before sending to AI
            # This ensures all information is preserved and properly formatted
            from utils.file_processor import FileProcessor
            cv_text = cv_data.get("extracted_text", "")
            cv_markdown = FileProcessor.text_to_markdown(cv_text) if cv_text else ""
            
            # Generate ATS-friendly CV
            ats_cv = await self._generate_ats_cv(
                original_cv=cv_markdown,  # Send Markdown, not raw text
                job_requirements=job_data,
                language=language
            )
            
            # Generate human-friendly CV
            human_cv = await self._generate_human_cv(
                original_cv=cv_markdown,  # Send Markdown, not raw text
                job_requirements=job_data,
                language=language
            )
            
            # Store CV versions
            if ats_cv:
                self.db_service.create_cv_version(
                    session_id=session_id,
                    version_type="ats_friendly",
                    cv_content=ats_cv.get("cv_content", ""),
                    structured_data=ats_cv.get("structured_data", {}),
                    ats_score=ats_cv.get("ats_score"),
                    keyword_match_score=ats_cv.get("keyword_match_score"),
                    language=language
                )
            
            if human_cv:
                self.db_service.create_cv_version(
                    session_id=session_id,
                    version_type="human_friendly",
                    cv_content=human_cv.get("cv_content", ""),
                    structured_data=human_cv.get("structured_data", {}),
                    language=language
                )
            
            # Move to interview prep
            return {
                "content": await self._generate_interview_prep_intro(language),
                "current_step": "interview_prep",
                "metadata": {"cvs_generated": True, "ats_available": bool(ats_cv), "human_available": bool(human_cv)}
            }
            
        except Exception as e:
            logger.error(f"Error generating CVs: {e}")
            return {
                "content": await self._generate_error_message(language),
                "current_step": "cv_generation"
            }
    
    async def _handle_interview_prep_step(self, session: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Handle interview preparation step."""
        language = session.get("language", "en")
        session_id = UUID(session["id"])
        
        try:
            # Get CV and job data
            cv_data = session.get("cv_data", {})
            job_data = session.get("job_opportunity_data", {})
            
            if not cv_data or not job_data:
                return {
                    "content": await self._generate_error_message(language),
                    "current_step": "interview_prep"
                }
            
            # IMPORTANT: Convert CV to Markdown before sending to AI
            from utils.file_processor import FileProcessor
            cv_text = cv_data.get("extracted_text", "")
            cv_markdown = FileProcessor.text_to_markdown(cv_text) if cv_text else ""
            
            # Generate interview prep
            interview_prep = await self._generate_interview_prep(
                cv_summary=cv_markdown,  # Send Markdown, not raw text
                job_opportunity=job_data,
                experience_highlights=session.get("profile_data", {}),
                language=language
            )
            
            if interview_prep:
                # Store interview prep
                self.db_service.create_interview_prep(
                    session_id=session_id,
                    likely_questions=interview_prep.get("likely_questions", []),
                    suggested_answers=interview_prep.get("suggested_answers", []),
                    key_stories=interview_prep.get("key_stories", []),
                    preparation_summary=interview_prep.get("preparation_summary", ""),
                    questions_to_ask=interview_prep.get("questions_to_ask", []),
                    language=language
                )
                
                # Move to score step
                return {
                    "content": await self._generate_score_intro(language),
                    "current_step": "score_and_recommendations",
                    "metadata": {"interview_prep_ready": True}
                }
            else:
                return {
                    "content": await self._generate_score_intro(language),
                    "current_step": "score_and_recommendations"
                }
                
        except Exception as e:
            logger.error(f"Error generating interview prep: {e}")
            return {
                "content": await self._generate_score_intro(language),
                "current_step": "score_and_recommendations"
            }
    
    async def _handle_score_step(self, session: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Handle score and recommendations step."""
        language = session.get("language", "en")
        session_id = UUID(session["id"])
        
        try:
            # Get CV and job data
            cv_data = session.get("cv_data", {})
            job_data = session.get("job_opportunity_data", {})
            
            if not cv_data or not job_data:
                # Complete without score
                self.db_service.complete_session(session_id)
                return {
                    "content": await self._generate_completion_message(language),
                    "current_step": "completed"
                }
            
            # IMPORTANT: Convert CV to Markdown before sending to AI
            # (Already converted above for interview prep, reuse if available)
            if 'cv_markdown' not in locals():
                from utils.file_processor import FileProcessor
                cv_text = cv_data.get("extracted_text", "")
                cv_markdown = FileProcessor.text_to_markdown(cv_text) if cv_text else ""
            
            # Calculate employability score
            score_data = await self._calculate_employability_score(
                cv_summary=cv_markdown,  # Send Markdown, not raw text
                job_requirements=job_data,
                language=language
            )
            
            if score_data:
                # Store score
                self.db_service.create_employability_score(
                    session_id=session_id,
                    overall_score=score_data.get("overall_score", 0),
                    technical_skills_score=score_data.get("technical_skills_score"),
                    experience_score=score_data.get("experience_score"),
                    communication_score=score_data.get("communication_score"),
                    strengths=score_data.get("strengths", []),
                    weaknesses=score_data.get("weaknesses", []),
                    recommendations=score_data.get("recommendations", [])
                )
            
            # Complete the session
            self.db_service.complete_session(session_id)
            
            # Generate completion message with score
            completion_msg = await self._generate_completion_message_with_score(language, score_data)
            
            return {
                "content": completion_msg,
                "current_step": "completed",
                "metadata": {"score_calculated": bool(score_data), "score": score_data}
            }
            
        except Exception as e:
            logger.error(f"Error calculating score: {e}")
            # Complete anyway
            self.db_service.complete_session(session_id)
            return {
                "content": await self._generate_completion_message(language),
                "current_step": "completed"
            }
    
    async def _generate_generic_response(self, language: str) -> str:
        """Generate a generic response when specific handler is not yet implemented."""
        messages = {
            "en": "I'm processing your request. This feature is being implemented...",
            "pt": "Estou a processar o seu pedido. Esta funcionalidade está a ser implementada...",
            "fr": "Je traite votre demande. Cette fonctionnalité est en cours d'implémentation...",
            "es": "Estoy procesando tu solicitud. Esta función se está implementando..."
        }
        
        return messages.get(language, messages["en"])
    
    async def _generate_clarification_message(self, language: str, context: str) -> str:
        """Generate message asking for clarification."""
        messages = {
            "en": f"I need more information about your {context}. Could you provide more details?",
            "pt": f"Preciso de mais informações sobre o seu {context}. Poderia fornecer mais detalhes?",
            "fr": f"J'ai besoin de plus d'informations sur votre {context}. Pourriez-vous fournir plus de détails ?",
            "es": f"Necesito más información sobre tu {context}. ¿Podrías proporcionar más detalles?"
        }
        
        return messages.get(language, messages["en"])
    
    async def _generate_error_message(self, language: str) -> str:
        """Generate error message."""
        messages = {
            "en": "I encountered an error processing your request. Please try again or rephrase your message.",
            "pt": "Encontrei um erro ao processar o seu pedido. Por favor, tente novamente ou reformule a sua mensagem.",
            "fr": "J'ai rencontré une erreur lors du traitement de votre demande. Veuillez réessayer ou reformuler votre message.",
            "es": "Encontré un error al procesar tu solicitud. Por favor intenta de nuevo o reformula tu mensaje."
        }
        
        return messages.get(language, messages["en"])
    
    async def _generate_completion_message(self, language: str) -> str:
        """Generate completion message."""
        messages = {
            "en": "Perfect! I've completed your CV preparation. You can now review the generated CV, interview preparation materials, and recommendations. Good luck with your application!",
            "pt": "Perfeito! Completei a preparação do seu CV. Pode agora revisar o CV gerado, os materiais de preparação para entrevista e as recomendações. Boa sorte com a sua candidatura!",
            "fr": "Parfait ! J'ai terminé la préparation de votre CV. Vous pouvez maintenant examiner le CV généré, les matériaux de préparation à l'entretien et les recommandations. Bonne chance avec votre candidature !",
            "es": "¡Perfecto! He completado la preparación de tu CV. Ahora puedes revisar el CV generado, los materiales de preparación para la entrevista y las recomendaciones. ¡Buena suerte con tu aplicación!"
        }
        
        return messages.get(language, messages["en"])
    
    # =========================================================================
    # Advanced Feature Implementations
    # =========================================================================
    
    async def _analyze_job_opportunity(
        self,
        job_text: str,
        language: str,
        session: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Analyze job opportunity using AI."""
        try:
            # IMPORTANT: Convert job posting to Markdown before sending to AI
            # This ensures all information is preserved and properly formatted
            from utils.file_processor import FileProcessor
            job_markdown = FileProcessor.text_to_markdown(job_text) if job_text else ""
            
            # Use existing job posting normalization
            template = await get_prompt("job_posting_normalization", language)
            
            ai_request = AIRequest(
                prompt_type=PromptType.JOB_POSTING_NORMALIZATION,
                template=template,
                variables={"job_posting_text": job_markdown, "enrichment_context": ""},  # Send Markdown
                language=language
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            if response.success and response.data:
                return response.data
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing job opportunity: {e}")
            return None
    
    async def _assess_job_risk(
        self,
        job_data: Dict[str, Any],
        language: str
    ) -> Optional[Dict[str, Any]]:
        """Assess job opportunity risk and quality."""
        try:
            template = await get_prompt("chatbot_job_risk_assessment", language)
            
            ai_request = AIRequest(
                prompt_type=PromptType.CHATBOT_JOB_RISK_ASSESSMENT,
                template=template,
                variables={
                    "job_posting": json.dumps(job_data),
                    "company_info": ""
                },
                language=language
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            if response.success and response.data:
                return response.data
            
            return None
            
        except Exception as e:
            logger.error(f"Error assessing job risk: {e}")
            return None
    
    async def _generate_digital_footprint_message(self, language: str) -> str:
        """Generate message about digital footprint analysis."""
        messages = {
            "en": "Now I'll analyze your digital footprint if you've provided links to LinkedIn, GitHub, or portfolio. I'll check for consistency with your CV and provide recommendations.",
            "pt": "Agora vou analisar a sua pegada digital se forneceu links para LinkedIn, GitHub ou portefólio. Vou verificar a consistência com o seu CV e fornecer recomendações.",
            "fr": "Maintenant, j'analyserai votre empreinte numérique si vous avez fourni des liens vers LinkedIn, GitHub ou un portfolio. Je vérifierai la cohérence avec votre CV et fournirai des recommandations.",
            "es": "Ahora analizaré tu huella digital si has proporcionado enlaces a LinkedIn, GitHub o portfolio. Verificaré la consistencia con tu CV y proporcionaré recomendaciones."
        }
        return messages.get(language, messages["en"])
    
    async def _analyze_digital_footprint(
        self,
        session_id: UUID,
        cv_summary: str,
        links: Dict[str, str],
        language: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze digital footprint from links."""
        try:
            # For now, use AI analysis based on CV only
            # In production, would fetch actual profile data from APIs
            template = await get_prompt("chatbot_digital_footprint_analysis", language)
            
            ai_request = AIRequest(
                prompt_type=PromptType.CHATBOT_DIGITAL_FOOTPRINT_ANALYSIS,
                template=template,
                variables={
                    "cv_summary": cv_summary[:2000],  # Limit length
                    "linkedin_data": links.get("linkedin", "") or "",
                    "github_data": links.get("github", "") or "",
                    "portfolio_data": links.get("portfolio", "") or ""
                },
                language=language
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            if response.success and response.data:
                return response.data
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing digital footprint: {e}")
            return None
    
    async def _generate_adaptive_questions_intro(
        self,
        language: str,
        footprint_analysis: Optional[Dict[str, Any]]
    ) -> str:
        """Generate intro message for adaptive questions."""
        messages = {
            "en": "Based on your CV and the job opportunity, I have some questions to help optimize your profile. Let's start:",
            "pt": "Com base no seu CV e na oportunidade de emprego, tenho algumas perguntas para ajudar a otimizar o seu perfil. Vamos começar:",
            "fr": "Basé sur votre CV et l'opportunité d'emploi, j'ai quelques questions pour aider à optimiser votre profil. Commençons :",
            "es": "Basándome en tu CV y la oportunidad de trabajo, tengo algunas preguntas para ayudar a optimizar tu perfil. Empecemos:"
        }
        return messages.get(language, messages["en"])
    
    async def _generate_adaptive_questions(
        self,
        session: Dict[str, Any],
        language: str
    ) -> Optional[Dict[str, Any]]:
        """Generate adaptive questions based on CV and job."""
        try:
            cv_data = session.get("cv_data", {})
            job_data = session.get("job_opportunity_data", {})
            
            if not cv_data or not job_data:
                return None
            
            template = await get_prompt("chatbot_question_generation", language)
            
            # IMPORTANT: Convert CV to Markdown before sending to AI
            from utils.file_processor import FileProcessor
            cv_text_raw = cv_data.get("extracted_text", "")
            cv_markdown = FileProcessor.text_to_markdown(cv_text_raw) if cv_text_raw else ""
            
            # Identify gaps (simplified for now) - use raw text for simple search
            gaps = []
            required_skills = job_data.get("required_skills", [])
            cv_text_lower = cv_text_raw.lower()
            
            for skill in required_skills[:5]:  # Limit to 5 skills
                if skill.lower() not in cv_text_lower:
                    gaps.append(f"Missing skill: {skill}")
            
            ai_request = AIRequest(
                prompt_type=PromptType.CHATBOT_QUESTION_GENERATION,
                template=template,
                variables={
                    "cv_summary": cv_markdown[:1000] if cv_markdown else "",  # Send Markdown, not raw text
                    "job_requirements": json.dumps(job_data),
                    "gaps": "\n".join(gaps)
                },
                language=language
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            if response.success and response.data:
                return response.data
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating adaptive questions: {e}")
            return None
    
    async def _generate_cv_generation_intro(self, language: str) -> str:
        """Generate intro message for CV generation."""
        messages = {
            "en": "Great! Now I'll generate optimized versions of your CV - one ATS-friendly for applicant tracking systems, and one human-friendly for recruiters. This may take a moment...",
            "pt": "Ótimo! Agora vou gerar versões otimizadas do seu CV - uma compatível com ATS para sistemas de rastreamento de candidatos, e outra amigável para recrutadores. Isto pode demorar um momento...",
            "fr": "Excellent ! Je vais maintenant générer des versions optimisées de votre CV - une compatible ATS pour les systèmes de suivi des candidats, et une conviviale pour les recruteurs. Cela peut prendre un moment...",
            "es": "¡Genial! Ahora generaré versiones optimizadas de tu CV - una compatible con ATS para sistemas de seguimiento de candidatos, y otra amigable para reclutadores. Esto puede tomar un momento..."
        }
        return messages.get(language, messages["en"])
    
    async def _generate_ats_cv(
        self,
        original_cv: str,
        job_requirements: Dict[str, Any],
        language: str
    ) -> Optional[Dict[str, Any]]:
        """Generate ATS-friendly CV."""
        try:
            template = await get_prompt("chatbot_cv_generation_ats", language)
            
            ai_request = AIRequest(
                prompt_type=PromptType.CHATBOT_CV_GENERATION,
                template=template,
                variables={
                    "original_cv": original_cv[:4000],  # Limit length
                    "job_requirements": json.dumps(job_requirements)
                },
                language=language,
                temperature=0.4,
                max_tokens=3000
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            if response.success and response.data:
                return response.data
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating ATS CV: {e}")
            return None
    
    async def _generate_human_cv(
        self,
        original_cv: str,
        job_requirements: Dict[str, Any],
        language: str
    ) -> Optional[Dict[str, Any]]:
        """Generate human-friendly CV."""
        try:
            template = await get_prompt("chatbot_cv_generation_human", language)
            
            ai_request = AIRequest(
                prompt_type=PromptType.CHATBOT_CV_GENERATION,
                template=template,
                variables={
                    "original_cv": original_cv[:4000],
                    "job_requirements": json.dumps(job_requirements)
                },
                language=language,
                temperature=0.6,
                max_tokens=3000
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            if response.success and response.data:
                return response.data
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating human CV: {e}")
            return None
    
    async def _generate_interview_prep_intro(self, language: str) -> str:
        """Generate intro message for interview prep."""
        messages = {
            "en": "Perfect! Your optimized CVs are ready. Now let me prepare interview materials tailored to this job opportunity...",
            "pt": "Perfeito! Os seus CVs otimizados estão prontos. Agora deixe-me preparar materiais de entrevista adaptados a esta oportunidade de emprego...",
            "fr": "Parfait ! Vos CV optimisés sont prêts. Maintenant, laissez-moi préparer des matériaux d'entretien adaptés à cette opportunité d'emploi...",
            "es": "¡Perfecto! Tus CVs optimizados están listos. Ahora déjame preparar materiales de entrevista adaptados a esta oportunidad de trabajo..."
        }
        return messages.get(language, messages["en"])
    
    async def _generate_interview_prep(
        self,
        cv_summary: str,
        job_opportunity: Dict[str, Any],
        experience_highlights: Dict[str, Any],
        language: str
    ) -> Optional[Dict[str, Any]]:
        """Generate interview preparation materials."""
        try:
            template = await get_prompt("chatbot_interview_prep", language)
            
            ai_request = AIRequest(
                prompt_type=PromptType.CHATBOT_INTERVIEW_PREP,
                template=template,
                variables={
                    "cv_summary": cv_summary[:2000],
                    "job_opportunity": json.dumps(job_opportunity),
                    "experience_highlights": json.dumps(experience_highlights)
                },
                language=language,
                temperature=0.5,
                max_tokens=2500
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            if response.success and response.data:
                return response.data
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating interview prep: {e}")
            return None
    
    async def _generate_score_intro(self, language: str) -> str:
        """Generate intro message for score calculation."""
        messages = {
            "en": "Excellent! Your interview preparation is ready. Now let me calculate your employability score for this opportunity...",
            "pt": "Excelente! A sua preparação para entrevista está pronta. Agora deixe-me calcular a sua pontuação de empregabilidade para esta oportunidade...",
            "fr": "Excellent ! Votre préparation à l'entretien est prête. Maintenant, laissez-moi calculer votre score d'employabilité pour cette opportunité...",
            "es": "¡Excelente! Tu preparación para la entrevista está lista. Ahora déjame calcular tu puntuación de empleabilidad para esta oportunidad..."
        }
        return messages.get(language, messages["en"])
    
    async def _calculate_employability_score(
        self,
        cv_summary: str,
        job_requirements: Dict[str, Any],
        language: str
    ) -> Optional[Dict[str, Any]]:
        """Calculate employability score."""
        try:
            template = await get_prompt("chatbot_employability_score", language)
            
            ai_request = AIRequest(
                prompt_type=PromptType.CHATBOT_EMPLOYABILITY_SCORE,
                template=template,
                variables={
                    "cv_summary": cv_summary[:2000],
                    "job_requirements": json.dumps(job_requirements),
                    "structured_analysis": ""
                },
                language=language,
                temperature=0.4,
                max_tokens=2000
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            if response.success and response.data:
                return response.data
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating employability score: {e}")
            return None
    
    async def _generate_completion_message_with_score(
        self,
        language: str,
        score_data: Optional[Dict[str, Any]]
    ) -> str:
        """Generate completion message with score."""
        base_msg = await self._generate_completion_message(language)
        
        if not score_data:
            return base_msg
        
        overall_score = score_data.get("overall_score", 0)
        explanation = score_data.get("explanation", "")
        
        score_msgs = {
            "en": f"\n\nYour employability score: {overall_score}/100\n\n{explanation}",
            "pt": f"\n\nA sua pontuação de empregabilidade: {overall_score}/100\n\n{explanation}",
            "fr": f"\n\nVotre score d'employabilité : {overall_score}/100\n\n{explanation}",
            "es": f"\n\nTu puntuación de empleabilidad: {overall_score}/100\n\n{explanation}"
        }
        
        return base_msg + score_msgs.get(language, score_msgs["en"])
    
    # =========================================================================
    # Conversational AI Integration
    # =========================================================================
    
    async def _generate_conversational_response(
        self,
        session: Dict[str, Any],
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        language: str
    ) -> Optional[str]:
        """
        Generate conversational response using AI providers with fallback chain.
        
        Uses AIManager.execute() which automatically respects the fallback chain
        configured in the database (app_settings table).
        """
        try:
            # Build system prompt based on session context
            system_prompt = self._build_system_prompt(session, language)
            
            # Build conversation context from history (last 10 messages for context)
            recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
            
            # Get labels based on language
            labels = {
                "en": {"history": "Conversation history:", "user": "User", "assistant": "Assistant"},
                "pt": {"history": "Histórico da conversa:", "user": "Utilizador", "assistant": "Assistente"},
                "fr": {"history": "Historique de la conversation:", "user": "Utilisateur", "assistant": "Assistant"},
                "es": {"history": "Historial de la conversación:", "user": "Usuario", "assistant": "Asistente"}
            }
            lang_labels = labels.get(language, labels["en"])
            
            # Build conversational prompt with full context
            conversation_parts = []
            
            # Add system instructions
            conversation_parts.append(f"{system_prompt}\n\n")
            
            # Add conversation history
            if recent_history:
                conversation_parts.append(f"{lang_labels['history']}\n")
                for msg in recent_history:
                    role_label = lang_labels["assistant"] if msg.get("role") == "bot" else lang_labels["user"]
                    content = msg.get("content", "").strip()
                    if content:
                        conversation_parts.append(f"{role_label}: {content}\n")
                conversation_parts.append("\n")
            
            # Add current user message
            conversation_parts.append(f"{lang_labels['user']}: {user_message}\n\n")
            conversation_parts.append(f"{lang_labels['assistant']}:")
            
            # Build final prompt
            conversational_prompt = "".join(conversation_parts)
            
            # Use AIManager.execute() - this automatically respects fallback chain from database
            # Don't specify provider_name so it uses the configured fallback chain
            ai_request = AIRequest(
                prompt_type=PromptType.CHATBOT_PROFILE_EXTRACTION,  # Use chatbot prompt type
                template=conversational_prompt,
                variables={},  # No variables needed for conversational prompt
                language=language,
                temperature=0.7,  # More conversational temperature
                max_tokens=1000
            )
            
            # Execute using AI manager - it will automatically use fallback chain from database
            logger.info(f"[Chatbot] Generating conversational response using AI providers with fallback chain")
            response = await self.ai_manager.execute(
                request=ai_request,
                provider_name=None,  # None = use fallback chain from database
                model_name=None,  # None = use model from fallback chain config
                enable_fallback=True  # Enable fallback between providers
            )
            
            if response.success:
                # Extract response text
                if response.raw_text:
                    logger.info(f"[Chatbot] Response from {response.provider}/{response.model or 'default'}")
                    return response.raw_text.strip()
                elif response.data:
                    # Try to extract text from data dict
                    if isinstance(response.data, str):
                        return response.data.strip()
                    elif isinstance(response.data, dict):
                        text = response.data.get("text") or response.data.get("content") or response.data.get("message")
                        if text:
                            return str(text).strip()
            
            # If no valid response, return error message
            logger.error(f"[Chatbot] AI request failed: {response.error}")
            return None
            
        except Exception as e:
            logger.error(f"Error generating conversational response: {e}", exc_info=True)
            return None
    
    async def _process_personal_links(
        self,
        session_id: UUID,
        session: Dict[str, Any],
        user_message: str
    ) -> None:
        """
        Process personal links (LinkedIn, GitHub, Portfolio) from user message.
        Detects URLs and enriches candidate profile with Brave Search.
        """
        try:
            # Extract URLs from message
            url_pattern = r'(https?://[^\s]+|www\.[^\s]+|linkedin\.com/[^\s]+|github\.com/[^\s]+)'
            urls = re.findall(url_pattern, user_message, re.IGNORECASE)
            
            if not urls:
                return
            
            # Get profile data
            profile_data = session.get("profile_data", {})
            links = profile_data.get("links", {})
            name = profile_data.get("name") or session.get("cv_data", {}).get("structured_data", {}).get("personal_info", {}).get("name") or "Candidate"
            
            # Categorize URLs
            for url in urls:
                # Normalize URL
                if not url.startswith("http"):
                    url = "https://" + url
                
                url_lower = url.lower()
                
                # Detect and store link type
                if "linkedin.com/in" in url_lower or "linkedin.com/people" in url_lower:
                    links["linkedin"] = url
                elif "github.com" in url_lower:
                    links["github"] = url
                elif "linkedin.com/company" in url_lower:
                    # This is a company LinkedIn, not personal - skip for personal links
                    continue
                else:
                    # Assume it's a portfolio/personal website
                    if not links.get("portfolio"):
                        links["portfolio"] = url
            
            # Update profile data with links
            profile_data["links"] = links
            
            # Enrich candidate information using Brave Search if we have links
            if self.brave_service and self.brave_service.is_enabled() and (links.get("linkedin") or links.get("github") or links.get("portfolio")):
                logger.info(f"[Chatbot] Enriching candidate profile with Brave Search using provided links")
                try:
                    # Use Brave Search to enrich candidate
                    enrichment = await self.brave_service.enrich_candidate(
                        candidate_name=name,
                        additional_keywords=[profile_data.get("location", "")] if profile_data.get("location") else None
                    )
                except Exception as e:
                    logger.warning(f"[Chatbot] Failed to enrich candidate profile: {e}")
                    enrichment = None

                if enrichment:
                    # Update profile with enriched data
                    if enrichment.linkedin_profile and not links.get("linkedin"):
                        links["linkedin"] = enrichment.linkedin_profile
                    if enrichment.github_profile and not links.get("github"):
                        links["github"] = enrichment.github_profile
                    if enrichment.portfolio_url and not links.get("portfolio"):
                        links["portfolio"] = enrichment.portfolio_url
                    
                    # Store enrichment data in session
                    candidate_enrichment = session.get("candidate_enrichment", {})
                    candidate_enrichment.update({
                        "linkedin_profile": enrichment.linkedin_profile,
                        "github_profile": enrichment.github_profile,
                        "portfolio_url": enrichment.portfolio_url,
                        "professional_summary": enrichment.professional_summary,
                        "publications": enrichment.publications,
                        "awards": enrichment.awards,
                        "ai_summary": enrichment.ai_summary
                    })
                    
                    profile_data["links"] = links
                    
                    # Update session
                    self.db_service.update_session(session_id, {
                        "profile_data": profile_data,
                        "candidate_enrichment": candidate_enrichment
                    })
                    
                    logger.info(f"[Chatbot] Successfully enriched candidate profile")

                    # Persist structured candidate profile using AI (best-effort)
                    try:
                        language = session.get("language", "en")
                        cv_struct = session.get("cv_data", {}).get("structured_data", {})

                        # Build candidate structuring prompt
                        template = await get_prompt("structure_candidate_enrichment", language)
                        ai_request = AIRequest(
                            prompt_type=PromptType.STRUCTURE_CANDIDATE_ENRICHMENT,
                            template=template,
                            variables={
                                "cv_data": json.dumps(cv_struct or {}),
                                "brave_enrichment_data": json.dumps(candidate_enrichment or {}),
                                "additional_context": "",
                            },
                            language=language,
                            temperature=0.2,
                            max_tokens=2200,
                        )
                        struct_resp = await self.ai_manager.execute(ai_request)
                        structured_candidate = struct_resp.data if (struct_resp and struct_resp.success) else None

                        # Risk analysis for candidate social media
                        risk_structured = None
                        try:
                            links_for_risk = profile_data.get("links", {})
                            risk_template = await get_prompt("analyze_candidate_social_media_risk", language)
                            risk_req = AIRequest(
                                prompt_type=PromptType.ANALYZE_CANDIDATE_SOCIAL_MEDIA_RISK,
                                template=risk_template,
                                variables={
                                    "cv_data": json.dumps(cv_struct or {}),
                                    "brave_enrichment_data": json.dumps(candidate_enrichment or {}),
                                    "social_media_links": json.dumps(links_for_risk or {}),
                                    "additional_context": "",
                                },
                                language=language,
                                temperature=0.3,
                                max_tokens=1800,
                            )
                            risk_resp = await self.ai_manager.execute(risk_req)
                            if risk_resp and risk_resp.success:
                                risk_structured = risk_resp.data
                        except Exception as e:
                            logger.warning(f"[Chatbot] Candidate risk analysis failed: {e}")

                        # Persist profile (requires a candidate_id; if not present, skip persistence)
                        try:
                            candidate_id = session.get("candidate_id")
                            if candidate_id:
                                sc = structured_candidate or {}
                                self.candidate_profile_service.upsert_candidate_profile(
                                    candidate_id=UUID(candidate_id),
                                    full_name=(profile_data.get("name") or sc.get("normalized_name") or name),
                                    normalized_name=(sc.get("normalized_name") if isinstance(sc, dict) else None),
                                    basic_info=(sc.get("basic_info") if isinstance(sc, dict) else None),
                                    contact_info=(sc.get("contact_info") if isinstance(sc, dict) else None),
                                    professional_summary=profile_data.get("summary"),
                                    professional_summary_structured=(sc.get("professional_summary_structured") if isinstance(sc, dict) else None),
                                    work_experience=(sc.get("work_experience") if isinstance(sc, dict) else None),
                                    education=(sc.get("education") if isinstance(sc, dict) else None),
                                    skills=(sc.get("skills") if isinstance(sc, dict) else None),
                                    projects=(sc.get("projects") if isinstance(sc, dict) else None),
                                    publications=(sc.get("publications") if isinstance(sc, dict) else None),
                                    awards=(sc.get("awards") if isinstance(sc, dict) else None),
                                    career_preferences=(sc.get("career_preferences") if isinstance(sc, dict) else None),
                                    ai_summary=candidate_enrichment.get("ai_summary"),
                                    ai_insights=(sc.get("ai_insights") if isinstance(sc, dict) else None),
                                    social_media_risk_analysis=risk_structured or (sc.get("social_media_risk_analysis") if isinstance(sc, dict) else None),
                                    raw_brave_data={
                                        "candidate_enrichment": candidate_enrichment
                                    },
                                    source_cv_id=None,
                                    source_session_id=session_id,
                                    enrichment_source="chatbot",
                                )
                        except Exception as e:
                            logger.warning(f"[Chatbot] Failed to persist candidate profile: {e}")
                    except Exception as e:
                        logger.warning(f"[Chatbot] Failed to structure/persist candidate profile: {e}")
            else:
                # Just update links if no enrichment
                self.db_service.update_session(session_id, {
                    "profile_data": profile_data
                })
                
        except Exception as e:
            logger.error(f"Error processing personal links: {e}", exc_info=True)
    
    async def _process_company_links(
        self,
        session_id: UUID,
        session: Dict[str, Any],
        user_message: str
    ) -> None:
        """
        Process company links/information from user message.
        Detects URLs and company names, enriches with Brave Search.
        """
        try:
            # Get CV data to find companies mentioned
            cv_data = session.get("cv_data", {})
            structured_cv_data = cv_data.get("structured_data", {})
            experience = structured_cv_data.get("experience") or structured_cv_data.get("work_experience") or []
            
            if not experience:
                return
            
            # Get or create companies enrichment data
            companies_enrichment = session.get("companies_enrichment", {})
            
            # Extract URLs from message
            url_pattern = r'(https?://[^\s]+|www\.[^\s]+|linkedin\.com/[^\s]+)'
            urls = re.findall(url_pattern, user_message, re.IGNORECASE)
            
            # Normalize and categorize URLs
            linkedin_urls = []
            website_urls = []
            
            for url in urls:
                # Normalize URL
                if not url.startswith("http"):
                    url = "https://" + url
                
                # Categorize URL
                if "linkedin.com/company" in url.lower():
                    linkedin_urls.append(url)
                else:
                    website_urls.append(url)
            
            # Try to match URLs to companies mentioned in user message or CV
            # Strategy: Match by company name mention in message or by order
            for exp in experience:
                if isinstance(exp, dict):
                    company_name = exp.get("company") or exp.get("employer") or exp.get("organization")
                    if not company_name:
                        continue
                    
                    # Initialize company data if not exists
                    if company_name not in companies_enrichment:
                        companies_enrichment[company_name] = {
                            "company_name": company_name,
                            "website": None,
                            "linkedin": None,
                            "email": None,
                            "enrichment_data": None
                        }
                    
                    company_name_lower = company_name.lower()
                    user_message_lower = user_message.lower()
                    
                    # Check if company name is mentioned in message (for link matching)
                    company_mentioned = company_name_lower in user_message_lower or any(
                        word in user_message_lower for word in company_name_lower.split() if len(word) > 3
                    )
                    
                    # Try to match LinkedIn URL (prefer LinkedIn company pages)
                    if linkedin_urls and company_mentioned:
                        # Use first LinkedIn URL if company is mentioned
                        if not companies_enrichment[company_name]["linkedin"]:
                            companies_enrichment[company_name]["linkedin"] = linkedin_urls[0]
                            linkedin_urls = linkedin_urls[1:]  # Remove used URL
                    
                    # Try to match website URL
                    if website_urls and company_mentioned:
                        # Use first website URL if company is mentioned
                        if not companies_enrichment[company_name]["website"]:
                            companies_enrichment[company_name]["website"] = website_urls[0]
                            website_urls = website_urls[1:]  # Remove used URL
                    
                    # If no direct match but we have URLs, use them in order
                    if not companies_enrichment[company_name]["linkedin"] and linkedin_urls:
                        companies_enrichment[company_name]["linkedin"] = linkedin_urls[0]
                        linkedin_urls = linkedin_urls[1:]
                    
                    if not companies_enrichment[company_name]["website"] and website_urls:
                        companies_enrichment[company_name]["website"] = website_urls[0]
                        website_urls = website_urls[1:]
                    
                    # Use direct links for enrichment
                    website = companies_enrichment[company_name].get("website")
                    linkedin = companies_enrichment[company_name].get("linkedin")
                    email = companies_enrichment[company_name].get("email")
                    
                    # ONLY enrich if we have explicit links OR company is explicitly mentioned in message
                    # Don't auto-enrich all companies from CV
                    has_explicit_links = website or linkedin
                    is_explicitly_mentioned = company_mentioned and (
                        "linkedin.com/company" in user_message.lower() or
                        any(word in user_message.lower() for word in ["website", "site", "empresa", "company"])
                    )
                    
                    # Enrich company information using Brave Search ONLY with direct links or explicit mention
                    if self.brave_service and self.brave_service.is_enabled() and (has_explicit_links or is_explicitly_mentioned):
                        try:
                            logger.info(f"[Chatbot] Enriching company '{company_name}' with Brave Search using provided links: website={bool(website)}, linkedin={bool(linkedin)}")
                            
                            # Use new method that takes direct links
                            if website or linkedin:
                                enrichment = await self.brave_service.enrich_company_from_links(
                                    company_name=company_name,
                                    website_url=website,
                                    linkedin_url=linkedin,
                                    email=email
                                )
                            else:
                                # Fallback to generic search if no links but company mentioned
                                enrichment = await self.brave_service.enrich_company(
                                    company_name=company_name,
                                    additional_context=None
                                )
                            
                            if enrichment:
                                companies_enrichment[company_name]["enrichment_data"] = {
                                    "website": enrichment.website or website,
                                    "description": enrichment.description,
                                    "industry": enrichment.industry,
                                    "size": enrichment.size,
                                    "location": enrichment.location,
                                    "recent_news": enrichment.recent_news[:3] if enrichment.recent_news else [],
                                    "ai_summary": enrichment.ai_summary
                                }
                                # Update links if Brave found better ones
                                if enrichment.website and not companies_enrichment[company_name]["website"]:
                                    companies_enrichment[company_name]["website"] = enrichment.website
                                if enrichment.social_media.get("linkedin") and not companies_enrichment[company_name]["linkedin"]:
                                    companies_enrichment[company_name]["linkedin"] = enrichment.social_media["linkedin"]
                                
                                logger.info(f"[Chatbot] Successfully enriched company '{company_name}'")

                                # Persist structured company profile using AI to match DB schema
                                try:
                                    language = session.get("language", "en")
                                    # Build company structuring prompt
                                    template = await get_prompt("structure_company_enrichment", language)
                                    ai_request = AIRequest(
                                        prompt_type=PromptType.STRUCTURE_COMPANY_ENRICHMENT,
                                        template=template,
                                        variables={
                                            "brave_enrichment_data": json.dumps(companies_enrichment[company_name]["enrichment_data"]),
                                            "additional_context": f"Website: {companies_enrichment[company_name].get('website') or ''}\nLinkedIn: {companies_enrichment[company_name].get('linkedin') or ''}",
                                        },
                                        language=language,
                                        temperature=0.2,
                                        max_tokens=1800,
                                    )
                                    struct_resp = await self.ai_manager.execute(ai_request)
                                    structured_company = struct_resp.data if (struct_resp and struct_resp.success) else None

                                    # Risk analysis for company social media/reputation
                                    risk_structured = None
                                    try:
                                        risk_template = await get_prompt("analyze_company_social_media_risk", language)
                                        risk_req = AIRequest(
                                            prompt_type=PromptType.ANALYZE_COMPANY_SOCIAL_MEDIA_RISK,
                                            template=risk_template,
                                            variables={
                                                "company_name": company_name,
                                                "brave_enrichment_data": json.dumps(companies_enrichment[company_name]["enrichment_data"]),
                                                "recent_news": json.dumps(enrichment.recent_news[:5] if enrichment.recent_news else []),
                                                "additional_context": "",
                                            },
                                            language=language,
                                            temperature=0.3,
                                            max_tokens=1600,
                                        )
                                        risk_resp = await self.ai_manager.execute(risk_req)
                                        if risk_resp and risk_resp.success:
                                            risk_structured = risk_resp.data
                                    except Exception as e:
                                        logger.warning(f"[Chatbot] Company risk analysis failed: {e}")

                                    # Persist profile
                                    if structured_company or risk_structured:
                                        sc = structured_company or {}
                                        self.company_profile_service.upsert_company_profile(
                                            company_name=company_name,
                                            normalized_name=(sc.get("normalized_name") if isinstance(sc, dict) else None),
                                            basic_info=(sc.get("basic_info") if isinstance(sc, dict) else None),
                                            contact_info=(sc.get("contact_info") if isinstance(sc, dict) else None),
                                            culture=(sc.get("culture") if isinstance(sc, dict) else None),
                                            technologies=(sc.get("technologies") if isinstance(sc, dict) else None),
                                            recent_activity=(sc.get("recent_activity") if isinstance(sc, dict) else None),
                                            hiring_info=(sc.get("hiring_info") if isinstance(sc, dict) else None),
                                            ai_summary=(enrichment.ai_summary if hasattr(enrichment, "ai_summary") else None),
                                            ai_insights=(sc.get("ai_insights") if isinstance(sc, dict) else None),
                                            reputation_risk_analysis=risk_structured or (sc.get("reputation_risk_analysis") if isinstance(sc, dict) else None),
                                            raw_brave_data={
                                                "enrichment_data": companies_enrichment[company_name]["enrichment_data"]
                                            },
                                            enrichment_source="chatbot",
                                            enriched_by_session_id=session_id,
                                        )
                                except Exception as e:
                                    logger.warning(f"[Chatbot] Failed to persist company profile: {e}")
                        except Exception as e:
                            logger.warning(f"[Chatbot] Failed to enrich company '{company_name}': {e}")
            
            # Also try to enrich companies without links using just company name
            # This happens when user mentions company name without providing URL
            for exp in experience:
                if isinstance(exp, dict):
                    company_name = exp.get("company") or exp.get("employer") or exp.get("organization")
                    if not company_name:
                        continue
                    
                    # Initialize company data if not exists
                    if company_name not in companies_enrichment:
                        companies_enrichment[company_name] = {
                            "company_name": company_name,
                            "website": None,
                            "linkedin": None,
                            "email": None,
                            "enrichment_data": None
                        }
                    
                    # If company doesn't have enrichment data yet, try to enrich with Brave Search
                    if not companies_enrichment[company_name].get("enrichment_data"):
                        # Check if company name was mentioned in user message
                        company_name_lower = company_name.lower()
                        user_message_lower = user_message.lower()
                        
                        # If company name is mentioned in message, enrich it
                        if company_name_lower in user_message_lower or any(word in user_message_lower for word in company_name_lower.split() if len(word) > 3):
                            if self.brave_service and self.brave_service.is_enabled():
                                try:
                                    logger.info(f"[Chatbot] Enriching company '{company_name}' mentioned in message with Brave Search")
                                    enrichment = await self.brave_service.enrich_company(
                                        company_name=company_name,
                                        additional_context=None
                                    )
                                    
                                    if enrichment:
                                        companies_enrichment[company_name]["enrichment_data"] = {
                                            "website": enrichment.website,
                                            "description": enrichment.description,
                                            "industry": enrichment.industry,
                                            "size": enrichment.size,
                                            "location": enrichment.location,
                                            "recent_news": enrichment.recent_news[:3] if enrichment.recent_news else []
                                        }
                                        
                                        # If Brave found website, update it
                                        if enrichment.website and not companies_enrichment[company_name]["website"]:
                                            companies_enrichment[company_name]["website"] = enrichment.website
                                        
                                        logger.info(f"[Chatbot] Successfully enriched company '{company_name}' from mention")
                                except Exception as e:
                                    logger.warning(f"[Chatbot] Failed to enrich company '{company_name}' from mention: {e}")
            
            # Update session with companies enrichment data
            if companies_enrichment:
                self.db_service.update_session(session_id, {
                    "companies_enrichment": companies_enrichment
                })
                logger.info(f"[Chatbot] Updated session with enrichment for {len(companies_enrichment)} companies")
                
        except Exception as e:
            logger.error(f"Error processing company links: {e}", exc_info=True)
    
    def _build_system_prompt(self, session: Dict[str, Any], language: str) -> str:
        """Build system prompt for conversational AI based on session context."""
        base_prompts = {
            "en": """You are a helpful and friendly AI CV preparation assistant. Your role is to guide candidates through optimizing their CV for a specific job opportunity through natural conversation.

IMPORTANT: The workflow is:
1. FIRST: Ask them to share their current CV (PDF or DOCX format)
2. AFTER CV UPLOAD: System automatically extracts all information (name, email, phone, location, social media links, experience, skills, etc.) and shows a summary
3. REVIEW: Ask them to confirm if the extracted information is correct, or if they want to change/add anything
4. JOB OPPORTUNITY: Once profile is confirmed, ask for the job opportunity they're applying for
5. ANALYSIS: Analyze gaps between their CV and job requirements, provide recommendations
6. OPTIMIZATION: Generate optimized CVs (ATS-friendly and human-friendly versions)
7. PREPARATION: Prepare them for interviews with likely questions and suggested answers
8. SCORING: Calculate their employability score for this opportunity

IMPORTANT GUIDELINES:
- Be conversational, friendly, warm, and helpful
- The FIRST thing you ask for is their CV upload
- After CV is uploaded and extracted, help them review and confirm the extracted information
- Allow them to add additional relevant information that's not in their CV
- Once profile is confirmed, move to job opportunity
- Ask ONE question at a time to avoid overwhelming the user
- Adapt your language to match the user's style and language
- Be patient and encouraging
- Focus on helping them succeed
- If the user seems confused, clarify and provide examples

WHEN PROCESSING LINKS:
- If the user provides personal links (LinkedIn profile, GitHub, portfolio): Inform them clearly: "I'm analyzing your personal profile links to enrich your candidate profile. This will help me understand your professional background better."
- If the user provides company links (LinkedIn company page, company website): Inform them clearly: "I'm researching information about [Company Name] to better understand the company you worked for. This will help me tailor your CV recommendations."
- NEVER start processing company information automatically without explicit links or user request
- If you're processing something in the background, always inform the user what you're doing and why""",
            
            "pt": """És um assistente de IA útil e amigável para preparação de CVs. O teu papel é guiar candidatos através da otimização do seu CV para uma oportunidade de emprego específica através de conversa natural.

IMPORTANTE: O fluxo de trabalho é:
1. PRIMEIRO: Pede-lhes para partilharem o CV atual (formato PDF ou DOCX)
2. APÓS UPLOAD DO CV: O sistema extrai automaticamente toda a informação (nome, email, telefone, localização, links de redes sociais, experiência, competências, etc.) e mostra um resumo
3. REVISÃO: Pede-lhes para confirmarem se a informação extraída está correta, ou se querem alterar/adicionar algo
4. OPORTUNIDADE DE EMPREGO: Uma vez que o perfil está confirmado, pergunta pela oportunidade de emprego para a qual se estão a candidatar
5. ANÁLISE: Analisa lacunas entre o CV e os requisitos da vaga, fornece recomendações
6. OTIMIZAÇÃO: Gera CVs otimizados (versões compatíveis com ATS e amigáveis para humanos)
7. PREPARAÇÃO: Prepara-os para entrevistas com perguntas prováveis e respostas sugeridas
8. PONTUAÇÃO: Calcula a pontuação de empregabilidade para esta oportunidade

DIRETRIZES IMPORTANTES:
- Sê conversacional, amigável, caloroso e útil
- A PRIMEIRA coisa que pedes é o upload do CV
- Após o CV ser carregado e extraído, ajuda-os a rever e confirmar a informação extraída
- Permite que adicionem informações relevantes adicionais que não estejam no CV
- Uma vez que o perfil está confirmado, avança para a oportunidade de emprego
- Faz UMA pergunta de cada vez para não sobrecarregar o utilizador
- Adapta o teu idioma para corresponder ao estilo e idioma do utilizador
- Sê paciente e encorajador
- Foca-te em ajudá-los a ter sucesso
- Se o utilizador parecer confuso, esclarece e fornece exemplos

AO PROCESSAR LINKS:
- Se o utilizador fornecer links pessoais (perfil LinkedIn, GitHub, portefólio): Informa-os claramente: "Estou a analisar os teus links pessoais para enriquecer o teu perfil de candidato. Isto vai ajudar-me a entender melhor o teu background profissional."
- Se o utilizador fornecer links de empresas (página LinkedIn da empresa, website da empresa): Informa-os claramente: "Estou a pesquisar informações sobre [Nome da Empresa] para entender melhor a empresa onde trabalhaste. Isto vai ajudar-me a adaptar as recomendações do teu CV."
- NUNCA comeces a processar informações de empresas automaticamente sem links explícitos ou pedido do utilizador
- Se estiveres a processar algo em segundo plano, informa sempre o utilizador do que estás a fazer e porquê""",
            
            "fr": """Tu es un assistant IA utile et amical pour la préparation de CV. Ton rôle est de guider les candidats dans l'optimisation de leur CV pour une opportunité d'emploi spécifique à travers une conversation naturelle.

IMPORTANT: Le flux de travail est:
1. PREMIER: Demande-leur de partager leur CV actuel (format PDF ou DOCX)
2. APRÈS TÉLÉCHARGEMENT DU CV: Le système extrait automatiquement toutes les informations (nom, email, téléphone, localisation, liens de réseaux sociaux, expérience, compétences, etc.) et affiche un résumé
3. RÉVISION: Demande-leur de confirmer si les informations extraites sont correctes, ou s'ils veulent modifier/ajouter quelque chose
4. OPPORTUNITÉ D'EMPLOI: Une fois le profil confirmé, demande l'opportunité d'emploi pour laquelle ils postulent
5. ANALYSE: Analyse les écarts entre leur CV et les exigences du poste, fournit des recommandations
6. OPTIMISATION: Génère des CV optimisés (versions compatibles ATS et conviviaux pour les humains)
7. PRÉPARATION: Prépare-les pour les entretiens avec des questions probables et des réponses suggérées
8. SCORING: Calcule leur score d'employabilité pour cette opportunité

DIRECTIVES IMPORTANTES:
- Sois conversationnel, amical, chaleureux et utile
- La PREMIÈRE chose que tu demandes est le téléchargement de leur CV
- Après que le CV soit téléchargé et extrait, aide-les à réviser et confirmer les informations extraites
- Permets-leur d'ajouter des informations pertinentes supplémentaires qui ne se trouvent pas dans leur CV
- Une fois le profil confirmé, passe à l'opportunité d'emploi
- Pose UNE question à la fois pour ne pas submerger l'utilisateur
- Adapte ta langue pour correspondre au style et à la langue de l'utilisateur
- Sois patient et encourageant
- Concentre-toi sur l'aide à leur succès
- Si l'utilisateur semble confus, clarifie et fournis des exemples

LORS DU TRAITEMENT DES LIENS:
- Si l'utilisateur fournit des liens personnels (profil LinkedIn, GitHub, portfolio): Informe-le clairement: "J'analyse tes liens personnels pour enrichir ton profil de candidat. Cela m'aidera à mieux comprendre ton parcours professionnel."
- Si l'utilisateur fournit des liens d'entreprise (page LinkedIn de l'entreprise, site web de l'entreprise): Informe-le clairement: "Je recherche des informations sur [Nom de l'Entreprise] pour mieux comprendre l'entreprise où tu as travaillé. Cela m'aidera à adapter les recommandations de ton CV."
- NE commence JAMAIS à traiter automatiquement des informations d'entreprise sans liens explicites ou demande de l'utilisateur
- Si tu traites quelque chose en arrière-plan, informe toujours l'utilisateur de ce que tu fais et pourquoi""",
            
            "es": """Eres un asistente de IA útil y amigable para la preparación de CV. Tu papel es guiar a los candidatos a través de la optimización de su CV para una oportunidad de trabajo específica mediante conversación natural.

IMPORTANTE: El flujo de trabajo es:
1. PRIMERO: Pídeles que compartan su CV actual (formato PDF o DOCX)
2. DESPUÉS DE SUBIR EL CV: El sistema extrae automáticamente toda la información (nombre, email, teléfono, ubicación, enlaces de redes sociales, experiencia, habilidades, etc.) y muestra un resumen
3. REVISIÓN: Pídeles que confirmen si la información extraída es correcta, o si quieren cambiar/agregar algo
4. OPORTUNIDAD DE TRABAJO: Una vez que el perfil está confirmado, pregunta por la oportunidad de trabajo para la que están aplicando
5. ANÁLISIS: Analiza las brechas entre su CV y los requisitos del trabajo, proporciona recomendaciones
6. OPTIMIZACIÓN: Genera CVs optimizados (versiones compatibles con ATS y amigables para humanos)
7. PREPARACIÓN: Prepáralos para entrevistas con preguntas probables y respuestas sugeridas
8. PUNTUACIÓN: Calcula su puntuación de empleabilidad para esta oportunidad

PAUTAS IMPORTANTES:
- Sé conversacional, amigable, cálido y útil
- Lo PRIMERO que pides es la subida de su CV
- Después de que el CV sea subido y extraído, ayúdalos a revisar y confirmar la información extraída
- Permíteles agregar información relevante adicional que no esté en su CV
- Una vez que el perfil esté confirmado, pasa a la oportunidad de trabajo
- Haz UNA pregunta a la vez para no abrumar al usuario
- Adapta tu idioma para que coincida con el estilo y el idioma del usuario
- Sé paciente y alentador
- Enfócate en ayudarlos a tener éxito
- Si el usuario parece confundido, aclara y proporciona ejemplos

AL PROCESAR ENLACES:
- Si el usuario proporciona enlaces personales (perfil de LinkedIn, GitHub, portfolio): Infórmale claramente: "Estoy analizando tus enlaces personales para enriquecer tu perfil de candidato. Esto me ayudará a entender mejor tu trayectoria profesional."
- Si el usuario proporciona enlaces de empresas (página de LinkedIn de la empresa, sitio web de la empresa): Infórmale claramente: "Estoy investigando información sobre [Nombre de la Empresa] para entender mejor la empresa donde trabajaste. Esto me ayudará a adaptar las recomendaciones de tu CV."
- NUNCA comiences a procesar información de empresas automáticamente sin enlaces explícitos o solicitud del usuario
- Si estás procesando algo en segundo plano, informa siempre al usuario qué estás haciendo y por qué"""
        }
        
        system_prompt = base_prompts.get(language, base_prompts["en"])
        
        # Add context about what information has been collected
        context_labels = {
            "en": {
                "header": "Current Context:",
                "profile": "Profile information collected:",
                "cv": "CV has been uploaded and analyzed. You have access to the extracted CV text.",
                "job": "Job opportunity information:"
            },
            "pt": {
                "header": "Contexto Atual:",
                "profile": "Informações do perfil coletadas:",
                "cv": "CV foi carregado e analisado. Tens acesso ao texto extraído do CV.",
                "job": "Informações da oportunidade de emprego:"
            },
            "fr": {
                "header": "Contexte Actuel:",
                "profile": "Informations du profil collectées:",
                "cv": "Le CV a été téléchargé et analysé. Tu as accès au texte extrait du CV.",
                "job": "Informations sur l'opportunité d'emploi:"
            },
            "es": {
                "header": "Contexto Actual:",
                "profile": "Información del perfil recopilada:",
                "cv": "El CV ha sido subido y analizado. Tienes acceso al texto extraído del CV.",
                "job": "Información de la oportunidad de trabajo:"
            }
        }
        
        labels = context_labels.get(language, context_labels["en"])
        context_parts = []
        
        profile_data = session.get("profile_data", {})
        if profile_data and any(profile_data.values()):
            context_parts.append(f"{labels['profile']} {json.dumps(profile_data, ensure_ascii=False)}")
        
        cv_data = session.get("cv_data", {})
        if cv_data and cv_data.get("extracted_text"):
            context_parts.append(labels["cv"])
        
        job_data = session.get("job_opportunity_data", {})
        if job_data and job_data.get("title"):
            context_parts.append(f"{labels['job']} {json.dumps(job_data, ensure_ascii=False)}")
        
        if context_parts:
            system_prompt += f"\n\n{labels['header']}\n" + "\n".join(context_parts)
        
        return system_prompt
    
    async def _detect_user_input(
        self,
        session: Dict[str, Any],
        user_message: str,
        language: str
    ) -> Optional[Dict[str, Any]]:
        """Detect if user provided profile, CV, or job information."""
        try:
            # Use AI to detect what information was provided
            detection_prompt = f"""Analyze the following user message and detect what information was provided.

User message: {user_message}

Return JSON with detected information:
{{
  "has_profile": true/false,
  "profile_data": {{"name": "...", "email": "...", "phone": "...", "location": "...", "links": {{}}}},
  "has_cv": true/false,
  "has_job": true/false,
  "job_data": {{"title": "...", "company": "...", "description": "..."}}
}}

Return ONLY JSON."""

            ai_request = AIRequest(
                prompt_type=PromptType.CHATBOT_PROFILE_EXTRACTION,
                template=detection_prompt,
                variables={},
                language=language,
                temperature=0.3,
                max_tokens=500
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            if response.success and response.data:
                return response.data
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting user input: {e}")
            return None


# Singleton instance
_chatbot_service_instance: Optional[ChatbotService] = None


def get_chatbot_service() -> ChatbotService:
    """Get singleton instance of ChatbotService."""
    global _chatbot_service_instance
    if _chatbot_service_instance is None:
        _chatbot_service_instance = ChatbotService()
    return _chatbot_service_instance

