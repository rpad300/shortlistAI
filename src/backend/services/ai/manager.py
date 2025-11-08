"""
AI Manager - Central service for managing AI providers and requests.

Handles provider selection, routing, fallback, and logging.
"""

from typing import Dict, Optional, Any
from .base import AIProvider, AIRequest, AIResponse
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .kimi_provider import KimiProvider
# Minimax provider imported dynamically when needed
from ...config import settings
import logging

logger = logging.getLogger(__name__)


class AIManager:
    """
    Central manager for AI operations.
    
    Responsibilities:
    - Initialize and manage multiple AI providers
    - Route requests to appropriate provider
    - Handle fallback when provider fails
    - Log AI usage for monitoring and cost tracking
    """
    
    def __init__(self):
        """Initialize AI manager with configured providers."""
        self.providers: Dict[str, AIProvider] = {}
        self.default_provider: Optional[str] = None
        
        # Initialize available providers based on environment variables
        self._initialize_providers()
    
    def _initialize_providers(self):
        """
        Initialize AI providers based on available API keys.
        """
        # Gemini
        if settings.gemini_api_key:
            self.providers["gemini"] = GeminiProvider(settings.gemini_api_key)
            if not self.default_provider:
                self.default_provider = "gemini"
            logger.info("Gemini provider initialized")
        
        # OpenAI
        if settings.openai_api_key:
            self.providers["openai"] = OpenAIProvider(settings.openai_api_key)
            if not self.default_provider:
                self.default_provider = "openai"
            logger.info("OpenAI provider initialized")
        
        # Claude
        if settings.anthropic_api_key:
            self.providers["claude"] = ClaudeProvider(settings.anthropic_api_key)
            if not self.default_provider:
                self.default_provider = "claude"
            logger.info("Claude provider initialized")

        # Kimi K2
        if settings.kimi_api_key:
            self.providers["kimi"] = KimiProvider(settings.kimi_api_key)
            if not self.default_provider:
                self.default_provider = "kimi"
            logger.info("Kimi provider initialized")

        # MiniMax - Only initialize if available
        # Note: Only used as fallback if Gemini/OpenAI/Claude fail
        minimax_key = os.getenv("MINIMAX_API_KEY")
        if minimax_key:
            try:
                from .minimax_provider import MinimaxProvider
                minimax_config = {
                    "group_id": os.getenv("MINIMAX_GROUP_ID", ""),
                }
                self.providers["minimax"] = MinimaxProvider(
                    minimax_key,
                    config=minimax_config,
                )
                if not self.default_provider:
                    self.default_provider = "minimax"
                logger.info("✅ Minimax provider initialized (Fallback 4)")
            except Exception as exc:
                logger.warning(f"Minimax provider failed to initialize: {exc}")
                # Continue without Minimax
        
        if not self.providers:
            logger.warning("No AI providers configured. Check API keys in environment.")
    
    def get_provider(self, provider_name: Optional[str] = None) -> Optional[AIProvider]:
        """
        Get AI provider by name.
        
        Args:
            provider_name: Name of provider or None for default
            
        Returns:
            AIProvider instance or None if not found
        """
        if provider_name:
            return self.providers.get(provider_name)
        
        if self.default_provider:
            return self.providers.get(self.default_provider)
        
        return None
    
    async def execute(
        self,
        request: AIRequest,
        provider_name: Optional[str] = None,
        enable_fallback: bool = True
    ) -> AIResponse:
        """
        Execute AI request with specified or default provider.
        
        Args:
            request: The AI request to execute
            provider_name: Specific provider to use or None for default
            enable_fallback: Whether to try other providers if first fails
            
        Returns:
            AIResponse with results or error
        """
        # Get primary provider
        provider = self.get_provider(provider_name)
        
        if not provider:
            return AIResponse(
                success=False,
                error="No AI provider available",
                provider="none"
            )
        
        # Execute request
        response = await provider.complete(request)
        
        # Log usage (TODO: store in database)
        await self._log_usage(request, response)
        
        # If failed and fallback enabled, try other providers
        if not response.success and enable_fallback:
            logger.warning(f"Provider {provider.provider_name} failed, trying fallback")
            
            for fallback_name, fallback_provider in self.providers.items():
                if fallback_name != provider.provider_name:
                    logger.info(f"Trying fallback provider: {fallback_name}")
                    response = await fallback_provider.complete(request)
                    await self._log_usage(request, response)
                    
                    if response.success:
                        break
        
        return response
    
    async def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        language: str = "en",
        provider_name: Optional[str] = None
    ) -> AIResponse:
        """
        Extract structured data from text.
        
        Args:
            text: Text to extract from
            schema: JSON schema for expected structure
            language: Language of the text
            provider_name: Specific provider to use
            
        Returns:
            AIResponse with extracted data
        """
        provider = self.get_provider(provider_name)
        
        if not provider:
            return AIResponse(
                success=False,
                error="No AI provider available",
                provider="none"
            )
        
        response = await provider.extract_structured_data(text, schema, language)
        await self._log_usage(None, response)
        
        return response
    
    async def _log_usage(self, request: Optional[AIRequest], response: AIResponse):
        """
        Log AI usage to database for monitoring and cost tracking.
        
        Args:
            request: The original request (if available)
            response: The response from AI provider
        """
        # TODO: Store in ai_usage_logs table
        log_data = {
            "provider": response.provider,
            "prompt_type": request.prompt_type if request else "unknown",
            "model_name": response.model,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.cost_usd,
            "latency_ms": response.latency_ms,
            "status": "success" if response.success else "error",
            "error_message": response.error
        }
        
        logger.info(f"AI usage: {log_data}")
        
        # In production, insert into database:
        # from database import get_supabase_client
        # client = get_supabase_client()
        # client.table("ai_usage_logs").insert(log_data).execute()
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all providers.
        
        Returns:
            Dict mapping provider names to health status
        """
        health = {}
        for name, provider in self.providers.items():
            health[name] = await provider.health_check()
        return health


# Global AI manager instance
_ai_manager: Optional[AIManager] = None


def get_ai_manager() -> AIManager:
    """
    Get global AI manager instance.
    
    Returns:
        AIManager singleton
    """
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIManager()
    return _ai_manager

