from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.dependencies import get_current_restaurant
from app.schemas import OrderResponse, OrderStatusUpdate, APIResponse, OrderSummaryResponse
from app.models import Restaurant, Order, OrderStatusEnum
import json


router = APIRouter(prefix="/orders", tags=["Orders"])


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, restaurant_id: int):
        await websocket.accept()
        if restaurant_id not in self.active_connections:
            self.active_connections[restaurant_id] = []
        self.active_connections[restaurant_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, restaurant_id: int):
        if restaurant_id in self.active_connections:
            self.active_connections[restaurant_id].remove(websocket)
    
    async def send_to_restaurant(self, restaurant_id: int, message: dict):
        if restaurant_id in self.active_connections:
            for connection in self.active_connections[restaurant_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()


def map_to_order_summary(order: Order) -> dict:
    """Map order to summary response"""
    item_count = 0
    if order.items:
        item_count = sum(item.quantity for item in order.items)
        
    return {
        "order_id": order.id,
        "item_count": item_count,
        "total_amount": order.total_amount,
        "created_at": order.created_at,
        "payment_method": order.payment_method,
        "status": order.status.value
    }


@router.get("/new", response_model=APIResponse)
def get_new_orders(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get all new orders"""
    orders = db.query(Order).filter(
        Order.restaurant_id == restaurant.id,
        Order.status == OrderStatusEnum.NEW
    ).order_by(Order.created_at.desc()).all()
    
    return APIResponse(
        success=True,
        message="New orders retrieved successfully",
        data={
            "orders": [map_to_order_summary(order) for order in orders]
        }
    )


@router.get("/ongoing", response_model=APIResponse)
def get_ongoing_orders(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get all ongoing orders"""
    orders = db.query(Order).filter(
        Order.restaurant_id == restaurant.id,
        Order.status.in_([
            OrderStatusEnum.ACCEPTED,
            OrderStatusEnum.PREPARING,
            OrderStatusEnum.READY,
            OrderStatusEnum.PICKED_UP
        ])
    ).order_by(Order.created_at.desc()).all()
    
    return APIResponse(
        success=True,
        message="Ongoing orders retrieved successfully",
        data={
            "orders": [map_to_order_summary(order) for order in orders]
        }
    )


@router.get("/completed", response_model=APIResponse)
def get_completed_orders(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get all completed orders"""
    orders = db.query(Order).filter(
        Order.restaurant_id == restaurant.id,
        Order.status.in_([
            OrderStatusEnum.DELIVERED,
            OrderStatusEnum.REJECTED,
            OrderStatusEnum.CANCELLED
        ])
    ).order_by(Order.created_at.desc()).limit(50).all()
    
    return APIResponse(
        success=True,
        message="Completed orders retrieved successfully",
        data={
            "orders": [map_to_order_summary(order) for order in orders]
        }
    )


from app.services.notification_service import NotificationService

# Helper to handle status updates
async def update_order_status_helper(
    order_id: int,
    new_status: OrderStatusEnum,
    restaurant_id: int,
    db: Session,
    timestamp_field: str = None
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.restaurant_id == restaurant_id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update status
    order.status = new_status
    
    # Update timestamp if specified
    if timestamp_field:
        setattr(order, timestamp_field, datetime.utcnow())
        
    # Special case for delivered
    if new_status == OrderStatusEnum.DELIVERED:
        order.completed_at = datetime.utcnow()
        
    db.commit()
    db.refresh(order)
    
    # Broadcast to restaurant WebSocket
    await broadcast_new_order(restaurant_id, order)
    
    # Send FCM notification and save to DB
    await NotificationService.send_order_update(
        db=db,
        order_id=order.id,
        status=new_status.value,
        customer_id=order.customer_id,
        owner_id=order.restaurant.owner_id if order.restaurant else None,
        delivery_partner_id=order.delivery_partner_id
    )
    
    return APIResponse(
        success=True,
        message=f"Order marked as {new_status.value}",
        data=OrderResponse.from_orm(order).dict()
    )


@router.put("/{order_id}/accept", response_model=APIResponse)
async def accept_order(
    order_id: int,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Accept an order"""
    return await update_order_status_helper(
        order_id, 
        OrderStatusEnum.ACCEPTED, 
        restaurant.id, 
        db, 
        "accepted_at"
    )


@router.put("/{order_id}/preparing", response_model=APIResponse)
async def preparing_order(
    order_id: int,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Mark order as preparing"""
    return await update_order_status_helper(
        order_id, 
        OrderStatusEnum.PREPARING, 
        restaurant.id, 
        db, 
        "preparing_at"
    )


@router.put("/{order_id}/ready", response_model=APIResponse)
async def ready_order(
    order_id: int,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Mark order as ready"""
    return await update_order_status_helper(
        order_id, 
        OrderStatusEnum.READY, 
        restaurant.id, 
        db, 
        "ready_at"
    )


@router.put("/{order_id}/pickedup", response_model=APIResponse)
async def pickedup_order(
    order_id: int,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Mark order as picked up"""
    return await update_order_status_helper(
        order_id, 
        OrderStatusEnum.PICKED_UP, 
        restaurant.id, 
        db, 
        "pickedup_at"
    )


@router.put("/{order_id}/delivered", response_model=APIResponse)
async def delivered_order(
    order_id: int,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Mark order as delivered"""
    return await update_order_status_helper(
        order_id, 
        OrderStatusEnum.DELIVERED, 
        restaurant.id, 
        db, 
        "delivered_at"
    )


@router.put("/{order_id}/release", response_model=APIResponse)
async def release_order(
    order_id: int,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Mark order as released from restaurant"""
    return await update_order_status_helper(
        order_id, 
        OrderStatusEnum.RELEASED, 
        restaurant.id, 
        db, 
        "released_at"
    )


@router.post("/{order_id}/reject", response_model=APIResponse)
async def reject_order(
    order_id: int,
    status_update: OrderStatusUpdate,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Reject an order"""
    try:
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.restaurant_id == restaurant.id
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order.status = OrderStatusEnum.REJECTED
        order.rejected_at = datetime.utcnow()
        order.rejection_reason = status_update.rejection_reason
        db.commit()
        db.refresh(order)
        
        # Send notification to customer
        await NotificationService.send_order_update(
            db=db,
            order_id=order.id,
            status="rejected",
            customer_id=order.customer_id
        )
        
        # Broadcast update
        await broadcast_new_order(restaurant.id, order)
        
        return APIResponse(
            success=True,
            message="Order rejected successfully",
            data=OrderResponse.from_orm(order).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject order: {str(e)}"
        )


@router.get("/{order_id}", response_model=APIResponse)
def get_order_details(
    order_id: int,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get order details"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.restaurant_id == restaurant.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Calculate subtotal
    subtotal = sum(item.price * item.quantity for item in order.items)
    
    # Construct response
    order_details = {
        "order_id": order.id,
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "delivery_address": order.delivery_address,
        "status": order.status.value,
        "items": [OrderResponse.from_orm(order).items] if hasattr(OrderResponse.from_orm(order), 'items') else [item for item in order.items], # Use ORM relationship directly
        "special_instructions": order.special_instructions,
        "subtotal": subtotal,
        "tax_amount": order.tax_amount,
        "delivery_fee": order.delivery_fee,
        "discount_amount": order.discount_amount,
        "total_amount": order.total_amount,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "timeline": {
            "created_at": order.created_at,
            "accepted_at": order.accepted_at,
            "preparing_at": order.preparing_at,
            "ready_at": order.ready_at,
            "pickedup_at": order.pickedup_at,
            "delivered_at": order.delivered_at,
            "rejected_at": order.rejected_at,
            "completed_at": order.completed_at or order.estimated_delivery_time
        }
    }
    
    # Fix items serialization - manual mapping to avoid Pydantic issues if any
    items_data = []
    for item in order.items:
        items_data.append({
            "id": item.id,
            "menu_item_id": item.menu_item_id,
            "quantity": item.quantity,
            "price": item.price,
            "special_instructions": item.special_instructions
        })
    order_details["items"] = items_data
    
    return APIResponse(
        success=True,
        message="Order details retrieved successfully",
        data=order_details
    )


@router.websocket("/live")
async def websocket_live_orders(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for live order updates"""
    try:
        # Verify token and get restaurant
        from app.services.jwt_service import verify_token
        payload = verify_token(token)
        
        if not payload:
            await websocket.close(code=1008)
            return
        
        owner_id = payload.get("owner_id")
        if not owner_id:
            await websocket.close(code=1008)
            return
        
        # Get restaurant
        from app.models import Owner
        owner = db.query(Owner).filter(Owner.id == owner_id).first()
        if not owner:
            await websocket.close(code=1008)
            return
        
        restaurant = db.query(Restaurant).filter(
            Restaurant.owner_id == owner.id
        ).first()
        
        if not restaurant:
            await websocket.close(code=1008)
            return
        
        # Connect to WebSocket
        await manager.connect(websocket, restaurant.id)
        
        try:
            while True:
                # Wait for messages (keep connection alive)
                data = await websocket.receive_text()
                
                # Handle ping/pong
                if data == "ping":
                    await websocket.send_text("pong")
        
        except WebSocketDisconnect:
            manager.disconnect(websocket, restaurant.id)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


# Helper function to broadcast new orders (to be called when new order is created)
# Helper function to broadcast order updates
async def broadcast_new_order(restaurant_id: int, order: Order, event_type: str = None):
    """
    Broadcast order update to restaurant's WebSocket connections.
    If event_type is not provided, it is inferred from the order status.
    """
    if not event_type:
        status_to_event = {
            OrderStatusEnum.NEW: "new_order",
            OrderStatusEnum.ACCEPTED: "order_accepted",
            OrderStatusEnum.PREPARING: "preparing",
            OrderStatusEnum.READY: "ready",
            OrderStatusEnum.PICKED_UP: "pickedup",
            OrderStatusEnum.DELIVERED: "delivered",
            OrderStatusEnum.RELEASED: "order_released",
            OrderStatusEnum.REJECTED: "order_rejected",
            OrderStatusEnum.CANCELLED: "order_cancelled"
        }
        event_type = status_to_event.get(order.status, "order_update")

    message = {
        "type": event_type,
        "order": OrderResponse.from_orm(order).dict()
    }
    await manager.send_to_restaurant(restaurant_id, message)
