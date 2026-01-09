import socketio
import json
import logging
from typing import Any, Dict, Optional
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)

def clean_json(data):
    """Recursively convert Decimal and datetime to JSON-serializable types"""
    if isinstance(data, list):
        return [clean_json(v) for v in data]
    if isinstance(data, dict):
        return {k: clean_json(v) for k, v in data.items()}
    if isinstance(data, Decimal):
        return float(data)
    if isinstance(data, datetime):
        return data.isoformat()
    return data

# Create an Async Socket.IO server
# We allow both polling and websocket transports to ensure compatibility 
# with various clients, including Flutter.
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# ASGI Application for mounting with FastAPI
sio_app = socketio.ASGIApp(
    socketio_server=sio,
    socketio_path=''
)

@sio.event
async def connect(sid, environ, auth):
    """
    Handle client connection.
    auth can contain tokens for verification.
    """
    logger.info(f"Client connected: {sid}")
    # You can extract user details from auth if provided by the client
    # Example: token = auth.get('token')
    return True

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")

@sio.on('request_join')
async def request_join(sid, data):
    """
    Allow client to join a specific room.
    Expected data: {"room": "restaurant_1"} or {"room": "customer_5"}
    """
    room = data.get('room')
    if room:
        await sio.enter_room(sid, room)
        logger.info(f"Client {sid} joined room: {room}")
        await sio.emit('room_joined', {"room": room}, to=sid)

@sio.event
async def leave_room(sid, data):
    """Allow client to leave a specific room"""
    room = data.get('room')
    if room:
        await sio.leave_room(sid, room)
        logger.info(f"Client {sid} left room: {room}")

async def emit_order_update(order_data: Dict[str, Any], event_type: str = "order_update"):
    """
    Broadcast order updates to relevant rooms.
    - restaurant_{restaurant_id}
    - customer_{customer_id}
    - delivery_{delivery_partner_id} (if assigned)
    - global_admin (for monitoring)
    """
    restaurant_id = order_data.get('restaurant_id')
    customer_id = order_data.get('customer_id')
    delivery_partner_id = order_data.get('delivery_partner_id')
    
    # Payload to send
    payload = clean_json({
        "event": event_type,
        "order": order_data
    })
    
    # Emit to restaurant
    if restaurant_id:
        await sio.emit('order_update', payload, room=f"restaurant_{restaurant_id}")
    
    # Emit to customer
    if customer_id:
        await sio.emit('order_update', payload, room=f"customer_{customer_id}")
        
    # Emit to delivery partner
    if delivery_partner_id:
        await sio.emit('order_update', payload, room=f"delivery_partner_{delivery_partner_id}")
        
    # Emit to global admin
    await sio.emit('order_update', payload, room="global_admin")
    
    logger.info(f"Emitted {event_type} for order {order_data.get('id')}")

async def emit_new_order(order_data: Dict[str, Any]):
    """Specific event for new order creation"""
    await emit_order_update(order_data, event_type="new_order")
    
    # Also notify all online delivery partners if no partner is assigned yet
    if not order_data.get('delivery_partner_id'):
        await sio.emit('new_available_order', clean_json({"order": order_data}), room="available_delivery_partners")
