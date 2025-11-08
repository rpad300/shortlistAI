"""
AI services package.

Provides abstraction layer for multiple AI providers.
"""

from .base import AIProvider, AIRequest, AIResponse, PromptType
from .gemini_provider import GeminiProvider
from .manager import AIManager

__all__ = [
    "AIProvider",
    "AIRequest",
    "AIResponse",
    "PromptType",
    "GeminiProvider",
    "AIManager",
]

