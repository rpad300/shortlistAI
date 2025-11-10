"""
Minimax AI provider implementation.

Using Minimax's official API as documented at:
https://platform.minimax.io/docs/guides/models-intro
"""

import json
import time
from typing import Dict, Any, Optional
import httpx
from .base import AIProvider, AIRequest, AIResponse, PromptType
import logging

logger = logging.getLogger(__name__)


class MinimaxProvider(AIProvider):
    """
    Minimax AI provider.
    
    Uses Minimax API for text generation and analysis.
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """Initialize Minimax provider with API key."""
        super().__init__(api_key, config)
        
        # Minimax API configuration
        self.api_base = self.config.get("api_base", "https://api.minimax.chat/v1")
        self.model_name = self.config.get("model", "abab6.5-chat")
        self.group_id = self.config.get("group_id", "")  # Required by Minimax
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @property
    def provider_name(self) -> str:
        return "minimax"
    
    async def complete(self, request: AIRequest) -> AIResponse:
        """Execute completion request using Minimax API."""
        start_time = time.time()
        
        try:
            # Build complete prompt
            prompt = self.build_prompt(request.template, request.variables)
            
            # Prepare request payload (Minimax format)
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant for CV analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": request.temperature or 0.7,
                "max_tokens": request.max_tokens or 2048,
                "top_p": 0.95
            }
            
            # Add group_id if configured
            if self.group_id:
                payload["group_id"] = self.group_id
            
            # Make async HTTP request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/text/chatcompletion_v2",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract response (Minimax format)
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
                    logger.warning(f"Failed to parse Minimax response as JSON: {e}")
                    logger.warning(f"Raw text (first 500 chars): {raw_text[:500]}")
            
            # Extract usage statistics
            usage = result.get("usage", {})
            input_tokens = usage.get("total_tokens", 0) - usage.get("completion_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            
            # Estimate cost (Minimax pricing - approximate)
            cost_usd = (input_tokens * 0.000001) + (output_tokens * 0.000002)
            
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
            logger.error(f"Minimax API error: {e}")
            
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
        """Extract structured data from text using Minimax."""
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
