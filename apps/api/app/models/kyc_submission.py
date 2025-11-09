from sqlmodel import SQLModel, Field, Column
from typing import Optional
from datetime import datetime, date
from uuid import UUID, uuid4
from sqlalchemy import JSON


class KYCSubmission(SQLModel, table=True):
    """KYC (Know Your Customer) submission model."""

    __tablename__ = "kyc_submissions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, unique=True)
    
    # Submission status
    status: str = Field(max_length=20, default="pending")  # pending, approved, rejected, needs_review
    kyc_provider: Optional[str] = Field(default=None, max_length=50)  # 'jumio', 'onfido', 'manual'
    provider_reference_id: Optional[str] = Field(default=None, max_length=255)
    
    # Personal information
    full_name: str = Field(max_length=255)
    date_of_birth: date
    nationality: Optional[str] = Field(default=None, max_length=50)
    
    # Identity document
    id_type: str = Field(max_length=50)  # 'passport', 'drivers_license', 'national_id'
    id_number_encrypted: Optional[str] = Field(default=None)  # Encrypted ID number
    id_expiry_date: Optional[date] = Field(default=None)
    
    # Address information
    address_line1: str = Field(max_length=255)
    address_line2: Optional[str] = Field(default=None, max_length=255)
    city: str = Field(max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: str = Field(max_length=20)
    country: str = Field(max_length=2)  # ISO 2-letter country code
    
    # Contact
    phone: str = Field(max_length=50)
    
    # Investor status
    is_accredited_investor: bool = Field(default=False)
    accreditation_proof: Optional[str] = Field(default=None)  # URL or reference to proof document
    
    # Document storage (S3 URLs or file paths)
    documents: dict = Field(default={}, sa_column=Column(JSON))  # JSON field for document URLs
    
    # Review information
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = Field(default=None)
    reviewed_by: Optional[UUID] = Field(default=None, foreign_key="users.id")
    rejection_reason: Optional[str] = Field(default=None)
    
    # Compliance checks
    sanctions_check_passed: bool = Field(default=False)
    sanctions_check_date: Optional[datetime] = Field(default=None)
    aml_risk_score: Optional[float] = Field(default=None)  # 0-100 risk score
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "approved",
                "full_name": "John Doe",
                "date_of_birth": "1990-01-01",
                "id_type": "passport",
                "address_line1": "123 Main St",
                "city": "Paris",
                "postal_code": "75001",
                "country": "FR",
                "phone": "+33123456789",
                "is_accredited_investor": False,
            }
        }
