from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.jwt_service import verify_token
from app.models import Owner, Restaurant, Customer, DeliveryPartner

security = HTTPBearer()


def get_current_owner(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Owner:
    """Get current authenticated owner from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    owner_id = payload.get("owner_id")
    if owner_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    owner = db.query(Owner).filter(Owner.id == owner_id).first()
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Owner not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not owner.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner account is inactive"
        )
    
    return owner


def get_current_restaurant(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db)
) -> Restaurant:
    """Get current owner's restaurant"""
    restaurant = db.query(Restaurant).filter(
        Restaurant.owner_id == owner.id,
        Restaurant.is_active == True
    ).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found. Please complete restaurant setup."
        )
    
    return restaurant


def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Customer:
    """Get current authenticated customer from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    customer_id = payload.get("customer_id")
    
    # If customer_id is missing, check if it's an owner token and try to find customer by phone
    if customer_id is None:
        owner_id = payload.get("owner_id")
        if owner_id:
            # It's an owner token, try to find corresponding customer by phone
            phone_number = payload.get("phone_number")
            if phone_number:
                customer = db.query(Customer).filter(Customer.phone_number == phone_number).first()
                if customer:
                    if not customer.is_active:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Customer account is inactive"
                        )
                    return customer
                    
        # If still no customer found or not an owner token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        phone_number = payload.get("phone_number")
        if phone_number:
            customer = db.query(Customer).filter(Customer.phone_number == phone_number).first()

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer account is inactive"
        )
    
    return customer


def get_current_delivery_partner(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> DeliveryPartner:
    """Get current authenticated delivery partner from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    delivery_partner_id = payload.get("delivery_partner_id")
    if delivery_partner_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    delivery_partner = db.query(DeliveryPartner).filter(DeliveryPartner.id == delivery_partner_id).first()
    if delivery_partner is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Delivery partner not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not delivery_partner.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Delivery partner account is inactive"
        )
    
    return delivery_partner

