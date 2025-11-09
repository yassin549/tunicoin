from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date

from app.core.database import get_session as get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.models import User, KYCSubmission, InvestmentAccount
from app.schemas.investment import KYCSubmissionCreate, KYCSubmissionResponse

router = APIRouter(prefix="/kyc", tags=["kyc"])


@router.post("/submit", response_model=KYCSubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_kyc(
    kyc_data: KYCSubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit KYC information for verification."""
    
    # Check if user already has a KYC submission
    existing = await db.execute(
        select(KYCSubmission).where(KYCSubmission.user_id == current_user.id)
    )
    existing_kyc = existing.scalar_one_or_none()
    
    if existing_kyc:
        # If already approved, don't allow resubmission
        if existing_kyc.status == "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="KYC already approved. Contact support for changes."
            )
        
        # If pending or rejected, update existing submission
        existing_kyc.full_name = kyc_data.full_name
        existing_kyc.date_of_birth = kyc_data.date_of_birth
        existing_kyc.nationality = kyc_data.nationality
        existing_kyc.id_type = kyc_data.id_type
        existing_kyc.address_line1 = kyc_data.address_line1
        existing_kyc.address_line2 = kyc_data.address_line2
        existing_kyc.city = kyc_data.city
        existing_kyc.state = kyc_data.state
        existing_kyc.postal_code = kyc_data.postal_code
        existing_kyc.country = kyc_data.country
        existing_kyc.phone = kyc_data.phone
        existing_kyc.is_accredited_investor = kyc_data.is_accredited_investor
        existing_kyc.status = "pending"
        existing_kyc.submitted_at = datetime.utcnow()
        existing_kyc.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(existing_kyc)
        return existing_kyc
    
    # Create new KYC submission
    new_kyc = KYCSubmission(
        user_id=current_user.id,
        full_name=kyc_data.full_name,
        date_of_birth=kyc_data.date_of_birth,
        nationality=kyc_data.nationality,
        id_type=kyc_data.id_type,
        address_line1=kyc_data.address_line1,
        address_line2=kyc_data.address_line2,
        city=kyc_data.city,
        state=kyc_data.state,
        postal_code=kyc_data.postal_code,
        country=kyc_data.country,
        phone=kyc_data.phone,
        is_accredited_investor=kyc_data.is_accredited_investor,
        status="pending",
        submitted_at=datetime.utcnow(),
        kyc_provider="manual",  # For now, manual review
    )
    
    db.add(new_kyc)
    await db.commit()
    await db.refresh(new_kyc)
    
    return new_kyc


@router.get("/status", response_model=KYCSubmissionResponse)
async def get_kyc_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's KYC submission status."""
    
    result = await db.execute(
        select(KYCSubmission).where(KYCSubmission.user_id == current_user.id)
    )
    kyc = result.scalar_one_or_none()
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No KYC submission found. Please submit KYC information."
        )
    
    return kyc


@router.post("/upload-document/{document_type}")
async def upload_kyc_document(
    document_type: str,  # 'id_front', 'id_back', 'selfie', 'proof_of_address'
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a KYC document.
    Document types: id_front, id_back, selfie, proof_of_address
    """
    
    # Validate document type
    valid_types = ['id_front', 'id_back', 'selfie', 'proof_of_address', 'accreditation_proof']
    if document_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit"
        )
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, and PDF are allowed."
        )
    
    # Get or create KYC submission
    result = await db.execute(
        select(KYCSubmission).where(KYCSubmission.user_id == current_user.id)
    )
    kyc = result.scalar_one_or_none()
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Please submit KYC information first before uploading documents."
        )
    
    # TODO: Upload to S3 or file storage
    # For now, we'll store a placeholder URL
    file_url = f"/uploads/kyc/{current_user.id}/{document_type}_{file.filename}"
    
    # Update documents JSON field
    if kyc.documents is None:
        kyc.documents = {}
    
    kyc.documents[document_type] = {
        "filename": file.filename,
        "url": file_url,
        "uploaded_at": datetime.utcnow().isoformat(),
        "size": len(file_content),
        "content_type": file.content_type,
    }
    
    kyc.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(kyc)
    
    return {
        "message": "Document uploaded successfully",
        "document_type": document_type,
        "filename": file.filename,
        "url": file_url,
    }


@router.delete("/document/{document_type}")
async def delete_kyc_document(
    document_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a KYC document."""
    
    result = await db.execute(
        select(KYCSubmission).where(KYCSubmission.user_id == current_user.id)
    )
    kyc = result.scalar_one_or_none()
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No KYC submission found"
        )
    
    if kyc.status == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete documents from approved KYC submission"
        )
    
    if not kyc.documents or document_type not in kyc.documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document type '{document_type}' not found"
        )
    
    # TODO: Delete from S3 or file storage
    
    # Remove from documents JSON
    del kyc.documents[document_type]
    kyc.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Document deleted successfully", "document_type": document_type}


