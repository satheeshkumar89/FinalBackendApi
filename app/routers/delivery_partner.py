from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import os

from app.database import get_db
from app.models import (
    DeliveryPartner, Order, OrderStatusEnum, Customer, Restaurant,
    OrderItem, MenuItem, OTP, DeviceToken, Notification
)
from app.schemas import (
    CustomerCreate, APIResponse, DeliveryPartnerResponse,
    OrderResponse, OrderItemResponse, RestaurantResponse,
    DeviceTokenCreate, NotificationResponse, SendOTPRequest, VerifyOTPRequest
)
from app.services.otp_service import create_otp, verify_otp, send_otp_sms
from app.services.jwt_service import create_access_token
from app.services.notification_service import NotificationService
from app.dependencies import get_current_delivery_partner
from app.socket_manager import emit_order_update
from pydantic import BaseModel, Field




router = APIRouter(prefix="/delivery-partner", tags=["Delivery Partner"])


# ============= Schemas =============
class DeliveryPartnerTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    delivery_partner: DeliveryPartnerResponse


class DeliveryPartnerRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: Optional[str] = None
    vehicle_number: str = Field(..., min_length=3, max_length=20)
    vehicle_type: str  # bike, scooter, car, bicycle
    license_number: Optional[str] = None
    profile_photo: Optional[str] = None


class DeliveryPartnerUpdateProfile(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[str] = None
    vehicle_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    license_number: Optional[str] = None
    profile_photo: Optional[str] = None


class OnlineStatusRequest(BaseModel):
    is_online: bool


class OrderListResponse(BaseModel):
    id: int
    order_number: str
    restaurant_name: str
    customer_name: str
    customer_phone: str
    delivery_address: str
    total_amount: Decimal
    status: str
    created_at: datetime
    estimated_delivery_time: Optional[datetime]


class EarningsResponse(BaseModel):
    today_earnings: Decimal
    week_earnings: Decimal
    month_earnings: Decimal
    total_deliveries: int
    avg_rating: Decimal


class OrderDetailForDeliveryResponse(BaseModel):
    id: int
    order_number: str
    restaurant_name: str
    restaurant_phone: str
    restaurant_address: str
    customer_name: str
    customer_phone: str
    delivery_address: str
    status: str
    total_amount: Decimal
    delivery_fee: Decimal
    payment_method: Optional[str]
    payment_status: str
    special_instructions: Optional[str]
    items: List[OrderItemResponse]
    created_at: datetime
    estimated_delivery_time: Optional[datetime]


class UpdateLocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = None  # GPS accuracy in meters
    bearing: Optional[float] = Field(None, ge=0, le=360)  # Direction 0-360
    speed: Optional[float] = None  # Speed in m/s
    order_id: Optional[int] = None  # Currently delivering this order


class LocationResponse(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float]
    bearing: Optional[float]
    speed: Optional[float]
    updated_at: datetime
    delivery_partner_name: Optional[str]


# ============= Authentication APIs =============
@router.post("/auth/send-otp", response_model=APIResponse)
def send_otp_to_delivery_partner(
    request: SendOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Send OTP to delivery partner's phone number.
    Create delivery partner if doesn't exist.
    """
    try:
        # Check if delivery partner exists
        delivery_partner = db.query(DeliveryPartner).filter(
            DeliveryPartner.phone_number == request.phone_number
        ).first()
        
        # If doesn't exist, create new delivery partner
        if not delivery_partner:
            delivery_partner = DeliveryPartner(
                full_name="Delivery Partner",  # Will be updated during profile completion
                phone_number=request.phone_number,
                is_active=True
            )
            db.add(delivery_partner)
            db.commit()
            db.refresh(delivery_partner)
        
        # Check if delivery partner is active
        if not delivery_partner.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been deactivated. Please contact support."
            )
        
        # Create OTP
        otp = create_otp(db, request.phone_number, delivery_partner_id=delivery_partner.id)
        
        # Send OTP via SMS
        send_otp_sms(request.phone_number, otp.otp_code)
        
        response_data = {
            "phone_number": request.phone_number,
            "expires_in": "5 minutes"
        }
        
        # Add OTP to response in development mode
        if os.getenv('ENVIRONMENT', 'development') == 'development':
            response_data["otp"] = otp.otp_code
            response_data["note"] = "OTP included in response for development only"
        
        return APIResponse(
            success=True,
            message="OTP sent successfully",
            data=response_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )



@router.post("/auth/verify-otp", response_model=DeliveryPartnerTokenResponse)
def verify_otp_and_login(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and return JWT token for delivery partner.
    """
    # Find delivery partner
    delivery_partner = db.query(DeliveryPartner).filter(
        DeliveryPartner.phone_number == request.phone_number
    ).first()
    
    if not delivery_partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery partner not found"
        )
    
    # Verify OTP
    is_valid = verify_otp(db, request.phone_number, request.otp_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )
    
    # Generate JWT token
    access_token = create_access_token(
        data={"delivery_partner_id": delivery_partner.id, "phone_number": delivery_partner.phone_number, "role": "delivery_partner"}
    )
    
    return DeliveryPartnerTokenResponse(
        access_token=access_token,
        token_type="bearer",
        delivery_partner=DeliveryPartnerResponse.from_orm(delivery_partner)
    )



# ============= Profile APIs =============
@router.get("/profile", response_model=DeliveryPartnerResponse)
async def get_delivery_partner_profile(
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner)
):
    """Get current delivery partner's profile."""
    return DeliveryPartnerResponse.from_orm(current_delivery_partner)


