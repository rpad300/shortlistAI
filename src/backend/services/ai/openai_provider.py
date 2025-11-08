"""
OpenAI AI provider implementation.
"""

import json
import time
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from .base import AIProvider, AIRequest, AIResponse, PromptType
import logging

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """
    OpenAI AI provider.
    
    Supports GPT-4, GPT-3.5-turbo, and other OpenAI models.
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """Initialize OpenAI provider with API key."""
        super().__init__(api_key, config)
        
        # Default model
        self.model_name = self.config.get("model", "gpt-4-turbo-preview")
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    async def complete(self, request: AIRequest) -> AIResponse:
        """Execute completion request using OpenAI."""
        start_time = time.time()
        
        try:
            # Build complete prompt
            prompt = self.build_prompt(request.template, request.variables)
            
            # Create chat completion
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for CV analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or 2048
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract response
            raw_text = response.choices[0].message.content
            
            # Try to parse as JSON if expected
            data = None
            if request.prompt_type in [
                PromptType.CV_EXTRACTION,
                PromptType.JOB_POSTING_NORMALIZATION,
                PromptType.INTERVIEWER_ANALYSIS,
                PromptType.CANDIDATE_ANALYSIS
            ]:
                try:
                    if "```json" in raw_text:
                        json_start = raw_text.find("```json") + 7
                        json_end = raw_text.find("```", json_start)
                        json_text = raw_text[json_start:json_end].strip()
                        data = json.loads(json_text)
                    else:
                        data = json.loads(raw_text)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse OpenAI response as JSON")
            
            # Calculate cost (rough estimate based on OpenAI pricing)
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            
            # GPT-4 pricing (approximate)
            if "gpt-4" in self.model_name:
                cost_usd = (input_tokens * 0.00003) + (output_tokens * 0.00006)
            else:  # GPT-3.5
                cost_usd = (input_tokens * 0.0000015) + (output_tokens * 0.000002)
            
            return AIResponse(
                success=True,
                data=data,
                raw_text=raw_text,
                provider=self.provider_name,
                model=self.model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                cost_usd=cost_usd
            )
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"OpenAI API error: {e}")
            
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
        """Extract structured data from text using OpenAI."""
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
            temperature=0.3,
            max_tokens=2048
        )
        
        return await self.complete(request)

