"""
Script to calculate and update costs for existing analyses in the database.

This script calculates costs based on token usage for all analyses that don't
have persisted costs yet.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import get_supabase_client
from utils.cost_calculator import calculate_cost_from_tokens
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def calculate_retroactive_costs():
    """Calculate and update costs for all analyses without persisted costs."""
    client = get_supabase_client()
    
    try:
        # Get all analyses without persisted costs (or with null costs)
        result = client.table("analyses")\
            .select("id, provider, model, input_tokens, output_tokens, input_cost, output_cost, total_cost")\
            .or_("input_cost.is.null,output_cost.is.null,total_cost.is.null")\
            .execute()
        
        analyses = result.data or []
        logger.info(f"Found {len(analyses)} analyses without persisted costs")
        
        if not analyses:
            logger.info("No analyses need cost calculation")
            return
        
        updated = 0
        errors = 0
        
        for analysis in analyses:
            try:
                analysis_id = analysis["id"]
                provider = analysis.get("provider", "unknown")
                input_tokens = analysis.get("input_tokens")
                output_tokens = analysis.get("output_tokens")
                
                # Skip if already has costs
                if (analysis.get("input_cost") is not None and 
                    analysis.get("output_cost") is not None and 
                    analysis.get("total_cost") is not None):
                    continue
                
                # Calculate costs
                cost_breakdown = await calculate_cost_from_tokens(
                    provider=provider,
                    model=analysis.get("model"),  # Use model from analysis if available
                    input_tokens=input_tokens,
                    output_tokens=output_tokens
                )
                
                # Update analysis with calculated costs
                update_result = client.table("analyses")\
                    .update({
                        "input_cost": cost_breakdown["input_cost"],
                        "output_cost": cost_breakdown["output_cost"],
                        "total_cost": cost_breakdown["total_cost"]
                    })\
                    .eq("id", analysis_id)\
                    .execute()
                
                if update_result.data:
                    updated += 1
                    if updated % 10 == 0:
                        logger.info(f"Updated {updated} analyses...")
                else:
                    errors += 1
                    logger.warning(f"Failed to update analysis {analysis_id}")
                    
            except Exception as e:
                errors += 1
                logger.error(f"Error updating analysis {analysis.get('id')}: {e}")
        
        logger.info(f"Cost calculation complete: {updated} updated, {errors} errors")
        
    except Exception as e:
        logger.error(f"Error calculating retroactive costs: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(calculate_retroactive_costs())

