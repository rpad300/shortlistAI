"""
Kimi K2 AI provider implementation.

Using Kimi K2's official API as documented at:
https://kimi-k2.ai/api-docs
"""

import json
import time
from typing import Dict, Any, Optional, List
import httpx
from .base import AIProvider, AIRequest, AIResponse, PromptType
import logging

logger = logging.getLogger(__name__)


class KimiProvider(AIProvider):
    """
    Kimi K2 AI provider.
    
    Uses Kimi K2 API for text generation and analysis.
    Compatible with OpenAI-like API structure.
    Supports models: kimi-k2, kimi-k2-0905, kimi-k2-thinking
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """Initialize Kimi provider with API key."""
        super().__init__(api_key, config)
        
        # Kimi K2 API configuration
        self.api_base = self.config.get("api_base", "https://kimi-k2.ai/api/v1")
        
        requested_model = self.config.get("model")
        preferred_models = self.config.get(
            "preferred_models",
            [
                "kimi-k2-0905",      # 256K context window
                "kimi-k2",            # 128K context window
                "kimi-k2-thinking",   # For complex reasoning
            ]
        )
        
        self._candidate_models: List[str] = (
            [requested_model] if requested_model else preferred_models
        )
        
        self.model_name: Optional[str] = None
        self._current_index = -1
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self._initialize_model():
            raise ValueError(
                "No Kimi models available. Checked candidates: "
                f"{', '.join(self._candidate_models)}"
            )
    
    @property
    def provider_name(self) -> str:
        return "kimi"
    
    async def complete(self, request: AIRequest) -> AIResponse:
        """Execute completion request using Kimi K2 API."""
        start_time = time.time()
        
        try:
            # Build complete prompt
            prompt = self.build_prompt(request.template, request.variables)
            
            # Get maximum tokens for this model
            from .model_limits import get_max_output_tokens
            max_tokens = request.max_tokens or get_max_output_tokens(self.model_name)
            
            # Prepare request payload (OpenAI-compatible format)
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant for CV analysis."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": request.temperature or 0.7,
                "max_tokens": max_tokens
            }
            
            # Make async HTTP request
            # Increased timeout for large CV analysis requests (can take 3-5 minutes)
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract response - handle different response structures
            raw_text = ""
            try:
                # Try OpenAI-compatible format first
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice:
                        message = choice["message"]
                        # For thinking models, check reasoning field if content is empty
                        raw_text = message.get("content", "")
                        if not raw_text and "reasoning" in message:
                            # For thinking models, the reasoning might contain the actual response
                            reasoning = message.get("reasoning", "")
                            if reasoning:
                                # Try to extract JSON from reasoning
                                # The reasoning might contain the full response or just the thinking process
                                # Look for JSON in the reasoning text
                                logger.info("Kimi thinking model: content empty, checking reasoning field")
                                
                                # Try to find JSON in reasoning (might be at the end)
                                # Look for JSON object/array patterns
                                json_start = max(
                                    reasoning.rfind("{"),
                                    reasoning.rfind("[")
                                )
                                if json_start >= 0:
                                    # Found potential JSON, extract from there
                                    potential_json = reasoning[json_start:]
                                    # Try to find the end of JSON
                                    brace_count = potential_json.count("{") - potential_json.count("}")
                                    bracket_count = potential_json.count("[") - potential_json.count("]")
                                    if brace_count == 0 and bracket_count == 0:
                                        # Balanced, use this as the response
                                        raw_text = potential_json
                                        logger.info("Kimi thinking model: extracted JSON from reasoning")
                                    else:
                                        # Not balanced, use full reasoning
                                        raw_text = reasoning
                                        logger.info("Kimi thinking model: using full reasoning as response")
                                else:
                                    # No JSON found, use reasoning anyway
                                    raw_text = reasoning
                                    logger.info("Kimi thinking model: using reasoning field as response (no JSON pattern found)")
                    elif "text" in choice:
                        raw_text = choice["text"]
                    elif "delta" in choice and "content" in choice["delta"]:
                        raw_text = choice["delta"]["content"]
                elif "text" in result:
                    raw_text = result["text"]
                elif "content" in result:
                    raw_text = result["content"]
                elif "message" in result:
                    message = result["message"]
                    raw_text = message.get("content", "")
                    if not raw_text and "reasoning" in message:
                        raw_text = message.get("reasoning", "")
                
                # Log if we couldn't extract text
                if not raw_text:
                    logger.warning(f"Kimi response structure unexpected. Full result: {json.dumps(result, indent=2)[:1000]}")
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"Error extracting Kimi response text: {e}")
                logger.error(f"Response structure: {json.dumps(result, indent=2)[:1000]}")
                raw_text = ""
            
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
                if not raw_text:
                    logger.error("Kimi returned empty response, cannot parse JSON")
                else:
                    json_text = raw_text  # Initialize before try block
                    try:
                        # Try to find JSON in response
                        json_text = raw_text
                        
                        # First, try to extract from code blocks
                        if "```json" in raw_text:
                            json_start = raw_text.find("```json") + 7
                            # Find the closing ``` (could be ```json or just ```)
                            json_end = raw_text.find("```", json_start)
                            if json_end == -1:
                                # No closing found, might be truncated - use everything after opening
                                json_end = len(raw_text)
                            if json_end > json_start:
                                json_text = raw_text[json_start:json_end].strip()
                                logger.info("Extracted JSON from ```json code block")
                        elif "```" in raw_text:
                            # Try to find code block
                            json_start = raw_text.find("```") + 3
                            # Skip language identifier if present (e.g., ```json or ```python)
                            # Check if next char is newline or {
                            if json_start < len(raw_text):
                                # Skip until we find { or [
                                while json_start < len(raw_text) and raw_text[json_start] not in "{[":
                                    if raw_text[json_start] == '\n':
                                        json_start += 1
                                        break
                                    json_start += 1
                            
                            json_end = raw_text.find("```", json_start)
                            if json_end == -1:
                                # No closing found, might be truncated - use everything after opening
                                json_end = len(raw_text)
                            if json_end > json_start:
                                json_text = raw_text[json_start:json_end].strip()
                                logger.info("Extracted JSON from ``` code block")
                        
                        # Clean up common AI mistakes
                        json_text = json_text.strip()
                        # Remove leading/trailing whitespace and newlines
                        json_text = json_text.strip('\n\r\t ')
                        
                        # Fix double braces (AI sometimes copies {{ from examples)
                        # Replace ALL occurrences, not just start/end
                        json_text = json_text.replace("{{", "{").replace("}}", "}")
                        
                        # Try to find JSON object/array boundaries if not already found
                        if not json_text.startswith(("{", "[")):
                            # Try to find first { or [
                            start_idx = min(
                                json_text.find("{") if json_text.find("{") >= 0 else len(json_text),
                                json_text.find("[") if json_text.find("[") >= 0 else len(json_text)
                            )
                            if start_idx < len(json_text):
                                # Find matching closing brace/bracket
                                brace_count = 0
                                bracket_count = 0
                                end_idx = start_idx
                                for i in range(start_idx, len(json_text)):
                                    if json_text[i] == "{":
                                        brace_count += 1
                                    elif json_text[i] == "}":
                                        brace_count -= 1
                                    elif json_text[i] == "[":
                                        bracket_count += 1
                                    elif json_text[i] == "]":
                                        bracket_count -= 1
                                    
                                    if brace_count == 0 and bracket_count == 0:
                                        end_idx = i + 1
                                        break
                                json_text = json_text[start_idx:end_idx]
                        
                        data = json.loads(json_text)
                        logger.info(f"Successfully parsed Kimi JSON response")
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse Kimi response as JSON: {e}")
                        logger.warning(f"Raw text (first 1000 chars): {raw_text[:1000]}")
                        logger.warning(f"Attempted JSON text (first 500 chars): {json_text[:500] if 'json_text' in locals() else 'N/A'}")
                    except Exception as e:
                        logger.error(f"Unexpected error parsing Kimi JSON: {e}")
                        logger.error(f"Raw text (first 1000 chars): {raw_text[:1000]}")
            
            # Extract usage statistics
            usage = result.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            
            # Estimate cost (Kimi K2 pricing - approximate, based on credit system)
            # 1 credit = 1 request, pricing varies by package
            # Rough estimate: $0.003-0.01 per request depending on package
            cost_usd = 0.005  # Average estimate
            
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
            
        except httpx.HTTPStatusError as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            logger.error(f"Kimi API HTTP error: {e}")
            
            # Try next model if model not found
            if e.response.status_code == 404 and "model" in error_msg.lower():
                if self._try_next_model():
                    logger.info(f"Retrying Kimi request with fallback model {self.model_name}")
                    return await self.complete(request)
            
            return AIResponse(
                success=False,
                error=error_msg,
                provider=self.provider_name,
                model=self.model_name,
                latency_ms=latency_ms
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
    
    def _initialize_model(self) -> bool:
        """Initialize Kimi model selection."""
        for idx in range(self._current_index + 1, len(self._candidate_models)):
            candidate = self._candidate_models[idx]
            try:
                self.model_name = candidate
                self._current_index = idx
                logger.info(f"Kimi provider using model {candidate}")
                return True
            except Exception as exc:
                logger.warning(f"Kimi model {candidate} unavailable ({exc}). Trying next fallback.")
        return False
    
    def _try_next_model(self) -> bool:
        """Attempt to switch to the next candidate model."""
        return self._initialize_model()
    
    async def health_check(self) -> bool:
        """Check if Kimi provider is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.api_base}/models",
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception:
            return False
    
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
