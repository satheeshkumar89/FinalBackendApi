from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_owner
from app.schemas import OwnerCreate, OwnerUpdate, OwnerResponse, APIResponse
from app.models import Owner

router = APIRouter(prefix="/owner", tags=["Owner"])


@router.post("/details", response_model=APIResponse)
def create_or_update_owner_details(
    owner_data: OwnerCreate,
    current_owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    """Create or update owner details"""
    try:
        # Check if email already exists for another owner
        existing_owner = db.query(Owner).filter(
            Owner.email == owner_data.email,
            Owner.id != current_owner.id
        ).first()
        
        if existing_owner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Update owner details
        current_owner.full_name = owner_data.full_name
        current_owner.email = owner_data.email
        
        db.commit()
        db.refresh(current_owner)
        
        return APIResponse(
            success=True,
            message="Owner details saved successfully",
            data=OwnerResponse.from_orm(current_owner).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save owner details: {str(e)}"
        )


@router.put("/details", response_model=APIResponse)
def update_owner_details(
    owner_data: OwnerUpdate,
    current_owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    """Update owner details"""
    try:
        if owner_data.full_name:
            current_owner.full_name = owner_data.full_name
        
        if owner_data.email:
            # Check if email already exists
            existing_owner = db.query(Owner).filter(
                Owner.email == owner_data.email,
                Owner.id != current_owner.id
            ).first()
            
            if existing_owner:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            current_owner.email = owner_data.email
        
        db.commit()
        db.refresh(current_owner)
        
        return APIResponse(
            success=True,
            message="Owner details updated successfully",
            data=OwnerResponse.from_orm(current_owner).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update owner details: {str(e)}"
        )


@router.get("/details", response_model=APIResponse)
def get_owner_details(
    current_owner: Owner = Depends(get_current_owner)
):
    """Get current owner details"""
    return APIResponse(
        success=True,
        message="Owner details retrieved successfully",
        data=OwnerResponse.from_orm(current_owner).dict()
    )
