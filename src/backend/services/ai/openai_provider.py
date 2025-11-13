"""
OpenAI AI provider implementation.
"""

import json
import time
from typing import Dict, Any, Optional, List
import logging

from openai import AsyncOpenAI

from .base import AIProvider, AIRequest, AIResponse, PromptType

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """
    OpenAI AI provider.
    
    Supports GPT-4, GPT-3.5-turbo, and other OpenAI models.
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """Initialize OpenAI provider with API key."""
        super().__init__(api_key, config)
        
        requested_model = self.config.get("model")
        self._candidate_models: List[str] = (
            [requested_model] if requested_model else [
                "gpt-4.1-mini",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
            ]
        )
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model_name: Optional[str] = None
        self._current_index = -1

        if not self._initialize_model():
            raise ValueError(
                "No OpenAI models available. Checked candidates: "
                f"{', '.join(self._candidate_models)}"
            )
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    async def complete(self, request: AIRequest) -> AIResponse:
        """Execute completion request using OpenAI."""
        start_time = time.time()
        
        try:
            # Build complete prompt
            prompt = self.build_prompt(request.template, request.variables)
            
            # Get maximum tokens for this model
            from .model_limits import get_max_output_tokens
            max_tokens = request.max_tokens or get_max_output_tokens(self.model_name)
            
            # Create chat completion
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for CV analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=request.temperature or 0.7,
                max_tokens=max_tokens
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
                    logger.warning(f"Failed to parse OpenAI response as JSON: {e}")
                    logger.warning(f"Raw text (first 500 chars): {raw_text[:500]}")
            
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
            
            error_message = str(e).lower()
            if "model" in error_message and "not" in error_message and self._try_next_model():
                logger.info(
                    "Retrying OpenAI request with fallback model %s",
                    self.model_name,
                )
                return await self.complete(request)

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

    def _initialize_model(self) -> bool:
        """Initialise OpenAI model selection."""
        last_error: Optional[str] = None
        for idx in range(self._current_index + 1, len(self._candidate_models)):
            candidate = self._candidate_models[idx]
            try:
                # No API call needed; store candidate for use in requests
                self.model_name = candidate
                self._current_index = idx
                logger.info("OpenAI provider using model %s", candidate)
                return True
            except Exception as exc:  # pragma: no cover - defensive
                last_error = str(exc)
                logger.warning(
                    "OpenAI model %s unavailable (%s). Trying next fallback.",
                    candidate,
                    exc,
                )
        if last_error:
            logger.error("OpenAI initialization failed: %s", last_error)
        return False

    def _try_next_model(self) -> bool:
        """Attempt to switch to the next candidate model."""
        return self._initialize_model()

