"""
Kimi AI provider implementation.

Using Kimi's official API as documented at:
https://kimi-k2.ai/api-docs
"""

import json
import time
from typing import Dict, Any, Optional
import httpx
from .base import AIProvider, AIRequest, AIResponse, PromptType
import logging

logger = logging.getLogger(__name__)


class KimiProvider(AIProvider):
    """
    Kimi AI provider.
    
    Uses Kimi API for text generation and analysis.
    Compatible with OpenAI-like API structure.
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """Initialize Kimi provider with API key."""
        super().__init__(api_key, config)
        
        # Kimi API configuration
        self.api_base = self.config.get("api_base", "https://api.moonshot.cn/v1")
        self.model_name = self.config.get("model", "moonshot-v1-8k")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @property
    def provider_name(self) -> str:
        return "kimi"
    
    async def complete(self, request: AIRequest) -> AIResponse:
        """Execute completion request using Kimi API."""
        start_time = time.time()
        
        try:
            # Build complete prompt
            prompt = self.build_prompt(request.template, request.variables)
            
            # Prepare request payload (OpenAI-compatible format)
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant for CV analysis."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": request.temperature or 0.7,
                "max_tokens": request.max_tokens or 2048
            }
            
            # Make async HTTP request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract response
            raw_text = result["choices"][0]["message"]["content"]
            
            # Try to parse as JSON if expected
            data = None
            if request.prompt_type in [
                PromptType.CV_EXTRACTION,
                PromptType.JOB_POSTING_NORMALIZATION,
                PromptType.INTERVIEWER_ANALYSIS,
                PromptType.CANDIDATE_ANALYSIS,
                PromptType.WEIGHTING_RECOMMENDATION,
                PromptType.CV_SUMMARY,
                PromptType.EXECUTIVE_RECOMMENDATION
            ]:
                try:
                    # Try to find JSON in response
                    json_text = raw_text
                    if "```json" in raw_text:
                        json_start = raw_text.find("```json") + 7
                        json_end = raw_text.find("```", json_start)
                        json_text = raw_text[json_start:json_end].strip()
                    elif "```" in raw_text:
                        json_start = raw_text.find("```") + 3
                        json_end = raw_text.find("```", json_start)
                        json_text = raw_text[json_start:json_end].strip()
                    
                    # Clean up common AI mistakes
                    json_text = json_text.strip()
                    # Fix double braces (AI sometimes copies {{ from examples)
                    # Replace ALL occurrences, not just start/end
                    json_text = json_text.replace("{{", "{").replace("}}", "}")
                    
                    data = json.loads(json_text)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse Kimi response as JSON: {e}")
                    logger.warning(f"Raw text (first 500 chars): {raw_text[:500]}")
            
            # Extract usage statistics
            usage = result.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            
            # Estimate cost (Kimi pricing - approximate)
            cost_usd = (input_tokens * 0.000002) + (output_tokens * 0.000004)
            
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
            logger.error(f"Kimi API error: {e}")
            
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
        """Extract structured data from text using Kimi."""
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