# ==================== Admin Endpoints ====================

@router.get("/admin/submissions", response_model=List[KYCSubmissionResponse])
async def get_all_kyc_submissions(
    status_filter: Optional[str] = None,
    limit: int = 50,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all KYC submissions (Admin only)."""
    
    query = select(KYCSubmission)
    
    if status_filter:
        query = query.where(KYCSubmission.status == status_filter)
    
    query = query.order_by(KYCSubmission.submitted_at.desc()).limit(limit)
    
    result = await db.execute(query)
    submissions = result.scalars().all()
    
    return submissions


@router.get("/admin/submissions/{kyc_id}", response_model=KYCSubmissionResponse)
async def get_kyc_submission(
    kyc_id: UUID,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific KYC submission (Admin only)."""
    
    result = await db.execute(
        select(KYCSubmission).where(KYCSubmission.id == kyc_id)
    )
    kyc = result.scalar_one_or_none()
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC submission not found"
        )
    
    return kyc


@router.post("/admin/submissions/{kyc_id}/approve")
async def approve_kyc(
    kyc_id: UUID,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a KYC submission (Admin only)."""
    
    result = await db.execute(
        select(KYCSubmission).where(KYCSubmission.id == kyc_id)
    )
    kyc = result.scalar_one_or_none()
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC submission not found"
        )
    
    if kyc.status == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="KYC already approved"
        )
    
    # Update KYC status
    kyc.status = "approved"
    kyc.reviewed_at = datetime.utcnow()
    kyc.reviewed_by = current_admin.id
    kyc.updated_at = datetime.utcnow()
    
    # Update user KYC status
    user_result = await db.execute(
        select(User).where(User.id == kyc.user_id)
    )
    user = user_result.scalar_one()
    user.kyc_status = "approved"
    user.kyc_verified_at = datetime.utcnow()
    
    # Activate any pending investment accounts
    accounts_result = await db.execute(
        select(InvestmentAccount).where(
            InvestmentAccount.user_id == kyc.user_id,
            InvestmentAccount.status == "pending_kyc"
        )
    )
    accounts = accounts_result.scalars().all()
    
    for account in accounts:
        account.status = "active"
        account.activated_at = datetime.utcnow()
        account.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(kyc)
    
    return {
        "message": "KYC approved successfully",
        "kyc_id": str(kyc.id),
        "user_id": str(kyc.user_id),
        "activated_accounts": len(accounts),
    }


@router.post("/admin/submissions/{kyc_id}/reject")
async def reject_kyc(
    kyc_id: UUID,
    rejection_reason: str,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject a KYC submission (Admin only)."""
    
    result = await db.execute(
        select(KYCSubmission).where(KYCSubmission.id == kyc_id)
    )
    kyc = result.scalar_one_or_none()
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC submission not found"
        )
    
    # Update KYC status
    kyc.status = "rejected"
    kyc.reviewed_at = datetime.utcnow()
    kyc.reviewed_by = current_admin.id
    kyc.rejection_reason = rejection_reason
    kyc.updated_at = datetime.utcnow()
    
    # Update user KYC status
    user_result = await db.execute(
        select(User).where(User.id == kyc.user_id)
    )
    user = user_result.scalar_one()
    user.kyc_status = "rejected"
    
    await db.commit()
    await db.refresh(kyc)
    
    return {
        "message": "KYC rejected",
        "kyc_id": str(kyc.id),
        "user_id": str(kyc.user_id),
        "reason": rejection_reason,
    }


@router.post("/admin/submissions/{kyc_id}/needs-review")
async def mark_kyc_needs_review(
    kyc_id: UUID,
    notes: str,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark KYC submission as needing additional review (Admin only)."""
    
    result = await db.execute(
        select(KYCSubmission).where(KYCSubmission.id == kyc_id)
    )
    kyc = result.scalar_one_or_none()
    
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC submission not found"
        )
    
    kyc.status = "needs_review"
    kyc.rejection_reason = notes
    kyc.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(kyc)
    
    return {
        "message": "KYC marked as needing review",
        "kyc_id": str(kyc.id),
        "notes": notes,
    }
