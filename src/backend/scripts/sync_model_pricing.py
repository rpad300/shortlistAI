"""
Script to sync model pricing from provider documentation/APIs.

This script populates the ai_model_pricing table with current pricing information.
Since most providers don't expose pricing via API, we use documented pricing.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

# Load environment variables
from dotenv import load_dotenv
project_root = Path(__file__).parent.parent.parent
env_file = project_root / '.env'
if env_file.exists():
    load_dotenv(env_file)

from services.database.pricing_service import get_pricing_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def sync_openai_pricing(pricing_service):
    """Sync OpenAI model pricing."""
    logger.info("Syncing OpenAI pricing...")
    
    # OpenAI pricing (as of 2024/2025)
    models = [
        {
            "model_name": "gpt-4o-mini",
            "display_name": "GPT-4o Mini",
            "input_price": 0.15,
            "output_price": 0.60,
            "context_window": 128000,
            "max_output": 16384
        },
        {
            "model_name": "gpt-4.1-mini",
            "display_name": "GPT-4.1 Mini",
            "input_price": 0.15,
            "output_price": 0.60,
            "context_window": 128000,
            "max_output": 16384
        },
        {
            "model_name": "gpt-4o",
            "display_name": "GPT-4o",
            "input_price": 5.0,
            "output_price": 15.0,
            "context_window": 128000,
            "max_output": 16384
        },
        {
            "model_name": "gpt-4-turbo",
            "display_name": "GPT-4 Turbo",
            "input_price": 10.0,
            "output_price": 30.0,
            "context_window": 128000,
            "max_output": 4096
        },
        {
            "model_name": "gpt-4",
            "display_name": "GPT-4",
            "input_price": 30.0,
            "output_price": 60.0,
            "context_window": 8192,
            "max_output": 4096
        },
        {
            "model_name": "gpt-3.5-turbo",
            "display_name": "GPT-3.5 Turbo",
            "input_price": 1.5,
            "output_price": 2.0,
            "context_window": 16385,
            "max_output": 4096
        },
    ]
    
    for model in models:
        await pricing_service.upsert_pricing(
            provider="openai",
            model_name=model["model_name"],
            input_price_per_1m=model["input_price"],
            output_price_per_1m=model["output_price"],
            model_display_name=model["display_name"],
            context_window=model.get("context_window"),
            max_output_tokens=model.get("max_output"),
            source="documentation",
            updated_by="system"
        )


async def sync_claude_pricing(pricing_service):
    """Sync Claude model pricing."""
    logger.info("Syncing Claude pricing...")
    
    # Anthropic Claude pricing (as of 2024/2025)
    models = [
        {
            "model_name": "claude-3-5-opus-20241022",
            "display_name": "Claude 3.5 Opus",
            "input_price": 15.0,
            "output_price": 75.0,
            "context_window": 200000,
            "max_output": 8192
        },
        {
            "model_name": "claude-3-5-sonnet-20241022",
            "display_name": "Claude 3.5 Sonnet",
            "input_price": 3.0,
            "output_price": 15.0,
            "context_window": 200000,
            "max_output": 8192
        },
        {
            "model_name": "claude-3-5-haiku-20241022",
            "display_name": "Claude 3.5 Haiku",
            "input_price": 0.25,
            "output_price": 1.25,
            "context_window": 200000,
            "max_output": 8192
        },
        {
            "model_name": "claude-3-opus-20240229",
            "display_name": "Claude 3 Opus",
            "input_price": 15.0,
            "output_price": 75.0,
            "context_window": 200000,
            "max_output": 4096
        },
        {
            "model_name": "claude-3-sonnet-20240229",
            "display_name": "Claude 3 Sonnet",
            "input_price": 3.0,
            "output_price": 15.0,
            "context_window": 200000,
            "max_output": 4096
        },
        {
            "model_name": "claude-3-haiku-20240307",
            "display_name": "Claude 3 Haiku",
            "input_price": 0.25,
            "output_price": 1.25,
            "context_window": 200000,
            "max_output": 4096
        },
    ]
    
    for model in models:
        await pricing_service.upsert_pricing(
            provider="claude",
            model_name=model["model_name"],
            input_price_per_1m=model["input_price"],
            output_price_per_1m=model["output_price"],
            model_display_name=model["display_name"],
            context_window=model.get("context_window"),
            max_output_tokens=model.get("max_output"),
            source="documentation",
            updated_by="system"
        )


async def sync_gemini_pricing(pricing_service):
    """Sync Gemini model pricing."""
    logger.info("Syncing Gemini pricing...")
    
    # Google Gemini pricing (as of 2024/2025)
    models = [
        {
            "model_name": "models/gemini-2.5-flash-lite",
            "display_name": "Gemini 2.5 Flash Lite",
            "input_price": 0.075,
            "output_price": 0.30,
            "context_window": 1000000,
            "max_output": 8192
        },
        {
            "model_name": "models/gemini-2.5-flash",
            "display_name": "Gemini 2.5 Flash",
            "input_price": 0.075,
            "output_price": 0.30,
            "context_window": 1000000,
            "max_output": 8192
        },
        {
            "model_name": "models/gemini-2.5-pro-latest",
            "display_name": "Gemini 2.5 Pro",
            "input_price": 1.25,
            "output_price": 5.0,
            "context_window": 2000000,
            "max_output": 8192
        },
        {
            "model_name": "models/gemini-2.0-flash-exp",
            "display_name": "Gemini 2.0 Flash Experimental",
            "input_price": 0.075,
            "output_price": 0.30,
            "context_window": 1000000,
            "max_output": 8192
        },
        {
            "model_name": "models/gemini-1.5-pro-latest",
            "display_name": "Gemini 1.5 Pro",
            "input_price": 1.25,
            "output_price": 5.0,
            "context_window": 2000000,
            "max_output": 8192
        },
        {
            "model_name": "models/gemini-1.5-flash-latest",
            "display_name": "Gemini 1.5 Flash",
            "input_price": 0.075,
            "output_price": 0.30,
            "context_window": 1000000,
            "max_output": 8192
        },
    ]
    
    for model in models:
        await pricing_service.upsert_pricing(
            provider="gemini",
            model_name=model["model_name"],
            input_price_per_1m=model["input_price"],
            output_price_per_1m=model["output_price"],
            model_display_name=model["display_name"],
            context_window=model.get("context_window"),
            max_output_tokens=model.get("max_output"),
            source="documentation",
            updated_by="system"
        )


async def sync_minimax_pricing(pricing_service):
    """Sync Minimax model pricing."""
    logger.info("Syncing Minimax pricing...")
    
    # Minimax pricing (as of 2024/2025)
    models = [
        {
            "model_name": "abab6.5-chat",
            "display_name": "ABAB 6.5 Chat",
            "input_price": 1.0,
            "output_price": 2.0,
            "context_window": 128000,
            "max_output": 4096
        },
        {
            "model_name": "abab6.5s-chat",
            "display_name": "ABAB 6.5S Chat",
            "input_price": 0.5,
            "output_price": 1.0,
            "context_window": 128000,
            "max_output": 4096
        },
    ]
    
    for model in models:
        await pricing_service.upsert_pricing(
            provider="minimax",
            model_name=model["model_name"],
            input_price_per_1m=model["input_price"],
            output_price_per_1m=model["output_price"],
            model_display_name=model["display_name"],
            context_window=model.get("context_window"),
            max_output_tokens=model.get("max_output"),
            source="documentation",
            updated_by="system"
        )


async def sync_kimi_pricing(pricing_service):
    """Sync Kimi model pricing."""
    logger.info("Syncing Kimi pricing...")
    
    # Kimi uses credit-based pricing (per request, not per token)
    models = [
        {
            "model_name": "kimi-k2-0905",
            "display_name": "Kimi K2 0905",
            "input_price": 0.0,  # Credit-based
            "output_price": 0.0,  # Credit-based
            "per_request_price": 0.005,  # Approximate per request
            "pricing_type": "credit_based",
            "context_window": 256000,
            "max_output": 8192
        },
        {
            "model_name": "kimi-k2",
            "display_name": "Kimi K2",
            "input_price": 0.0,
            "output_price": 0.0,
            "per_request_price": 0.005,
            "pricing_type": "credit_based",
            "context_window": 128000,
            "max_output": 8192
        },
        {
            "model_name": "kimi-k2-thinking",
            "display_name": "Kimi K2 Thinking",
            "input_price": 0.0,
            "output_price": 0.0,
            "per_request_price": 0.005,
            "pricing_type": "credit_based",
            "context_window": 128000,
            "max_output": 8192
        },
    ]
    
    for model in models:
        await pricing_service.upsert_pricing(
            provider="kimi",
            model_name=model["model_name"],
            input_price_per_1m=model["input_price"],
            output_price_per_1m=model["output_price"],
            model_display_name=model["display_name"],
            pricing_type=model.get("pricing_type", "per_token"),
            per_request_price=model.get("per_request_price"),
            context_window=model.get("context_window"),
            max_output_tokens=model.get("max_output"),
            source="documentation",
            updated_by="system"
        )


async def sync_all_pricing():
    """Sync pricing for all providers."""
    pricing_service = get_pricing_service()
    
    await sync_openai_pricing(pricing_service)
    await sync_claude_pricing(pricing_service)
    await sync_gemini_pricing(pricing_service)
    await sync_minimax_pricing(pricing_service)
    await sync_kimi_pricing(pricing_service)
    
    logger.info("Pricing sync complete!")


if __name__ == "__main__":
    asyncio.run(sync_all_pricing())

