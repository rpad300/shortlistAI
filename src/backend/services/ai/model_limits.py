"""
Model token limits and capabilities.

Defines maximum tokens (output) and context window (input) for each AI model.
"""

from typing import Dict, Optional

# Maximum output tokens per model
# These are the limits for max_tokens/max_output_tokens parameter
MODEL_MAX_OUTPUT_TOKENS: Dict[str, int] = {
    # Gemini models
    "models/gemini-2.5-pro": 8192,
    "models/gemini-2.5-pro-latest": 8192,
    "models/gemini-2.5-pro-preview-03-25": 8192,
    "models/gemini-2.5-pro-preview-05-06": 8192,
    "models/gemini-2.5-pro-preview-06-05": 8192,
    "models/gemini-2.5-flash": 8192,
    "models/gemini-2.5-flash-lite": 8192,
    "models/gemini-2.5-flash-preview-05-20": 8192,
    "models/gemini-2.5-flash-lite-preview-06-17": 8192,
    "models/gemini-2.0-flash": 8192,
    "models/gemini-2.0-flash-exp": 8192,
    "models/gemini-2.0-pro-exp": 8192,
    "models/gemini-1.5-pro": 8192,
    "models/gemini-1.5-pro-latest": 8192,
    "models/gemini-1.5-flash": 8192,
    "models/gemini-1.5-flash-latest": 8192,
    "models/gemini-pro": 2048,
    
    # OpenAI models
    "gpt-4o": 16384,
    "gpt-4o-mini": 16384,
    "gpt-4-turbo": 4096,
    "gpt-4": 4096,
    "gpt-3.5-turbo": 4096,
    "gpt-4.1-mini": 16384,
    
    # Claude models
    "claude-3-5-sonnet-20241022": 8192,
    "claude-3-opus-20240229": 4096,
    "claude-3-sonnet-20240229": 4096,
    "claude-3-haiku-20240307": 4096,
    
    # Kimi K2 models
    "kimi-k2-0905": 8192,  # 256K context
    "kimi-k2": 8192,  # 128K context
    "kimi-k2-thinking": 8192,
    
    # MiniMax models
    "abab6.5-chat": 4096,
    "abab6.5s-chat": 4096,
}

# Context window (input tokens) per model
MODEL_CONTEXT_WINDOW: Dict[str, int] = {
    # Gemini models
    "models/gemini-2.5-pro": 2000000,  # 2M tokens
    "models/gemini-2.5-pro-latest": 2000000,
    "models/gemini-2.5-flash": 1000000,  # 1M tokens
    "models/gemini-2.5-flash-lite": 1000000,
    "models/gemini-2.0-flash": 1000000,
    "models/gemini-1.5-pro": 2000000,
    "models/gemini-1.5-flash": 1000000,
    "models/gemini-pro": 30720,
    
    # OpenAI models
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4": 8192,
    "gpt-3.5-turbo": 16385,
    "gpt-4.1-mini": 128000,
    
    # Claude models
    "claude-3-5-sonnet-20241022": 200000,
    "claude-3-opus-20240229": 200000,
    "claude-3-sonnet-20240229": 200000,
    "claude-3-haiku-20240307": 200000,
    
    # Kimi K2 models
    "kimi-k2-0905": 256000,  # 256K context
    "kimi-k2": 128000,  # 128K context
    "kimi-k2-thinking": 128000,
    
    # MiniMax models
    "abab6.5-chat": 128000,
    "abab6.5s-chat": 128000,
}


def get_max_output_tokens(model_name: str) -> int:
    """
    Get maximum output tokens for a model.
    
    Args:
        model_name: Full model identifier (e.g., "models/gemini-2.5-pro", "gpt-4o")
        
    Returns:
        Maximum output tokens, or 8192 as default
    """
    # Try exact match first
    if model_name in MODEL_MAX_OUTPUT_TOKENS:
        return MODEL_MAX_OUTPUT_TOKENS[model_name]
    
    # Try without "models/" prefix for Gemini
    if model_name.startswith("models/"):
        short_name = model_name.replace("models/", "")
        if short_name in MODEL_MAX_OUTPUT_TOKENS:
            return MODEL_MAX_OUTPUT_TOKENS[short_name]
    
    # Try with "models/" prefix
    if not model_name.startswith("models/"):
        prefixed = f"models/{model_name}"
        if prefixed in MODEL_MAX_OUTPUT_TOKENS:
            return MODEL_MAX_OUTPUT_TOKENS[prefixed]
    
    # Default: return high limit for modern models
    return 8192


def get_context_window(model_name: str) -> int:
    """
    Get context window (input tokens) for a model.
    
    Args:
        model_name: Full model identifier
        
    Returns:
        Context window size, or 128000 as default
    """
    # Try exact match first
    if model_name in MODEL_CONTEXT_WINDOW:
        return MODEL_CONTEXT_WINDOW[model_name]
    
    # Try without "models/" prefix for Gemini
    if model_name.startswith("models/"):
        short_name = model_name.replace("models/", "")
        if short_name in MODEL_CONTEXT_WINDOW:
            return MODEL_CONTEXT_WINDOW[short_name]
    
    # Try with "models/" prefix
    if not model_name.startswith("models/"):
        prefixed = f"models/{model_name}"
        if prefixed in MODEL_CONTEXT_WINDOW:
            return MODEL_CONTEXT_WINDOW[prefixed]
    
    # Default: return high limit for modern models
    return 128000

