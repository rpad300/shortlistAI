"""
Pydantic models for Candidate entity.

Defines request/response schemas for candidate-related operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class CandidateBase(BaseModel):
    """Base candidate model with common fields."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=100)


class CandidateCreate(CandidateBase):
    """Model for creating a new candidate."""
    consent_given: bool = Field(..., description="User must give consent to store data")
    consent_timestamp: Optional[datetime] = None


class CandidateUpdate(BaseModel):
    """Model for updating candidate information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=100)


class CandidateInDB(CandidateBase):
    """Model representing a candidate as stored in database."""
    id: UUID
    consent_given: bool
    consent_timestamp: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CandidateResponse(CandidateInDB):
    """Model for candidate API responses."""
    pass

