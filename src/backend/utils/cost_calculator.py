"""
Cost calculation utilities for AI providers.

Calculates costs based on token usage for different AI providers.
All providers charge for BOTH input AND output tokens (with different prices).
"""

from typing import Optional, Dict


def calculate_cost_from_tokens(
    provider: str, 
    model: Optional[str], 
    input_tokens: Optional[int], 
    output_tokens: Optional[int]
) -> Dict[str, float]:
    """
    Calculate cost based on actual token usage.
    
    ALL providers charge for BOTH input AND output tokens (with different prices).
    
    Pricing per 1M tokens:
    - Gemini: Input $0.075/1M, Output $0.30/1M (gemini-2.0-flash-exp)
    - OpenAI GPT-4: Input $30/1M, Output $60/1M
    - OpenAI GPT-3.5: Input $1.50/1M, Output $2/1M
    - Claude Opus: Input $15/1M, Output $75/1M
    - Claude Sonnet: Input $3/1M, Output $15/1M
    - Claude Haiku: Input $0.25/1M, Output $1.25/1M
    - Kimi: ~$0.005 per request (credit-based, approximate) - não cobra por tokens
    - Minimax: Input $1/1M, Output $2/1M
    
    Args:
        provider: AI provider name (gemini, openai, claude, kimi, minimax)
        model: Optional model name (for OpenAI and Claude to determine pricing tier)
        input_tokens: Number of input tokens used
        output_tokens: Number of output tokens generated
    
    Returns:
        Dict with 'input_cost', 'output_cost', and 'total_cost' in USD
    """
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
        # Gemini 2.0 Flash pricing - cobra por AMBOS
        input_cost = (input_tokens / 1_000_000) * 0.075
        output_cost = (output_tokens / 1_000_000) * 0.30
    
    elif provider == "openai":
        model_name = (model or "").lower()
        if "gpt-4" in model_name:
            # GPT-4 pricing - cobra por AMBOS
            input_cost = (input_tokens / 1_000_000) * 30.0
            output_cost = (output_tokens / 1_000_000) * 60.0
        else:
            # GPT-3.5 pricing - cobra por AMBOS
            input_cost = (input_tokens / 1_000_000) * 1.5
            output_cost = (output_tokens / 1_000_000) * 2.0
    
    elif provider == "claude":
        model_name = (model or "").lower()
        if "opus" in model_name:
            # Claude Opus - cobra por AMBOS
            input_cost = (input_tokens / 1_000_000) * 15.0
            output_cost = (output_tokens / 1_000_000) * 75.0
        elif "sonnet" in model_name:
            # Claude Sonnet - cobra por AMBOS
            input_cost = (input_tokens / 1_000_000) * 3.0
            output_cost = (output_tokens / 1_000_000) * 15.0
        else:  # Haiku
            # Claude Haiku - cobra por AMBOS
            input_cost = (input_tokens / 1_000_000) * 0.25
            output_cost = (output_tokens / 1_000_000) * 1.25
    
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

