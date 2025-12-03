from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_owner, get_current_restaurant
from app.schemas import (
    RestaurantCreate, RestaurantUpdate, RestaurantResponse, APIResponse,
    CuisineResponse, RestaurantCuisineCreate, AddressCreate, AddressUpdate,
    AddressResponse, DocumentUploadResponse, PresignedUrlResponse,
    VerificationStatusResponse, MenuItemResponse, ReviewResponse,
    OnboardingStatusResponse
)
from app.models import (
    Owner, Restaurant, Cuisine, RestaurantCuisine, Address, Document,
    RestaurantTypeEnum, VerificationStatusEnum
)
from app.services.s3_service import s3_service
from app.services.verification_service import VerificationService
import uuid

router = APIRouter(prefix="/restaurant", tags=["Restaurant"])

@router.get("/onboarding-status", response_model=APIResponse)
def get_onboarding_status(
    current_owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    """Get the current onboarding status and next step"""
    # 1. Owner Details (Always true if we are here, as get_current_owner validates token)
    owner_completed = True
    
    # 2. Restaurant Details
    restaurant = db.query(Restaurant).filter(Restaurant.owner_id == current_owner.id).first()
    restaurant_completed = restaurant is not None
    
    # 3. Address Details
    address_completed = False
    if restaurant and restaurant.address:
        address_completed = True
        
    # 4. Cuisine Selection
    cuisine_completed = False
    if restaurant and restaurant.cuisines:
        cuisine_completed = True
        
    # 5. Document Upload
    doc_completed = False
    if restaurant:
        # Check for required docs: fssai_license, restaurant_photo
        docs = db.query(Document).filter(Document.restaurant_id == restaurant.id).all()
        doc_types = [d.document_type for d in docs]
        if "fssai_license" in doc_types and "restaurant_photo" in doc_types:
            doc_completed = True
            
    # Determine Next Step
    next_step = "owner_details"
    if owner_completed:
        next_step = "restaurant_details"
        if restaurant_completed:
            next_step = "address_details"
            if address_completed:
                next_step = "cuisine_selection"
                if cuisine_completed:
                    next_step = "document_upload"
                    if doc_completed:
                        next_step = "kyc_submitted"
                        
    # Verification Status
    verification_status = "pending"
    if restaurant:
        verification_status = restaurant.verification_status.value
        
    # If already submitted/approved, next_step might be different
    if verification_status in ["submitted", "under_review", "approved", "rejected"]:
         next_step = "kyc_submitted"

    return APIResponse(
        success=True,
        message="Onboarding status retrieved",
        data=OnboardingStatusResponse(
            owner_details_completed=owner_completed,
            restaurant_details_completed=restaurant_completed,
            address_details_completed=address_completed,
            cuisine_selection_completed=cuisine_completed,
            document_upload_completed=doc_completed,
            next_step=next_step,
            verification_status=verification_status
        ).dict()
    )



@router.get("/types", response_model=APIResponse)
def get_restaurant_types():
    """Get list of restaurant types"""
    types = [
        {"value": t.value, "label": t.value.replace("_", " ").title()}
        for t in RestaurantTypeEnum
    ]
    return APIResponse(
        success=True,
        message="Restaurant types retrieved successfully",
        data={"types": types}
    )


@router.post("/create", response_model=APIResponse)
def create_restaurant_details(
    restaurant_data: RestaurantCreate,
    current_owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    """Create restaurant details"""
    try:
        # Check if owner already has a restaurant
        existing_restaurant = db.query(Restaurant).filter(
            Restaurant.owner_id == current_owner.id
        ).first()
        
        if existing_restaurant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Restaurant already exists. Use PUT to update."
            )
        
        # Check if FSSAI license already exists
        existing_fssai = db.query(Restaurant).filter(
            Restaurant.fssai_license_number == restaurant_data.fssai_license_number
        ).first()
        
        if existing_fssai:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FSSAI license number already registered"
            )
        
        # Create restaurant
        restaurant = Restaurant(
            owner_id=current_owner.id,
            restaurant_name=restaurant_data.restaurant_name,
            restaurant_type=restaurant_data.restaurant_type,
            fssai_license_number=restaurant_data.fssai_license_number,
            opening_time=restaurant_data.opening_time,
            closing_time=restaurant_data.closing_time
        )
        
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)
        
        return APIResponse(
            success=True,
            message="Restaurant details saved successfully",
            data=RestaurantResponse.from_orm(restaurant).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save restaurant details: {str(e)}"
        )