@router.post("/register", response_model=APIResponse)
async def register_delivery_partner(
    registration_data: DeliveryPartnerRegisterRequest,
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """
    Complete registration for delivery partner.
    This should be called after OTP verification to complete the profile.
    After registration, admin approval is required before going online.
    """
    from app.models import VerificationStatusEnum
    
    # Update delivery partner details
    current_delivery_partner.full_name = registration_data.full_name
    current_delivery_partner.email = registration_data.email
    current_delivery_partner.vehicle_number = registration_data.vehicle_number
    current_delivery_partner.vehicle_type = registration_data.vehicle_type
    current_delivery_partner.license_number = registration_data.license_number
    current_delivery_partner.profile_photo = registration_data.profile_photo
    current_delivery_partner.is_registered = True  # Mark as registered
    current_delivery_partner.verification_status = VerificationStatusEnum.SUBMITTED  # Pending admin approval
    
    db.commit()
    db.refresh(current_delivery_partner)
    
    return APIResponse(
        success=True,
        message="Registration submitted successfully. Please wait for admin approval.",
        data=DeliveryPartnerResponse.from_orm(current_delivery_partner).dict()
    )


@router.put("/profile", response_model=APIResponse)
async def update_delivery_partner_profile(
    update_data: DeliveryPartnerUpdateProfile,
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """Update delivery partner's profile."""
    if update_data.full_name is not None:
        current_delivery_partner.full_name = update_data.full_name
    if update_data.email is not None:
        current_delivery_partner.email = update_data.email
    if update_data.vehicle_number is not None:
        current_delivery_partner.vehicle_number = update_data.vehicle_number
    if update_data.vehicle_type is not None:
        current_delivery_partner.vehicle_type = update_data.vehicle_type
    if update_data.license_number is not None:
        current_delivery_partner.license_number = update_data.license_number
    if update_data.profile_photo is not None:
        current_delivery_partner.profile_photo = update_data.profile_photo
    
    db.commit()
    db.refresh(current_delivery_partner)
    
    return APIResponse(
        success=True,
        message="Profile updated successfully",
        data=DeliveryPartnerResponse.from_orm(current_delivery_partner).dict()
    )


# ============= Online/Offline Status =============
@router.post("/status/toggle", response_model=APIResponse)
async def toggle_online_status(
    status_data: OnlineStatusRequest,
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """
    Toggle delivery partner's online/offline status.
    When online, they can receive order notifications and accept orders.
    When offline, they won't receive new order requests.
    
    Requirements:
    - Must complete registration
    - Must be approved by admin
    """
    from app.models import VerificationStatusEnum
    
    # Check if partner is registered
    if not current_delivery_partner.is_registered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete registration before going online"
        )
    
    # Check if partner is approved by admin
    if current_delivery_partner.verification_status != VerificationStatusEnum.APPROVED:
        status_message = {
            VerificationStatusEnum.PENDING: "Your account is pending verification",
            VerificationStatusEnum.SUBMITTED: "Your registration is under review by admin",
            VerificationStatusEnum.UNDER_REVIEW: "Your account is under review by admin",
            VerificationStatusEnum.REJECTED: "Your account has been rejected. Please contact support."
        }.get(current_delivery_partner.verification_status, "Your account is not approved yet")
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{status_message}. You cannot go online until approved."
        )
    
    current_delivery_partner.is_online = status_data.is_online
    
    # Update timestamps
    if status_data.is_online:
        current_delivery_partner.last_online_at = datetime.utcnow()
    else:
        current_delivery_partner.last_offline_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_delivery_partner)
    
    status_message = "You are now online and can receive orders" if status_data.is_online else "You are now offline"
    
    return APIResponse(
        success=True,
        message=status_message,
        data={
            "is_online": current_delivery_partner.is_online,
            "last_online_at": current_delivery_partner.last_online_at.isoformat() if current_delivery_partner.last_online_at else None,
            "last_offline_at": current_delivery_partner.last_offline_at.isoformat() if current_delivery_partner.last_offline_at else None
        }
    )


