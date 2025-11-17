from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging

from services.database import (
    get_company_profile_service,
    get_candidate_profile_service,
)
from uuid import UUID

router = APIRouter(prefix="/profiles", tags=["profiles"])

logger = logging.getLogger(__name__)


def _risk_level_order(level: str) -> int:
    order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    return order.get((level or "").lower(), -1)


@router.get("/company")
async def list_company_profiles(
    name: Optional[str] = Query(default=None, description="Company name contains filter"),
    industry: Optional[str] = Query(default=None, description="Basic info industry exact match"),
    min_risk_level: Optional[str] = Query(default=None, description="Minimum risk level: low|medium|high|critical"),
    limit: int = Query(default=50, ge=1, le=200),
) -> JSONResponse:
    try:
        svc = get_company_profile_service()

        # Base fetch: by name or industry to bound result size
        results: List[Dict[str, Any]] = []
        if name:
            # naive contains: Supabase doesn't support ilike contains easily; fetch and filter client-side
            res = svc.client.table(svc.table_profiles).select("*").limit(1000).execute()
            base = res.data or []
            results = [r for r in base if name.lower() in (r.get("company_name") or "").lower()]
        elif industry:
            # Fetch all and filter by JSONB field client-side (simpler than RPC here)
            res = svc.client.table(svc.table_profiles).select("*").limit(1000).execute()
            base = res.data or []
            results = [r for r in base if (r.get("basic_info") or {}).get("industry") == industry]
        else:
            res = svc.client.table(svc.table_profiles).select("*").limit(limit).execute()
            results = res.data or []

        # Apply risk filter
        if min_risk_level:
            min_ord = _risk_level_order(min_risk_level)
            filtered = []
            for r in results:
                risk = (r.get("reputation_risk_analysis") or {})
                lvl = risk.get("risk_level")
                if _risk_level_order(lvl) >= min_ord:
                    filtered.append(r)
            results = filtered

        # Cap limit
        results = results[:limit]

        return JSONResponse({"status": "success", "count": len(results), "items": results})
    except Exception as e:
        logger.error(f"Error listing company profiles: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/company/{profile_id}")
async def get_company_profile(profile_id: str) -> JSONResponse:
    try:
        svc = get_company_profile_service()
        res = svc.client.table(svc.table_profiles).select("*").eq("id", profile_id).limit(1).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Company profile not found")
        return JSONResponse({"status": "success", "item": res.data[0]})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/company/{profile_id}/positions")
async def list_company_positions(
    profile_id: str,
    status: Optional[str] = Query(default=None, description="Filter by status: active|closed|filled|cancelled"),
    limit: int = Query(default=50, ge=1, le=200),
) -> JSONResponse:
    try:
        svc = get_company_profile_service()
        query = svc.client.table(svc.table_positions).select("*").eq("company_profile_id", profile_id)
        if status:
            query = query.eq("status", status)
        res = query.limit(limit).execute()
        items = res.data or []
        return JSONResponse({"status": "success", "count": len(items), "items": items})
    except Exception as e:
        logger.error(f"Error listing company positions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/candidate")
async def list_candidate_profiles(
    candidate_name: Optional[str] = Query(default=None, description="Full name contains filter"),
    min_risk_level: Optional[str] = Query(default=None, description="Minimum risk level: low|medium|high|critical"),
    limit: int = Query(default=50, ge=1, le=200),
) -> JSONResponse:
    try:
        svc = get_candidate_profile_service()

        # Base fetch
        res = svc.client.table(svc.table_profiles).select("*").limit(1000).execute()
        results = res.data or []

        # Name contains
        if candidate_name:
            results = [r for r in results if candidate_name.lower() in (r.get("full_name") or "").lower()]

        # Risk filter
        if min_risk_level:
            min_ord = _risk_level_order(min_risk_level)
            filtered = []
            for r in results:
                risk = (r.get("social_media_risk_analysis") or {})
                lvl = risk.get("risk_level")
                if _risk_level_order(lvl) >= min_ord:
                    filtered.append(r)
            results = filtered

        results = results[:limit]
        return JSONResponse({"status": "success", "count": len(results), "items": results})
    except Exception as e:
        logger.error(f"Error listing candidate profiles: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/candidate/{profile_id}")
async def get_candidate_profile(profile_id: str) -> JSONResponse:
    try:
        svc = get_candidate_profile_service()
        res = svc.client.table(svc.table_profiles).select("*").eq("id", profile_id).limit(1).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Candidate profile not found")
        return JSONResponse({"status": "success", "item": res.data[0]})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching candidate profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


