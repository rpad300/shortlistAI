"""
Pricing service for AI models.

Manages pricing information for AI models from different providers.
Pricing can be fetched from provider APIs or manually configured.
"""

from typing import Optional, Dict, Any, List
from database import get_supabase_client
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PricingService:
    """Service for managing AI model pricing information."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "ai_model_pricing"
    
    async def get_pricing(
        self, 
        provider: str, 
        model_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get pricing for a specific provider and model.
        
        Args:
            provider: Provider name (openai, claude, gemini, kimi, minimax)
            model_name: Optional specific model name
            
        Returns:
            Pricing dict with input_price_per_1m, output_price_per_1m, etc.
        """
        try:
            query = self.client.table(self.table)\
                .select("*")\
                .eq("provider", provider)\
                .eq("is_active", True)
            
            if model_name:
                query = query.eq("model_name", model_name)
            
            query = query.order("last_updated_at", desc=True)
            result = query.execute()
            
            if result.data and len(result.data) > 0:
                # Return most recent pricing
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting pricing for {provider}/{model_name}: {e}")
            return None
    
    async def get_all_pricing(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all active pricing records.
        
        Args:
            provider: Optional provider filter
            
        Returns:
            List of pricing records
        """
        try:
            query = self.client.table(self.table)\
                .select("*")\
                .eq("is_active", True)\
                .order("provider, model_name")
            
            if provider:
                query = query.eq("provider", provider)
            
            result = query.execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting all pricing: {e}")
            return []
    
    async def upsert_pricing(
        self,
        provider: str,
        model_name: str,
        input_price_per_1m: float,
        output_price_per_1m: float,
        model_display_name: Optional[str] = None,
        pricing_type: str = "per_token",
        per_request_price: Optional[float] = None,
        context_window: Optional[int] = None,
        max_output_tokens: Optional[int] = None,
        source: str = "api",
        updated_by: str = "system"
    ) -> Optional[Dict[str, Any]]:
        """
        Upsert pricing information for a model.
        
        Args:
            provider: Provider name
            model_name: Model identifier
            input_price_per_1m: Price per 1M input tokens
            output_price_per_1m: Price per 1M output tokens
            model_display_name: Human-readable model name
            pricing_type: 'per_token', 'per_request', 'credit_based'
            per_request_price: For per-request pricing
            context_window: Max context window
            max_output_tokens: Max output tokens
            source: 'api', 'manual', 'estimated'
            updated_by: Who updated this
            
        Returns:
            Created/updated pricing record
        """
        try:
            # Check if exists
            existing = await self.get_pricing(provider, model_name)
            
            data = {
                "provider": provider,
                "model_name": model_name,
                "model_display_name": model_display_name or model_name,
                "input_price_per_1m": input_price_per_1m,
                "output_price_per_1m": output_price_per_1m,
                "pricing_type": pricing_type,
                "per_request_price": per_request_price,
                "context_window": context_window,
                "max_output_tokens": max_output_tokens,
                "source": source,
                "updated_by": updated_by,
                "last_updated_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            
            if existing:
                # Update existing
                result = self.client.table(self.table)\
                    .update(data)\
                    .eq("id", existing["id"])\
                    .execute()
            else:
                # Insert new
                result = self.client.table(self.table)\
                    .insert(data)\
                    .execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Upserted pricing for {provider}/{model_name}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error upserting pricing for {provider}/{model_name}: {e}")
            return None
    
    async def deactivate_pricing(self, provider: str, model_name: str) -> bool:
        """Deactivate pricing for a model."""
        try:
            result = self.client.table(self.table)\
                .update({"is_active": False})\
                .eq("provider", provider)\
                .eq("model_name", model_name)\
                .execute()
            
            return result.data is not None and len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error deactivating pricing for {provider}/{model_name}: {e}")
            return False


def get_pricing_service() -> PricingService:
    """Get pricing service instance."""
    return PricingService()