@router.put("/details", response_model=APIResponse)
def update_restaurant_details(
    restaurant_data: RestaurantUpdate,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Update restaurant details"""
    try:
        if restaurant_data.restaurant_name:
            restaurant.restaurant_name = restaurant_data.restaurant_name
        
        if restaurant_data.restaurant_type:
            restaurant.restaurant_type = restaurant_data.restaurant_type
        
        if restaurant_data.opening_time:
            restaurant.opening_time = restaurant_data.opening_time
        
        if restaurant_data.closing_time:
            restaurant.closing_time = restaurant_data.closing_time
        
        db.commit()
        db.refresh(restaurant)
        
        return APIResponse(
            success=True,
            message="Restaurant details updated successfully",
            data=RestaurantResponse.from_orm(restaurant).dict()
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update restaurant details: {str(e)}"
        )


@router.put("/status", response_model=APIResponse)
def update_restaurant_status(
    is_open: bool,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Update restaurant open/closed status"""
    try:
        restaurant.is_open = is_open
        db.commit()
        db.refresh(restaurant)
        
        status_msg = "opened" if is_open else "closed"
        return APIResponse(
            success=True,
            message=f"Restaurant is now {status_msg}",
            data={"is_open": restaurant.is_open}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update status: {str(e)}"
        )


@router.get("/details", response_model=APIResponse)
def get_restaurant_details(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get restaurant details"""
    # Serialize basic info manually to avoid Pydantic validation errors on missing relationships
    restaurant_data = RestaurantResponse.from_orm(restaurant).dict()
    
    # Safely handle Address
    if restaurant.address:
        restaurant_data["address"] = AddressResponse.from_orm(restaurant.address).dict()
    else:
        restaurant_data["address"] = None
        
    # Safely handle Cuisines
    if restaurant.cuisines:
        restaurant_data["cuisines"] = [CuisineResponse.from_orm(rc.cuisine).dict() for rc in restaurant.cuisines if rc.cuisine]
    else:
        restaurant_data["cuisines"] = []
        
    # Safely handle Menu Items
    # (Optional: usually fetched separately, but included in full details)
    if restaurant.menu_items:
        restaurant_data["menu"] = [MenuItemResponse.from_orm(item).dict() for item in restaurant.menu_items if item.is_available]
    else:
        restaurant_data["menu"] = []
        
    # Safely handle Reviews
    if restaurant.reviews:
        # Limit to recent 5 reviews
        reviews = sorted(restaurant.reviews, key=lambda r: r.created_at, reverse=True)[:5]
        review_list = []
        for review in reviews:
            review_dict = ReviewResponse.from_orm(review).dict()
            if review.customer:
                review_dict["customer_name"] = review.customer.full_name or "Anonymous"
            review_list.append(review_dict)
        restaurant_data["reviews"] = review_list
    else:
        restaurant_data["reviews"] = []
    
    return APIResponse(
        success=True,
        message="Restaurant details retrieved successfully",
        data=restaurant_data
    )


@router.get("/cuisines/available", response_model=APIResponse)
def get_available_cuisines(db: Session = Depends(get_db)):
    """Get list of available cuisines"""
    cuisines = db.query(Cuisine).filter(Cuisine.is_active == True).all()
    return APIResponse(
        success=True,
        message="Cuisines retrieved successfully",
        data={
            "cuisines": [CuisineResponse.from_orm(c).dict() for c in cuisines]
        }
    )


@router.post("/cuisines", response_model=APIResponse)
def add_restaurant_cuisines(
    cuisine_data: RestaurantCuisineCreate,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Add cuisines to restaurant"""
    try:
        # Remove existing cuisines
        db.query(RestaurantCuisine).filter(
            RestaurantCuisine.restaurant_id == restaurant.id
        ).delete()
        
        # Add new cuisines
        for cuisine_id in cuisine_data.cuisine_ids:
            # Verify cuisine exists
            cuisine = db.query(Cuisine).filter(Cuisine.id == cuisine_id).first()
            if not cuisine:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cuisine with id {cuisine_id} not found"
                )
            
            restaurant_cuisine = RestaurantCuisine(
                restaurant_id=restaurant.id,
                cuisine_id=cuisine_id
            )
            db.add(restaurant_cuisine)
        
        db.commit()
        
        return APIResponse(
            success=True,
            message="Cuisines added successfully",
            data={"cuisine_ids": cuisine_data.cuisine_ids}
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add cuisines: {str(e)}"
        )


@router.post("/address", response_model=APIResponse)
def create_restaurant_address(
    address_data: AddressCreate,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Create restaurant address"""
    try:
        # Check if address already exists
        existing_address = db.query(Address).filter(
            Address.restaurant_id == restaurant.id
        ).first()
        
        if existing_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Address already exists. Use PUT to update."
            )
        
        address = Address(
            restaurant_id=restaurant.id,
            latitude=address_data.latitude,
            longitude=address_data.longitude,
            address_line_1=address_data.address_line_1,
            address_line_2=address_data.address_line_2,
            city=address_data.city,
            state=address_data.state,
            pincode=address_data.pincode,
            landmark=address_data.landmark
        )
        
        db.add(address)
        db.commit()
        db.refresh(address)
        
        return APIResponse(
            success=True,
            message="Address saved successfully",
            data=AddressResponse.from_orm(address).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save address: {str(e)}"
        )


@router.put("/address", response_model=APIResponse)
def update_restaurant_address(
    address_data: AddressUpdate,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Update restaurant address"""
    try:
        address = db.query(Address).filter(
            Address.restaurant_id == restaurant.id
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found. Use POST to create."
            )
        
        if address_data.latitude:
            address.latitude = address_data.latitude
        if address_data.longitude:
            address.longitude = address_data.longitude
        if address_data.address_line_1:
            address.address_line_1 = address_data.address_line_1
        if address_data.address_line_2 is not None:
            address.address_line_2 = address_data.address_line_2
        if address_data.city:
            address.city = address_data.city
        if address_data.state:
            address.state = address_data.state
        if address_data.pincode:
            address.pincode = address_data.pincode
        if address_data.landmark is not None:
            address.landmark = address_data.landmark
        
        db.commit()
        db.refresh(address)
        
        return APIResponse(
            success=True,
            message="Address updated successfully",
            data=AddressResponse.from_orm(address).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update address: {str(e)}"
        )


@router.post("/documents/presigned-url", response_model=APIResponse)
def get_presigned_upload_url(
    document_type: str,
    filename: str,
    content_type: str,
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """Get presigned URL for document upload"""
    try:
        # Validate document type
        valid_types = ["fssai_license", "restaurant_photo"]
        if document_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type. Must be one of: {valid_types}"
            )
        
        # Generate file key
        file_key = s3_service.generate_upload_key(document_type, filename)
        
        # Generate presigned URL
        upload_url = s3_service.generate_presigned_url(
            file_key=file_key,
            content_type=content_type
        )
        
        return APIResponse(
            success=True,
            message="Presigned URL generated successfully",
            data={
                "upload_url": upload_url,
                "file_key": file_key,
                "expires_in": 3600
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate presigned URL: {str(e)}"
        )


@router.post("/documents/confirm-upload", response_model=APIResponse)
def confirm_document_upload(
    document_type: str,
    file_key: str,
    filename: str,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Confirm document upload and save to database"""
    try:
        # Get file URL
        file_url = s3_service.get_file_url(file_key)
        
        # Check if document already exists
        existing_doc = db.query(Document).filter(
            Document.restaurant_id == restaurant.id,
            Document.document_type == document_type
        ).first()
        
        if existing_doc:
            # Update existing document
            existing_doc.file_url = file_url
            existing_doc.file_name = filename
        else:
            # Create new document
            document = Document(
                restaurant_id=restaurant.id,
                document_type=document_type,
                file_url=file_url,
                file_name=filename
            )
            db.add(document)
        
        db.commit()
        
        return APIResponse(
            success=True,
            message="Document uploaded successfully",
            data={
                "document_type": document_type,
                "file_url": file_url
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm document upload: {str(e)}"
        )


@router.post("/submit-kyc", response_model=APIResponse)
def submit_kyc(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Submit restaurant for KYC verification"""
    try:
        VerificationService.submit_for_verification(db, restaurant.id)
        
        return APIResponse(
            success=True,
            message="KYC submitted successfully. Your restaurant will be reviewed shortly.",
            data={
                "status": VerificationStatusEnum.SUBMITTED.value
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit KYC: {str(e)}"
        )


@router.get("/verification-status", response_model=APIResponse)
def get_verification_status(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get restaurant verification status"""
    status_data = VerificationService.get_verification_status(db, restaurant.id)
    
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    return APIResponse(
        success=True,
        message="Verification status retrieved successfully",
        data=status_data
    )


@router.get("/refresh-status", response_model=APIResponse)
def refresh_verification_status(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Refresh and get latest verification status"""
    db.refresh(restaurant)
    
    return APIResponse(
        success=True,
        message="Status refreshed successfully",
        data={
            "status": restaurant.verification_status.value,
            "verification_notes": restaurant.verification_notes,
            "updated_at": restaurant.updated_at
        }
    )