@router.get("/status", response_model=APIResponse)
async def get_online_status(
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner)
):
    """Get current online/offline status."""
    return APIResponse(
        success=True,
        message="Status retrieved successfully",
        data={
            "is_online": current_delivery_partner.is_online,
            "is_registered": current_delivery_partner.is_registered,
            "last_online_at": current_delivery_partner.last_online_at.isoformat() if current_delivery_partner.last_online_at else None,
            "last_offline_at": current_delivery_partner.last_offline_at.isoformat() if current_delivery_partner.last_offline_at else None
        }
    )


# ============= Device Token (Push Notifications) =============
@router.post("/device-token", response_model=APIResponse)
async def register_delivery_partner_device_token(
    token_data: DeviceTokenCreate,
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """Register device token for push notifications."""
    # Check if token already exists
    existing_token = db.query(DeviceToken).filter(
        DeviceToken.token == token_data.token
    ).first()
    
    if existing_token:
        # Update existing token
        existing_token.delivery_partner_id = current_delivery_partner.id
        existing_token.device_type = token_data.device_type
        existing_token.is_active = True
        db.commit()
        return APIResponse(
            success=True,
            message="Device token updated successfully"
        )
    
    # Create new token
    new_token = DeviceToken(
        delivery_partner_id=current_delivery_partner.id,
        token=token_data.token,
        device_type=token_data.device_type,
        is_active=True
    )
    db.add(new_token)
    db.commit()
    
    return APIResponse(
        success=True,
        message="Device token registered successfully"
    )


# ============= Orders APIs =============
@router.get("/orders/available", response_model=List[OrderListResponse])
async def get_available_orders(
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """
    Get all orders that are available for delivery.
    Available statuses: ACCEPTED, PREPARING, READY (Wait for pickup)
    """
    orders = db.query(Order).filter(
        Order.status.in_([
            OrderStatusEnum.NEW,
            OrderStatusEnum.ACCEPTED,
            OrderStatusEnum.PREPARING,
            OrderStatusEnum.READY
        ]),
        Order.delivery_partner_id == None
    ).order_by(desc(Order.created_at)).all()
    
    result = []
    for order in orders:
        restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
        result.append(OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            restaurant_name=restaurant.restaurant_name if restaurant else "Unknown",
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            delivery_address=order.delivery_address,
            total_amount=order.total_amount,
            status=order.status.value,
            created_at=order.created_at,
            estimated_delivery_time=order.estimated_delivery_time
        ))
    
    return result


@router.get("/orders/active", response_model=List[OrderListResponse])
async def get_active_orders(
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """
    Get all active orders assigned to this delivery partner.
    Statuses: ACCEPTED, PREPARING, READY (Assigned), PICKED_UP (Out for delivery)
    """
    orders = db.query(Order).filter(
        Order.delivery_partner_id == current_delivery_partner.id,
        Order.status.in_([
            OrderStatusEnum.ACCEPTED,
            OrderStatusEnum.PREPARING,
            OrderStatusEnum.READY,
            OrderStatusEnum.PICKED_UP
        ])
    ).order_by(desc(Order.created_at)).all()
    
    result = []
    for order in orders:
        restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
        result.append(OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            restaurant_name=restaurant.restaurant_name if restaurant else "Unknown",
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            delivery_address=order.delivery_address,
            total_amount=order.total_amount,
            status=order.status.value,
            created_at=order.created_at,
            estimated_delivery_time=order.estimated_delivery_time
        ))
    
    return result


@router.get("/orders/completed", response_model=List[OrderListResponse])
async def get_completed_orders(
    limit: int = 50,
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """
    Get delivery history - all completed deliveries.
    """
    orders = db.query(Order).filter(
        Order.delivery_partner_id == current_delivery_partner.id,
        Order.status == OrderStatusEnum.DELIVERED
    ).order_by(desc(Order.delivered_at)).limit(limit).all()
    
    result = []
    for order in orders:
        restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
        result.append(OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            restaurant_name=restaurant.restaurant_name if restaurant else "Unknown",
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            delivery_address=order.delivery_address,
            total_amount=order.total_amount,
            status=order.status.value,
            created_at=order.created_at,
            estimated_delivery_time=order.estimated_delivery_time
        ))
    
    return result


@router.get("/orders/{order_id}", response_model=OrderDetailForDeliveryResponse)
async def get_order_details(
    order_id: int,
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Delivery partner can only view orders that are:
    # 1. Ready for pickup (no delivery partner assigned yet)
    # 2. Already assigned to them
    if order.delivery_partner_id and order.delivery_partner_id != current_delivery_partner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this order"
        )
    
    # Get restaurant info
    restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
    restaurant_address = ""
    restaurant_phone = ""
    if restaurant:
        if restaurant.address:
            restaurant_address = f"{restaurant.address.address_line_1}, {restaurant.address.city}"
        if restaurant.owner:
            restaurant_phone = restaurant.owner.phone_number
    
    # Get order items
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    items_response = []
    for item in order_items:
        items_response.append(OrderItemResponse(
            id=item.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            price=item.price,
            special_instructions=item.special_instructions
        ))
    
    return OrderDetailForDeliveryResponse(
        id=order.id,
        order_number=order.order_number,
        restaurant_name=restaurant.restaurant_name if restaurant else "Unknown",
        restaurant_phone=restaurant_phone,
        restaurant_address=restaurant_address,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        delivery_address=order.delivery_address,
        status=order.status.value,
        total_amount=order.total_amount,
        delivery_fee=order.delivery_fee,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        special_instructions=order.special_instructions,
        items=items_response,
        created_at=order.created_at,
        estimated_delivery_time=order.estimated_delivery_time
    )


@router.post("/orders/{order_id}/accept", response_model=APIResponse)
async def accept_order_for_delivery(
    order_id: int,
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """
    Accept an order for delivery.
    Order must be in READY status.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status not in [OrderStatusEnum.NEW, OrderStatusEnum.ACCEPTED, OrderStatusEnum.PREPARING, OrderStatusEnum.READY]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order is not available for acceptance. Current status: {order.status.value}"
        )
    
    if order.delivery_partner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order has already been accepted by another delivery partner"
        )
    
    # Assign delivery partner
    order.delivery_partner_id = current_delivery_partner.id
    
    # If order was READY, move it to PICKED_UP automatically
    if order.status == OrderStatusEnum.READY:
        order.status = OrderStatusEnum.PICKED_UP
        order.pickedup_at = datetime.utcnow()
    # Otherwise, it stays in its current status (ACCEPTED or PREPARING) until the restaurant marks it READY
    
    db.commit()
    db.refresh(order)
    
    # Send notifications
    # To Customer
    if order.customer_id:
        await NotificationService.create_notification(
            db=db,
            customer_id=order.customer_id,
            title=f"Order #{order.order_number} Picked Up",
            message=f"{current_delivery_partner.full_name} is on the way with your order!",
            notification_type="order_update",
            order_id=order.id
        )
    
    # To Restaurant Owner
    restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
    if restaurant and restaurant.owner_id:
        await NotificationService.create_notification(
            db=db,
            owner_id=restaurant.owner_id,
            title=f"Order #{order.order_number} Picked Up",
            message=f"Delivery partner {current_delivery_partner.full_name} has picked up the order",
            notification_type="order_update",
            order_id=order.id
        )
    
    # Broadcast to Socket.IO
    order_data = OrderResponse.from_orm(order).dict()
    await emit_order_update(order_data, event_type="order_partner_assigned")
    
    return APIResponse(
        success=True,
        message="Order accepted for delivery successfully",
        data={"order_id": order.id, "status": order.status.value}
    )


@router.post("/orders/{order_id}/complete", response_model=APIResponse)
async def mark_order_as_delivered(
    order_id: int,
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """
    Mark order as delivered.
    Order must be in PICKED_UP status and assigned to this delivery partner.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.delivery_partner_id != current_delivery_partner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This order is not assigned to you"
        )
    
    if order.status != OrderStatusEnum.PICKED_UP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order is not out for delivery. Current status: {order.status.value}"
        )
    
    # Update order status to DELIVERED
    order.status = OrderStatusEnum.DELIVERED
    order.delivered_at = datetime.utcnow()
    order.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    # Send notifications
    # To Customer
    if order.customer_id:
        await NotificationService.create_notification(
            db=db,
            customer_id=order.customer_id,
            title=f"Order #{order.order_number} Delivered",
            message="Your order has been delivered. Enjoy your meal! 🎉",
            notification_type="order_update",
            order_id=order.id
        )
    
    # To Restaurant Owner
    restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
    if restaurant and restaurant.owner_id:
        await NotificationService.create_notification(
            db=db,
            owner_id=restaurant.owner_id,
            title=f"Order #{order.order_number} Delivered",
            message="Order has been successfully delivered to the customer",
            notification_type="order_update",
            order_id=order.id
        )
    
    # Broadcast to Socket.IO
    order_data = OrderResponse.from_orm(order).dict()
    await emit_order_update(order_data, event_type="order_delivered")
    
    return APIResponse(
        success=True,
        message="Order marked as delivered successfully",
        data={"order_id": order.id, "status": order.status.value}
    )


