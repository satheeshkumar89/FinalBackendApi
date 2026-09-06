from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_owner, get_current_customer, get_current_delivery_partner
from app.models import Notification, DeviceToken, Owner, Customer, DeliveryPartner
from app.schemas import NotificationResponse, DeviceTokenCreate, DeviceTokenResponse, APIResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=APIResponse)
def get_notifications(
    db: Session = Depends(get_db),
    owner: Owner = Depends(get_current_owner)
):
    """Get notifications for the current owner"""
    notifications = db.query(Notification).filter(
        Notification.owner_id == owner.id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    return APIResponse(
        success=True,
        message="Notifications retrieved successfully",
        data=[NotificationResponse.from_orm(n).dict() for n in notifications]
    )


@router.get("/customer", response_model=APIResponse)
def get_customer_notifications(
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer)
):
    """Get notifications for the current customer"""
    notifications = db.query(Notification).filter(
        Notification.customer_id == customer.id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    return APIResponse(
        success=True,
        message="Notifications retrieved successfully",
        data=[NotificationResponse.from_orm(n).dict() for n in notifications]
    )


@router.get("/delivery-partner", response_model=APIResponse)
def get_delivery_partner_notifications(
    db: Session = Depends(get_db),
    delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner)
):
    """Get notifications for the current delivery partner"""
    notifications = db.query(Notification).filter(
        Notification.delivery_partner_id == delivery_partner.id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    return APIResponse(
        success=True,
        message="Notifications retrieved successfully",
        data=[NotificationResponse.from_orm(n).dict() for n in notifications]
    )


@router.put("/{notification_id}/read", response_model=APIResponse)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notification.is_read = True
    db.commit()
    
    return APIResponse(
        success=True,
        message="Notification marked as read"
    )


@router.post("/device-token", response_model=APIResponse)
def register_device_token(
    request: DeviceTokenCreate,
    db: Session = Depends(get_db),
    owner: Owner = Depends(get_current_owner)
):
    """Register or update device token for owner"""
    token = db.query(DeviceToken).filter(DeviceToken.token == request.token).first()
    if token:
        token.owner_id = owner.id
        token.device_type = request.device_type
        token.is_active = True
    else:
        token = DeviceToken(
            owner_id=owner.id,
            token=request.token,
            device_type=request.device_type
        )
        db.add(token)
    
    db.commit()
    return APIResponse(
        success=True,
        message="Device token registered successfully"
    )


@router.post("/customer/device-token", response_model=APIResponse)
def register_customer_device_token(
    request: DeviceTokenCreate,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer)
):
    """Register or update device token for customer"""
    token = db.query(DeviceToken).filter(DeviceToken.token == request.token).first()
    if token:
        token.customer_id = customer.id
        token.device_type = request.device_type
        token.is_active = True
    else:
        token = DeviceToken(
            customer_id=customer.id,
            token=request.token,
            device_type=request.device_type
        )
        db.add(token)
    
    db.commit()
    return APIResponse(
        success=True,
        message="Device token registered successfully"
    )


@router.post("/delivery-partner/device-token", response_model=APIResponse)
def register_delivery_partner_device_token_alt(
    request: DeviceTokenCreate,
    db: Session = Depends(get_db),
    delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner)
):
    """Register or update device token for delivery partner"""
    token = db.query(DeviceToken).filter(DeviceToken.token == request.token).first()
    if token:
        token.delivery_partner_id = delivery_partner.id
        token.device_type = request.device_type
        token.is_active = True
    else:
        token = DeviceToken(
            delivery_partner_id=delivery_partner.id,
            token=request.token,
            device_type=request.device_type
        )
        db.add(token)
    
    db.commit()
    return APIResponse(
        success=True,
        message="Device token registered successfully"
    )
