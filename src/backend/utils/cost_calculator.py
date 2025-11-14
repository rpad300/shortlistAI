"""
Cost calculation utilities for AI providers.

Calculates costs based on token usage for different AI providers.
Uses pricing information from the database (ai_model_pricing table).
Falls back to hardcoded pricing if database pricing is not available.
"""

from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


async def calculate_cost_from_tokens(
    provider: str, 
    model: Optional[str], 
    input_tokens: Optional[int], 
    output_tokens: Optional[int]
) -> Dict[str, float]:
    """
    Calculate cost based on actual token usage.
    
    First tries to get pricing from database (ai_model_pricing table).
    Falls back to hardcoded pricing if database pricing is not available.
    
    Args:
        provider: AI provider name (gemini, openai, claude, kimi, minimax)
        model: Optional model name (for OpenAI and Claude to determine pricing tier)
        input_tokens: Number of input tokens used
        output_tokens: Number of output tokens generated
    
    Returns:
        Dict with 'input_cost', 'output_cost', and 'total_cost' in USD
    """
    # Try to get pricing from database first
    try:
        from services.database.pricing_service import get_pricing_service
        pricing_service = get_pricing_service()
        pricing = await pricing_service.get_pricing(provider, model)
        
        if pricing:
            # Use database pricing
            input_price_per_1m = float(pricing.get("input_price_per_1m", 0))
            output_price_per_1m = float(pricing.get("output_price_per_1m", 0))
            pricing_type = pricing.get("pricing_type", "per_token")
            per_request_price = pricing.get("per_request_price")
            
            if pricing_type == "credit_based" or pricing_type == "per_request":
                # For credit-based or per-request pricing
                if per_request_price:
                    total_cost = float(per_request_price)
                    # Distribute proportionally if we have tokens
                    if input_tokens and output_tokens:
                        total_tokens = input_tokens + output_tokens
                        input_cost = (input_tokens / total_tokens) * total_cost
                        output_cost = (output_tokens / total_tokens) * total_cost
                    else:
                        input_cost = total_cost * 0.5
                        output_cost = total_cost * 0.5
                    
                    return {
                        "input_cost": input_cost,
                        "output_cost": output_cost,
                        "total_cost": total_cost
                    }
            
            # Standard per-token pricing
            if input_tokens is not None and output_tokens is not None:
                input_cost = (input_tokens / 1_000_000) * input_price_per_1m
                output_cost = (output_tokens / 1_000_000) * output_price_per_1m
                return {
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                    "total_cost": input_cost + output_cost
                }
    except Exception as e:
        logger.warning(f"Error getting pricing from database: {e}, falling back to hardcoded pricing")
    
    # Fallback to hardcoded pricing
    if input_tokens is None or output_tokens is None:
        # Fallback to estimated cost per call if tokens not available
        fallback_costs = {
            "gemini": 0.0001,
            "openai": 0.0002,
            "claude": 0.0003,
            "kimi": 0.005,
            "minimax": 0.0001
        }
        total = fallback_costs.get(provider, 0.0001)
        return {
            "input_cost": total * 0.5,  # Estimate 50/50 split
            "output_cost": total * 0.5,
            "total_cost": total
        }
    
    # Convert tokens to cost based on provider and model
    input_cost = 0.0
    output_cost = 0.0
    
    if provider == "gemini":
        model_name = (model or "").lower()
        # Gemini pricing varies by model - all charge for BOTH input and output
        if "2.0-flash" in model_name or "flash-exp" in model_name:
            # Gemini 2.0 Flash: Input $0.075/1M, Output $0.30/1M
            input_cost = (input_tokens / 1_000_000) * 0.075
            output_cost = (output_tokens / 1_000_000) * 0.30
        elif "1.5" in model_name or "pro" in model_name:
            # Gemini 1.5 Pro: Input $1.25/1M, Output $5/1M
            input_cost = (input_tokens / 1_000_000) * 1.25
            output_cost = (output_tokens / 1_000_000) * 5.0
        else:
            # Default to Flash pricing (most common)
            input_cost = (input_tokens / 1_000_000) * 0.075
            output_cost = (output_tokens / 1_000_000) * 0.30
    
    elif provider == "openai":
        model_name = (model or "").lower()
        # OpenAI pricing varies by model - all charge for BOTH input and output
        if "gpt-4o-mini" in model_name or "gpt-4.1-mini" in model_name:
            # GPT-4o-mini: Input $0.15/1M, Output $0.60/1M
            input_cost = (input_tokens / 1_000_000) * 0.15
            output_cost = (output_tokens / 1_000_000) * 0.60
        elif "gpt-4-turbo" in model_name or "gpt-4o" in model_name:
            # GPT-4 Turbo/GPT-4o: Input $5/1M, Output $15/1M
            input_cost = (input_tokens / 1_000_000) * 5.0
            output_cost = (output_tokens / 1_000_000) * 15.0
        elif "gpt-4" in model_name:
            # GPT-4 (standard): Input $30/1M, Output $60/1M
            input_cost = (input_tokens / 1_000_000) * 30.0
            output_cost = (output_tokens / 1_000_000) * 60.0
        else:
            # GPT-3.5-turbo or other: Input $1.50/1M, Output $2/1M
            input_cost = (input_tokens / 1_000_000) * 1.5
            output_cost = (output_tokens / 1_000_000) * 2.0
    
    elif provider == "claude":
        model_name = (model or "").lower()
        # Claude pricing varies by model - all charge for BOTH input and output
        if "opus" in model_name:
            # Claude Opus: Input $15/1M, Output $75/1M
            input_cost = (input_tokens / 1_000_000) * 15.0
            output_cost = (output_tokens / 1_000_000) * 75.0
        elif "sonnet" in model_name or "3.5" in model_name:
            # Claude 3.5 Sonnet: Input $3/1M, Output $15/1M
            input_cost = (input_tokens / 1_000_000) * 3.0
            output_cost = (output_tokens / 1_000_000) * 15.0
        elif "haiku" in model_name:
            # Claude Haiku: Input $0.25/1M, Output $1.25/1M
            input_cost = (input_tokens / 1_000_000) * 0.25
            output_cost = (output_tokens / 1_000_000) * 1.25
        else:
            # Default to Sonnet pricing if model not specified
            input_cost = (input_tokens / 1_000_000) * 3.0
            output_cost = (output_tokens / 1_000_000) * 15.0
    
    elif provider == "kimi":
        # Kimi uses credit-based pricing (não cobra por tokens, mas por request)
        # Distribuímos o custo estimado proporcionalmente
        total_estimated = 0.005
        total_tokens = (input_tokens or 0) + (output_tokens or 0)
        if total_tokens > 0:
            input_cost = (input_tokens / total_tokens) * total_estimated
            output_cost = (output_tokens / total_tokens) * total_estimated
        else:
            input_cost = total_estimated * 0.5
            output_cost = total_estimated * 0.5
    
    elif provider == "minimax":
        # Minimax - cobra por AMBOS
        input_cost = (input_tokens / 1_000_000) * 1.0
        output_cost = (output_tokens / 1_000_000) * 2.0
    
    else:
        # Unknown provider, use fallback
        total = 0.0001
        input_cost = total * 0.5
        output_cost = total * 0.5
    
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost
    }