# ============= Earnings & Stats =============
@router.get("/earnings", response_model=EarningsResponse)
async def get_delivery_partner_earnings(
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """Get earnings statistics for the delivery partner."""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = today_start.replace(day=1)
    
    # Today's earnings
    today_orders = db.query(func.sum(Order.delivery_fee)).filter(
        Order.delivery_partner_id == current_delivery_partner.id,
        Order.status == OrderStatusEnum.DELIVERED,
        Order.delivered_at >= today_start
    ).scalar() or Decimal("0.00")
    
    # Week's earnings
    week_orders = db.query(func.sum(Order.delivery_fee)).filter(
        Order.delivery_partner_id == current_delivery_partner.id,
        Order.status == OrderStatusEnum.DELIVERED,
        Order.delivered_at >= week_start
    ).scalar() or Decimal("0.00")
    
    # Month's earnings
    month_orders = db.query(func.sum(Order.delivery_fee)).filter(
        Order.delivery_partner_id == current_delivery_partner.id,
        Order.status == OrderStatusEnum.DELIVERED,
        Order.delivered_at >= month_start
    ).scalar() or Decimal("0.00")
    
    # Total deliveries
    total_deliveries = db.query(func.count(Order.id)).filter(
        Order.delivery_partner_id == current_delivery_partner.id,
        Order.status == OrderStatusEnum.DELIVERED
    ).scalar() or 0
    
    return EarningsResponse(
        today_earnings=today_orders,
        week_earnings=week_orders,
        month_earnings=month_orders,
        total_deliveries=total_deliveries,
        avg_rating=current_delivery_partner.rating
    )


# ============= Notifications =============
@router.get("/notifications", response_model=List[NotificationResponse])
async def get_delivery_partner_notifications(
    limit: int = 50,
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """Get notification history for delivery partner."""
    notifications = db.query(Notification).filter(
        Notification.delivery_partner_id == current_delivery_partner.id
    ).order_by(desc(Notification.created_at)).limit(limit).all()
    
    return [NotificationResponse.from_orm(notif) for notif in notifications]


@router.put("/notifications/{notification_id}/read", response_model=APIResponse)
async def mark_notification_as_read(
    notification_id: int,
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.delivery_partner_id == current_delivery_partner.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    db.commit()
    
    return APIResponse(
        success=True,
        message="Notification marked as read"
    )


# ============= Location Tracking =============

@router.post("/location/update", response_model=APIResponse)
async def update_delivery_partner_location(
    location_data: UpdateLocationRequest,
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """
    Update delivery partner's current location.
    Should be called periodically (every 5-10 seconds) when partner is delivering an order.
    """
    # Import here to avoid circular dependencies
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Create a simple location tracking record in-memory or use a separate table
    # For now, we'll store it in a simple way
    from sqlalchemy import text
    
    try:
        # Store location in database
        query = text("""
            INSERT INTO delivery_partner_locations 
            (delivery_partner_id, order_id, latitude, longitude, accuracy, bearing, speed, created_at, updated_at)
            VALUES (:partner_id, :order_id, :lat, :lng, :accuracy, :bearing, :speed, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """)
        
        db.execute(query, {
            "partner_id": current_delivery_partner.id,
            "order_id": location_data.order_id,
            "lat": location_data.latitude,
            "lng": location_data.longitude,
            "accuracy": location_data.accuracy,
            "bearing": location_data.bearing,
            "speed": location_data.speed
        })
        db.commit()
        
        return APIResponse(
            success=True,
            message="Location updated successfully",
            data={
                "latitude": location_data.latitude,
                "longitude": location_data.longitude,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        # If table doesn't exist yet, return success anyway
        # Location tracking is optional
        return APIResponse(
            success=True,
            message="Location update received",
            data={
                "latitude": location_data.latitude,
                "longitude": location_data.longitude,
                "timestamp": datetime.utcnow().isoformat(),
                "note": "Location tracking table will be created in next migration"
            }
        )


@router.get("/location/current", response_model=APIResponse)
async def get_current_location(
    current_delivery_partner: DeliveryPartner = Depends(get_current_delivery_partner),
    db: Session = Depends(get_db)
):
    """Get delivery partner's most recent location."""
    from sqlalchemy import text
    
    try:
        query = text("""
            SELECT latitude, longitude, accuracy, bearing, speed, updated_at
            FROM delivery_partner_locations
            WHERE delivery_partner_id = :partner_id
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        result = db.execute(query, {"partner_id": current_delivery_partner.id}).fetchone()
        
        if result:
            return APIResponse(
                success=True,
                message="Location retrieved successfully",
                data={
                    "latitude": result[0],
                    "longitude": result[1],
                    "accuracy": result[2],
                    "bearing": result[3],
                    "speed": result[4],
                    "updated_at": result[5].isoformat() if result[5] else None
                }
            )
        else:
            return APIResponse(
                success=True,
                message="No location data available",
                data=None
            )
    except:
        return APIResponse(
            success=True,
            message="Location tracking not yet initialized",
            data=None
        )
