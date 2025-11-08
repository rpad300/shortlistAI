"""
Google Gemini AI provider implementation.
"""

import json
import time
from typing import Dict, Any, Optional
import google.generativeai as genai
from .base import AIProvider, AIRequest, AIResponse, PromptType
import logging

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """
    Google Gemini AI provider.
    
    Supports Gemini Pro and other Gemini models.
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """Initialize Gemini provider with API key."""
        super().__init__(api_key, config)
        genai.configure(api_key=self.api_key)
        
        # Default model
        self.model_name = self.config.get("model", "gemini-pro")
        self.model = genai.GenerativeModel(self.model_name)
    
    @property
    def provider_name(self) -> str:
        return "gemini"
    
    async def complete(self, request: AIRequest) -> AIResponse:
        """
        Execute completion request using Gemini.
        """
        start_time = time.time()
        
        try:
            # Build complete prompt
            prompt = self.build_prompt(request.template, request.variables)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=request.temperature or 0.7,
                max_output_tokens=request.max_tokens or 2048,
            )
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract text
            raw_text = response.text if hasattr(response, 'text') else ""
            
            # Try to parse as JSON if expected
            data = None
            if request.prompt_type in [
                PromptType.CV_EXTRACTION,
                PromptType.JOB_POSTING_NORMALIZATION,
                PromptType.INTERVIEWER_ANALYSIS,
                PromptType.CANDIDATE_ANALYSIS
            ]:
                try:
                    # Try to find JSON in response
                    if "```json" in raw_text:
                        json_start = raw_text.find("```json") + 7
                        json_end = raw_text.find("```", json_start)
                        json_text = raw_text[json_start:json_end].strip()
                        data = json.loads(json_text)
                    else:
                        data = json.loads(raw_text)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse Gemini response as JSON")
            
            # Estimate cost (rough approximation)
            # Gemini pricing varies; this is a placeholder
            input_chars = len(prompt)
            output_chars = len(raw_text)
            cost_usd = (input_chars * 0.000001) + (output_chars * 0.000002)
            
            return AIResponse(
                success=True,
                data=data,
                raw_text=raw_text,
                provider=self.provider_name,
                model=self.model_name,
                input_tokens=input_chars // 4,  # Rough estimate
                output_tokens=output_chars // 4,
                latency_ms=latency_ms,
                cost_usd=cost_usd
            )
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Gemini API error: {e}")
            
            return AIResponse(
                success=False,
                error=str(e),
                provider=self.provider_name,
                model=self.model_name,
                latency_ms=latency_ms
            )
    
    async def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        language: str = "en"
    ) -> AIResponse:
        """
        Extract structured data from text using Gemini.
        """
        # Build prompt for structured extraction
        schema_str = json.dumps(schema, indent=2)
        
        template = """Extract information from the following text and return it as JSON matching this schema:

Schema:
{schema}

Text to analyze:
{text}

Return ONLY valid JSON matching the schema above, with no additional text or explanation."""
        
        request = AIRequest(
            prompt_type=PromptType.CV_EXTRACTION,
            template=template,
            variables={
                "schema": schema_str,
                "text": text
            },
            language=language,
            temperature=0.3,  # Lower temperature for more consistent extraction
            max_tokens=2048
        )
        
        return await self.complete(request)

