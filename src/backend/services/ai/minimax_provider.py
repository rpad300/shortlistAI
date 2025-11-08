"""
MiniMax AI provider implementation.

The MiniMax platform exposes a REST API that differs from the OpenAI schema.
The official documentation (https://platform.minimax.io/docs/guides/models-intro)
specifies Bearer token authentication plus the `X-Group-ID` header. We keep the
implementation thin and rely on `httpx` as the sanctioned HTTP client while
respecting the documented request and response formats.
"""

import json
import os
import time
from typing import Any, Dict, Optional, Tuple

import httpx

from .base import AIProvider, AIRequest, AIResponse, PromptType

import logging

logger = logging.getLogger(__name__)


class MiniMaxProvider(AIProvider):
    """
    MiniMax AI provider.

    The provider requires both an API key and a Group ID. The Group ID can be
    supplied either through the config dictionary or the MINIMAX_GROUP_ID
    environment variable.
    """

    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(api_key, config)
        self.model_name = self.config.get("model", "abab6.5-chat")
        self.base_url = self.config.get(
            "base_url", "https://api.minimax.chat/v1/text/chatcompletion"
        )
        self.group_id = self.config.get("group_id") or os.getenv("MINIMAX_GROUP_ID")

        if not self.group_id:
            raise ValueError(
                "MiniMax provider requires a group identifier. "
                "Set MINIMAX_GROUP_ID or provide config['group_id']."
            )

        self.timeout = self.config.get("timeout_seconds", 60)

    @property
    def provider_name(self) -> str:
        return "minimax"

    async def complete(self, request: AIRequest) -> AIResponse:
        """Execute completion request using the MiniMax text chat endpoint."""
        start_time = time.time()

        prompt = self.build_prompt(request.template, request.variables)

        payload = {
            "model": self.model_name,
            "messages": [
                {"sender_type": "USER", "text": prompt},
            ],
            # The API expects integer token budgets. MiniMax refers to this as
            # "tokens_to_generate".
            "tokens_to_generate": request.max_tokens or 2048,
            "temperature": request.temperature if request.temperature is not None else 0.7,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Group-ID": self.group_id,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                )

            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code != 200:
                logger.error(
                    "MiniMax API error (%s): %s", response.status_code, response.text
                )
                return AIResponse(
                    success=False,
                    error=f"MiniMax API error: {response.text}",
                    provider=self.provider_name,
                    model=self.model_name,
                    latency_ms=latency_ms,
                )

            result = response.json()
            raw_text, parsed = self._extract_text_and_json(result)

            usage = result.get("usage", {})
            input_tokens = usage.get("input_tokens")
            output_tokens = usage.get("output_tokens") or usage.get("total_tokens")

            # Pricing is region specific; we leave cost calculation to billing.
            cost_usd = None

            return AIResponse(
                success=True,
                data=parsed,
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
            logger.error("MiniMax API request failed: %s", exc)
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
        """Extract structured data from free-form text using MiniMax."""
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

    def _extract_text_and_json(self, result: Dict[str, Any]) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Extract assistant text and JSON payload from the MiniMax response.

        The API can return either `output_text` or a `choices` collection.
        """
        raw_text = ""
        parsed: Optional[Dict[str, Any]] = None

        if "output_text" in result:
            raw_text = result["output_text"]
        elif "text" in result:
            raw_text = result["text"]
        elif "choices" in result:
            messages = result["choices"][0].get("messages", []) if result["choices"] else []
            for message in messages:
                if message.get("sender_type") == "BOT" and "text" in message:
                    raw_text = message["text"]
                    break
                content = message.get("content")
                if isinstance(content, list):
                    for block in content:
                        if block.get("type") in {"output_text", "text"} and block.get("text"):
                            raw_text = block["text"]
                            break
                    if raw_text:
                        break
        elif "data" in result and isinstance(result["data"], dict):
            raw_text = result["data"].get("output_text", "")

        if raw_text:
            try:
                if "```json" in raw_text:
                    json_start = raw_text.find("```json") + 7
                    json_end = raw_text.find("```", json_start)
                    json_text = raw_text[json_start:json_end].strip()
                    parsed = json.loads(json_text)
                else:
                    parsed = json.loads(raw_text)
            except json.JSONDecodeError:
                logger.debug("MiniMax response is not JSON; returning raw text only.")

        return raw_text, parsed


