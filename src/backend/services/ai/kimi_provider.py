"""
Kimi K2 AI provider implementation using the official OpenAI-compatible SDK.

The Kimi API exposes OpenAI- and Anthropic-compatible interfaces. To stay in
line with the "original library" requirement we reuse the official OpenAI
Python client and only override the `base_url` so that requests are sent to
Kimi's gateway while the rest of the client stack (auth, retries, parsing)
remains untouched.
"""

import json
import time
from typing import Any, Dict, Optional

from openai import AsyncOpenAI

from .base import AIProvider, AIRequest, AIResponse, PromptType

import logging

logger = logging.getLogger(__name__)


class KimiProvider(AIProvider):
    """
    Kimi K2 AI provider.

    The service is OpenAI-compatible, so the official `openai` SDK is used with
    the base URL configured to point at `https://kimi-k2.ai/api/v1`.
    """

    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """Initialize Kimi provider with API key and optional configuration."""
        super().__init__(api_key, config)
        self.model_name = self.config.get("model", "kimi-k2-0905")
        self.base_url = self.config.get("base_url", "https://kimi-k2.ai/api/v1")
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    @property
    def provider_name(self) -> str:
        return "kimi"

    async def complete(self, request: AIRequest) -> AIResponse:
        """Execute completion request using the Kimi OpenAI-compatible API."""
        start_time = time.time()

        try:
            prompt = self.build_prompt(request.template, request.variables)

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI assistant specialised in CV analysis "
                            "and recruiting support."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or 2048,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            raw_text = response.choices[0].message.content if response.choices else ""

            data: Optional[Dict[str, Any]] = None
            if request.prompt_type in {
                PromptType.CV_EXTRACTION,
                PromptType.JOB_POSTING_NORMALIZATION,
                PromptType.INTERVIEWER_ANALYSIS,
                PromptType.CANDIDATE_ANALYSIS,
            }:
                try:
                    if "```json" in raw_text:
                        json_start = raw_text.find("```json") + 7
                        json_end = raw_text.find("```", json_start)
                        json_text = raw_text[json_start:json_end].strip()
                        data = json.loads(json_text)
                    else:
                        data = json.loads(raw_text)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse Kimi response as JSON")

            usage = response.usage or None
            input_tokens = usage.prompt_tokens if usage else None
            output_tokens = usage.completion_tokens if usage else None

            # Pricing published 2025-01-30 (Starter plan as reference)
            # The API is credit-based; we store token counts for downstream cost
            # computation handled by billing logic.
            cost_usd = None

            return AIResponse(
                success=True,
                data=data,
                raw_text=raw_text,
                provider=self.provider_name,
                model=self.model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                cost_usd=cost_usd,
            )

        except Exception as exc:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error("Kimi API error: %s", exc)
            return AIResponse(
                success=False,
                error=str(exc),
                provider=self.provider_name,
                model=self.model_name,
                latency_ms=latency_ms,
            )

    async def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        language: str = "en",
    ) -> AIResponse:
        """Extract structured data from text via the Kimi API."""
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
            variables={"schema": schema_str, "text": text},
            language=language,
            temperature=0.3,
            max_tokens=2048,
        )

        return await self.complete(request)


