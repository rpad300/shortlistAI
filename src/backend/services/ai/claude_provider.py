"""
Anthropic Claude AI provider implementation.
"""

import json
import time
from typing import Dict, Any, Optional
from anthropic import AsyncAnthropic
from .base import AIProvider, AIRequest, AIResponse, PromptType
import logging

logger = logging.getLogger(__name__)


class ClaudeProvider(AIProvider):
    """
    Anthropic Claude AI provider.
    
    Supports Claude 3 Opus, Sonnet, and Haiku models.
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """Initialize Claude provider with API key."""
        super().__init__(api_key, config)
        
        # Default model
        self.model_name = self.config.get("model", "claude-3-sonnet-20240229")
        self.client = AsyncAnthropic(api_key=self.api_key)
    
    @property
    def provider_name(self) -> str:
        return "claude"
    
    async def complete(self, request: AIRequest) -> AIResponse:
        """Execute completion request using Claude."""
        start_time = time.time()
        
        try:
            # Build complete prompt
            prompt = self.build_prompt(request.template, request.variables)
            
            # Create message
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=request.max_tokens or 2048,
                temperature=request.temperature or 0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract response
            raw_text = response.content[0].text if response.content else ""
            
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
                    logger.warning("Failed to parse Claude response as JSON")
            
            # Calculate cost (Claude pricing)
            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0
            
            # Claude 3 pricing (approximate)
            if "opus" in self.model_name:
                cost_usd = (input_tokens * 0.000015) + (output_tokens * 0.000075)
            elif "sonnet" in self.model_name:
                cost_usd = (input_tokens * 0.000003) + (output_tokens * 0.000015)
            else:  # Haiku
                cost_usd = (input_tokens * 0.00000025) + (output_tokens * 0.00000125)
            
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
            logger.error(f"Claude API error: {e}")
            
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
        """Extract structured data from text using Claude."""
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

