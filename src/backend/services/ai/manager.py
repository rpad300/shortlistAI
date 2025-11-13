"""
AI Manager - Central service for managing AI providers and requests.

Handles provider selection, routing, fallback, and logging.
"""

import logging
import os
from typing import Dict, Optional, Any

from config import settings

from .base import AIProvider, AIRequest, AIResponse
from .claude_provider import ClaudeProvider
from .gemini_provider import GeminiProvider
from .kimi_provider import KimiProvider
from .openai_provider import OpenAIProvider
# Minimax provider imported dynamically when needed

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
        
        # Load fallback chain from database (async, but we'll set it on first use)
        self._db_fallback_chain: Optional[List[Dict[str, Any]]] = None
    
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
    
    async def _load_fallback_chain_from_db(self):
        """Load fallback chain from database."""
        if hasattr(self, '_db_fallback_chain') and self._db_fallback_chain is not None:
            return self._db_fallback_chain
        
        try:
            import json
            from database import get_supabase_client
            client = get_supabase_client()
            result = client.table("app_settings").select("*").eq("setting_key", "default_ai_provider").execute()
            
            if result.data and len(result.data) > 0:
                setting_value = result.data[0]["setting_value"]
                # Try to parse as JSON (new format)
                try:
                    fallback_chain = json.loads(setting_value) if isinstance(setting_value, str) else setting_value
                    if isinstance(fallback_chain, list):
                        # Filter to only include available providers
                        filtered_chain = [
                            item for item in fallback_chain
                            if item.get("provider") in self.providers
                        ]
                        if filtered_chain:
                            self._db_fallback_chain = filtered_chain
                            logger.info(f"Loaded fallback chain from database: {len(filtered_chain)} provider(s)")
                            return filtered_chain
                except (json.JSONDecodeError, TypeError):
                    # Old format (single provider string)
                    if setting_value in self.providers:
                        self._db_fallback_chain = [{"provider": setting_value, "model": None, "order": 1}]
                        return self._db_fallback_chain
        except Exception as e:
            logger.warning(f"Could not load fallback chain from database: {e}")
        
        self._db_fallback_chain = []
        return []
    
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
        model_name: Optional[str] = None,
        enable_fallback: bool = True  # ENABLED: Fallback between providers/models
    ) -> AIResponse:
        """
        Execute AI request with fallback chain support.
        
        If provider_name is specified, uses that provider (with optional model).
        Otherwise, uses fallback chain from database.
        
        Args:
            request: The AI request to execute
            provider_name: Specific provider to use or None for fallback chain
            model_name: Specific model to use (only if provider_name is specified)
            enable_fallback: Whether to try fallback chain if first attempt fails
            
        Returns:
            AIResponse with results or error
        """
        # If specific provider/model requested, try that first
        if provider_name:
            provider = self.get_provider(provider_name)
            if provider:
                # Create a temporary provider instance with specific model if needed
                if model_name:
                    # Create provider with specific model config
                    from config import settings
                    
                    # Normalize model name for Gemini (needs "models/" prefix)
                    normalized_model = model_name
                    if provider_name == "gemini" and not normalized_model.startswith("models/"):
                        normalized_model = f"models/{normalized_model}"
                    
                    provider_config = {"model": normalized_model}
                    
                    if provider_name == "gemini" and settings.gemini_api_key:
                        from .gemini_provider import GeminiProvider
                        provider = GeminiProvider(settings.gemini_api_key, provider_config)
                    elif provider_name == "openai" and settings.openai_api_key:
                        from .openai_provider import OpenAIProvider
                        provider = OpenAIProvider(settings.openai_api_key, provider_config)
                    elif provider_name == "kimi" and settings.kimi_api_key:
                        from .kimi_provider import KimiProvider
                        provider = KimiProvider(settings.kimi_api_key, provider_config)
                    elif provider_name == "claude" and settings.anthropic_api_key:
                        from .claude_provider import ClaudeProvider
                        provider = ClaudeProvider(settings.anthropic_api_key, provider_config)
                
                response = await provider.complete(request)
                await self._log_usage(request, response)
                if response.success or not enable_fallback:
                    return response
        
        # Load fallback chain from database
        fallback_chain = await self._load_fallback_chain_from_db()
        
        if not fallback_chain:
            # Fallback to default provider if no chain configured
            if self.default_provider:
                provider = self.get_provider(self.default_provider)
                if provider:
                    response = await provider.complete(request)
                    await self._log_usage(request, response)
                    return response
        
        # Try each item in fallback chain
        last_error = None
        for item in fallback_chain:
            provider_name_item = item.get("provider")
            model_name_item = item.get("model")
            
            provider = self.get_provider(provider_name_item)
            if not provider:
                logger.warning(f"Provider {provider_name_item} not available, skipping")
                continue
            
            # Create provider instance with specific model if specified
            if model_name_item:
                from config import settings
                
                # Normalize model name for Gemini (needs "models/" prefix)
                normalized_model = model_name_item
                if provider_name_item == "gemini" and not normalized_model.startswith("models/"):
                    normalized_model = f"models/{normalized_model}"
                
                provider_config = {"model": normalized_model}
                
                try:
                    if provider_name_item == "gemini" and settings.gemini_api_key:
                        from .gemini_provider import GeminiProvider
                        provider = GeminiProvider(settings.gemini_api_key, provider_config)
                    elif provider_name_item == "openai" and settings.openai_api_key:
                        from .openai_provider import OpenAIProvider
                        provider = OpenAIProvider(settings.openai_api_key, provider_config)
                    elif provider_name_item == "kimi" and settings.kimi_api_key:
                        from .kimi_provider import KimiProvider
                        provider = KimiProvider(settings.kimi_api_key, provider_config)
                    elif provider_name_item == "claude" and settings.anthropic_api_key:
                        from .claude_provider import ClaudeProvider
                        provider = ClaudeProvider(settings.anthropic_api_key, provider_config)
                    elif provider_name_item == "minimax" and settings.minimax_api_key:
                        from .minimax_provider import MinimaxProvider
                        import os
                        minimax_config = {
                            "group_id": os.getenv("MINIMAX_GROUP_ID", ""),
                            "model": normalized_model
                        }
                        provider = MinimaxProvider(settings.minimax_api_key, minimax_config)
                except Exception as e:
                    logger.warning(f"Failed to create {provider_name_item} provider with model {model_name_item}: {e}")
                    last_error = str(e)
                    continue
            
            try:
                logger.info(f"Trying {provider_name_item}/{model_name_item or 'default'}")
                response = await provider.complete(request)
                await self._log_usage(request, response)
                if response.success:
                    return response
                last_error = response.error
            except Exception as e:
                logger.warning(f"Error with {provider_name_item}/{model_name_item or 'default'}: {e}")
                last_error = str(e)
        
        # All fallback attempts failed
        return AIResponse(
            success=False,
            error=f"All providers in fallback chain failed. Last error: {last_error}",
            provider="none"
        )
    
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

