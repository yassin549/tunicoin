"""User schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserResponse(BaseModel):
    """User response (public profile)."""
    id: UUID
    email: EmailStr
    is_verified: bool
    is_active: bool
    plan_id: str
    kyc_status: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "is_verified": True,
                "is_active": True,
                "plan_id": "free",
                "kyc_status": "pending",
                "created_at": "2024-01-01T00:00:00Z",
                "last_login": "2024-01-15T12:30:00Z"
            }
        }


class UserProfileResponse(BaseModel):
    """Detailed user profile response."""
    id: UUID
    email: EmailStr
    is_verified: bool
    is_active: bool
    is_admin: bool
    plan_id: str
    kyc_status: str
    twofa_enabled: bool
    stripe_customer_id: Optional[str] = None
    next_billing_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "is_verified": True,
                "is_active": True,
                "is_admin": False,
                "plan_id": "pro",
                "kyc_status": "approved",
                "twofa_enabled": True,
                "stripe_customer_id": "cus_...",
                "next_billing_date": "2024-02-01T00:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T00:00:00Z",
                "last_login": "2024-01-15T12:30:00Z"
            }
        }
