from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    CustomerUpdate, CustomerResponse, APIResponse, RestaurantResponse, 
    CategoryResponse, AddressResponse, CuisineResponse, MenuItemResponse, 
    ReviewResponse, AddToCartRequest, UpdateCartItemRequest, CartResponse, CartItemResponse,
    OrderCreateRequest, OrderResponse, OrderItemResponse, CustomerAddressCreate, CustomerAddressResponse,
    OrderTrackingResponse, OrderTrackingTimelineStep, DeliveryPartnerResponse
)
from app.models import Customer, Restaurant, Category, MenuItem, Review, Cart, CartItem, Order, OrderItem, Address, CustomerAddress, DeliveryPartner
from app.dependencies import get_current_customer
from typing import List
from decimal import Decimal
from datetime import datetime
from app.services.notification_service import NotificationService


router = APIRouter(prefix="/customer", tags=["Customer"])


@router.put("/profile", response_model=CustomerResponse)
def update_profile(
    profile_data: CustomerUpdate,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Update customer profile"""
    if profile_data.full_name:
        current_customer.full_name = profile_data.full_name
    if profile_data.email:
        current_customer.email = profile_data.email
    if profile_data.profile_photo:
        current_customer.profile_photo = profile_data.profile_photo
    
    db.commit()
    db.refresh(current_customer)
    return current_customer


@router.get("/profile", response_model=CustomerResponse)
def get_profile(current_customer: Customer = Depends(get_current_customer)):
    """Get customer profile"""
    return current_customer


@router.get("/home", response_model=APIResponse)
def get_home_data(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get home screen data"""
    # Get categories
    categories = db.query(Category).filter(Category.is_active == True).order_by(Category.display_order).all()
    
    # Get restaurants (simplified logic for now)
    restaurants = db.query(Restaurant).filter(Restaurant.is_active == True, Restaurant.is_open == True).all()
    
    # Construct response
    data = {
        "categories": [CategoryResponse.from_orm(c).dict() for c in categories],
        "restaurants": [RestaurantResponse.from_orm(r).dict() for r in restaurants],
        "offers": [
            {
                "id": 1,
                "title": "Weekend Special",
                "description": "Flat 30% off on all orders",
                "image_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
                "code": "WEEKEND30"
            }
        ]
    }
    
    return APIResponse(
        success=True,
        message="Home data fetched successfully",
        data=data
    )


@router.get("/restaurants/{restaurant_id}", response_model=APIResponse)
def get_restaurant_details(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get restaurant details, menu, and reviews"""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    # Construct response with all details
    # Note: In a real app, you might want to paginate reviews or menu items if there are many
    
    # Serialize basic info
    restaurant_data = RestaurantResponse.from_orm(restaurant).dict()
    
    # Address
    if restaurant.address:
        restaurant_data["address"] = AddressResponse.from_orm(restaurant.address).dict()
    else:
        restaurant_data["address"] = None
        
    # Cuisines
    restaurant_data["cuisines"] = [CuisineResponse.from_orm(rc.cuisine).dict() for rc in restaurant.cuisines]
    
    # Menu Items
    # Grouping logic can be done here or in frontend. For now, sending flat list.
    restaurant_data["menu"] = [MenuItemResponse.from_orm(item).dict() for item in restaurant.menu_items if item.is_available]
    
    # Reviews
    # Fetch recent reviews
    reviews = db.query(Review).filter(Review.restaurant_id == restaurant_id).order_by(Review.created_at.desc()).limit(5).all()
    review_list = []
    for review in reviews:
        review_dict = ReviewResponse.from_orm(review).dict()
        if review.customer:
            review_dict["customer_name"] = review.customer.full_name or "Anonymous"
        review_list.append(review_dict)
        
    restaurant_data["reviews"] = review_list
    
    return APIResponse(
        success=True,
        message="Restaurant details fetched successfully",
        data=restaurant_data
    )


# ============= Cart Endpoints =============

def get_or_create_cart(db: Session, customer_id: int) -> Cart:
    cart = db.query(Cart).filter(Cart.customer_id == customer_id).first()
    if not cart:
        cart = Cart(customer_id=customer_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def calculate_cart_totals(cart: Cart) -> CartResponse:
    item_total = Decimal("0.0")
    items_response = []
    
    for item in cart.items:
        # Ensure menu item price is used
        price = item.menu_item.discount_price if item.menu_item.discount_price and item.menu_item.discount_price > 0 else item.menu_item.price
        item_total += price * item.quantity
        
        # Create item response with calculated price
        item_resp = CartItemResponse(
            id=item.id,
            menu_item_id=item.menu_item_id,
            menu_item=MenuItemResponse.from_orm(item.menu_item),
            quantity=item.quantity,
            price=price
        )
        items_response.append(item_resp)
        
    # Mock charges for now
    delivery_fee = Decimal("40.0") if item_total > 0 else Decimal("0.0")
    tax_amount = item_total * Decimal("0.05") # 5% tax
    discount_amount = Decimal("0.0") # Placeholder for promo code
    
    total_amount = item_total + delivery_fee + tax_amount - discount_amount
    
    return CartResponse(
        id=cart.id,
        restaurant_id=cart.restaurant_id,
        restaurant_name=cart.restaurant.restaurant_name if cart.restaurant else None,
        items=items_response,
        item_total=item_total,
        delivery_fee=delivery_fee,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total_amount=total_amount
    )

@router.post("/cart/add", response_model=APIResponse)
def add_to_cart(
    request: AddToCartRequest,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Add item to cart"""
    cart = get_or_create_cart(db, current_customer.id)
    
    # Check if cart has items from another restaurant
    if cart.restaurant_id and cart.restaurant_id != request.restaurant_id:
        # Automatically clear cart for different restaurant (User Preference)
        if cart.items:
            db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
            
        cart.restaurant_id = request.restaurant_id
    
    if not cart.restaurant_id:
        cart.restaurant_id = request.restaurant_id
        
    # Check if item already exists
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.menu_item_id == request.menu_item_id
    ).first()
    
    if cart_item:
        cart_item.quantity += request.quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            menu_item_id=request.menu_item_id,
            quantity=request.quantity
        )
        db.add(cart_item)
        
    db.commit()
    db.refresh(cart)
    
    return APIResponse(
        success=True,
        message="Item added to cart",
        data=calculate_cart_totals(cart).dict()
    )

@router.get("/cart", response_model=APIResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get cart details"""
    cart = get_or_create_cart(db, current_customer.id)
    return APIResponse(
        success=True,
        message="Cart fetched successfully",
        data=calculate_cart_totals(cart).dict()
    )


@router.delete("/cart", response_model=APIResponse)
def clear_cart(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Clear all items from cart"""
    cart = get_or_create_cart(db, current_customer.id)
    
    # Delete all items in the cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    
    # Reset restaurant association
    cart.restaurant_id = None
    
    db.commit()
    db.refresh(cart)
    
    return APIResponse(
        success=True,
        message="Cart cleared successfully",
        data=calculate_cart_totals(cart).dict()
    )

@router.put("/cart/items/{item_id}", response_model=APIResponse)
def update_cart_item(
    item_id: int,
    request: UpdateCartItemRequest,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Update cart item quantity"""
    cart = get_or_create_cart(db, current_customer.id)
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
        
    if request.quantity <= 0:
        db.delete(cart_item)
    else:
        cart_item.quantity = request.quantity
        
    db.commit()
    db.refresh(cart)
    
    return APIResponse(
        success=True,
        message="Cart updated",
        data=calculate_cart_totals(cart).dict()
    )

@router.delete("/cart/items/{item_id}", response_model=APIResponse)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Remove item from cart"""
    cart = get_or_create_cart(db, current_customer.id)
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if cart_item:
        db.delete(cart_item)
        db.commit()
        db.refresh(cart)
        
    return APIResponse(
        success=True,
        message="Item removed from cart",
        data=calculate_cart_totals(cart).dict()
    )

# ============= Order Endpoints =============

import random
import string

def generate_order_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

@router.post("/orders", response_model=APIResponse)
async def create_order(
    request: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Create new order"""
    try:
        # 1. Validate Cart/Items
        cart = get_or_create_cart(db, current_customer.id)
        if not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")
            
        if cart.restaurant_id != request.restaurant_id:
             raise HTTPException(status_code=400, detail="Cart restaurant mismatch")

        # 2. Get Address
        address = db.query(CustomerAddress).filter(
            CustomerAddress.id == request.address_id,
            CustomerAddress.customer_id == current_customer.id
        ).first()
        
        if not address:
            delivery_address_str = "123 MG Road, Bangalore, Karnataka 560001"
        else:
            delivery_address_str = f"{address.address_line_1}, {address.city}, {address.pincode}"

        # 3. Calculate Totals
        cart_totals = calculate_cart_totals(cart)
        
        # 4. Create Order
        order = Order(
            order_number=generate_order_number(),
            restaurant_id=request.restaurant_id,
            customer_id=current_customer.id,
            customer_name=current_customer.full_name or "Guest",
            customer_phone=current_customer.phone_number,
            delivery_address=delivery_address_str,
            status="new",
            total_amount=cart_totals.total_amount,
            delivery_fee=cart_totals.delivery_fee,
            tax_amount=cart_totals.tax_amount,
            discount_amount=cart_totals.discount_amount,
            payment_method=request.payment_method,
            payment_status="success"
        )
        db.add(order)
        db.flush() # Get order ID without committing yet
        
        # 5. Create Order Items
        for item in cart.items:
            price = item.menu_item.discount_price if item.menu_item.discount_price and item.menu_item.discount_price > 0 else item.menu_item.price
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item.menu_item_id,
                quantity=item.quantity,
                price=price
            )
            db.add(order_item)
            
        # 6. Clear Cart
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        cart.restaurant_id = None
        
        # Save order ID and number before commit to avoid expiration issues
        res_order_id = order.id
        res_order_number = order.order_number
        
        db.commit()
        
        # Notify relevant parties about new order
        try:
            restaurant = db.query(Restaurant).filter(Restaurant.id == request.restaurant_id).first()
            if restaurant:
                # Use the comprehensive helper that notifies owner and delivery partners
                await NotificationService.send_order_update(
                    db=db,
                    order_id=res_order_id,
                    status="new",
                    owner_id=restaurant.owner_id
                )
        except Exception as ne:
            print(f"Notification error: {ne}")
        
        # Broadcast to Socket.IO
        # from app.socket_manager import emit_new_order
        # from app.schemas import OrderResponse
        # order_data = OrderResponse.from_orm(order).dict()
        # await emit_new_order(order_data)
        
        return APIResponse(
            success=True,
            message="Order placed successfully",
            data={"order_id": res_order_id, "order_number": res_order_number}
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error creating order: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to place order: {str(e)}"
        )


# ============= Address Endpoints =============

@router.post("/addresses", response_model=APIResponse)
def add_address(
    address: CustomerAddressCreate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Add a new delivery address"""
    # If set as default, unset other defaults
    if address.is_default:
        db.query(CustomerAddress).filter(
            CustomerAddress.customer_id == current_customer.id
        ).update({"is_default": False})
    
    new_address = CustomerAddress(
        customer_id=current_customer.id,
        **address.dict()
    )
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    
    return APIResponse(
        success=True,
        message="Address added successfully",
        data=CustomerAddressResponse.from_orm(new_address).dict()
    )

@router.get("/addresses", response_model=APIResponse)
def get_addresses(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get all saved addresses"""
    addresses = db.query(CustomerAddress).filter(
        CustomerAddress.customer_id == current_customer.id
    ).order_by(CustomerAddress.is_default.desc(), CustomerAddress.created_at.desc()).all()
    
    return APIResponse(
        success=True,
        message="Addresses fetched successfully",
        data=[CustomerAddressResponse.from_orm(addr).dict() for addr in addresses]
    )

@router.put("/addresses/{address_id}", response_model=APIResponse)
def update_address(
    address_id: int,
    address_update: CustomerAddressCreate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Update an existing address"""
    address = db.query(CustomerAddress).filter(
        CustomerAddress.id == address_id,
        CustomerAddress.customer_id == current_customer.id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
        
    # If set as default, unset other defaults
    if address_update.is_default:
        db.query(CustomerAddress).filter(
            CustomerAddress.customer_id == current_customer.id
        ).update({"is_default": False})
        
    for key, value in address_update.dict().items():
        setattr(address, key, value)
        
    db.commit()
    db.refresh(address)
    
    return APIResponse(
        success=True,
        message="Address updated successfully",
        data=CustomerAddressResponse.from_orm(address).dict()
    )

@router.delete("/addresses/{address_id}", response_model=APIResponse)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Delete an address"""
    address = db.query(CustomerAddress).filter(
        CustomerAddress.id == address_id,
        CustomerAddress.customer_id == current_customer.id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
        
    db.delete(address)
    db.commit()
    
    return APIResponse(
        success=True,
        message="Address deleted successfully"
    )

# ============= Order History Endpoints =============

@router.get("/orders", response_model=APIResponse)
def get_order_history(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get customer order history"""
    orders = db.query(Order).filter(
        Order.customer_id == current_customer.id
    ).order_by(Order.created_at.desc()).all()
    
    # Manually construct response to ensure restaurant details are included
    # Pydantic's from_orm should handle the relationship if loaded, but let's be explicit
    orders_data = []
    for order in orders:
        order_dict = OrderResponse.from_orm(order).dict()
        # Ensure restaurant is populated
        if order.restaurant:
            order_dict['restaurant'] = RestaurantResponse.from_orm(order.restaurant).dict()
        orders_data.append(order_dict)

    return APIResponse(
        success=True,
        message="Order history fetched successfully",
        data=orders_data
    )

@router.get("/orders/{order_id}", response_model=APIResponse)
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get specific order details"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_customer.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order_data = OrderResponse.from_orm(order).dict()
    
    # Ensure restaurant is populated
    if order.restaurant:
        order_data['restaurant'] = RestaurantResponse.from_orm(order.restaurant).dict()
        
    # Ensure items are populated with menu item details
    items_data = []
    for item in order.items:
        item_dict = OrderItemResponse.from_orm(item).dict()
        if item.menu_item:
             item_dict['menu_item'] = MenuItemResponse.from_orm(item.menu_item).dict()
        items_data.append(item_dict)
    order_data['items'] = items_data

    return APIResponse(
        success=True,
        message="Order details fetched successfully",
        data=order_data
    )

@router.post("/orders/{order_id}/repeat", response_model=APIResponse)
def repeat_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Repeat a past order (add items to cart)"""
    # 1. Fetch the past order
    old_order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_customer.id
    ).first()
    
    if not old_order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # 2. Get or Create Cart
    cart = get_or_create_cart(db, current_customer.id)
    
    # 3. Check Restaurant Match
    if cart.restaurant_id and cart.restaurant_id != old_order.restaurant_id:
        # Clear cart if different restaurant
        # In real app, might ask for confirmation. Here we force clear for "Reorder" convenience.
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        cart.restaurant_id = old_order.restaurant_id
        
    if not cart.restaurant_id:
        cart.restaurant_id = old_order.restaurant_id
        
    # 4. Add items to cart
    for item in old_order.items:
        # Check if menu item still exists and is available
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if not menu_item or not menu_item.is_available:
            continue # Skip unavailable items
            
        # Check if item already in cart
        cart_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.menu_item_id == item.menu_item_id
        ).first()
        
        if cart_item:
            cart_item.quantity += item.quantity
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                menu_item_id=item.menu_item_id,
                quantity=item.quantity
            )
            db.add(cart_item)
            
    db.commit()
    db.refresh(cart)
    
    return APIResponse(
        success=True,
        message="Items added to cart",
        data=calculate_cart_totals(cart).dict()
    )


# ============= Order Tracking Endpoints =============

@router.get("/orders/{order_id}/track", response_model=APIResponse)
def track_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get order tracking details"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_customer.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # 1. Build Timeline
    timeline = []
    
    # Define steps and their corresponding timestamp fields in Order model
    steps = [
        ("Order Confirmed", "Your order has been confirmed by the restaurant", "accepted_at"),
        ("Preparing", "Restaurant is preparing your delicious food", "preparing_at"),
        ("Handed Over to Partner", "Order released and moving to you", "released_at"),
        ("Out for Delivery", "Your order is on the way", "pickedup_at"),
        ("Delivered", "Enjoy your meal!", "delivered_at")
    ]
    
    current_status_index = -1
    if order.status == "new":
        current_status_index = -1
    elif order.status == "accepted":
        current_status_index = 0
    elif order.status == "preparing" or order.status == "ready":
        current_status_index = 1
    elif order.status == "released":
        current_status_index = 2
    elif order.status == "picked_up":
        current_status_index = 3
    elif order.status == "delivered":
        current_status_index = 4
        
    for i, (title, subtitle, time_field) in enumerate(steps):
        timestamp = getattr(order, time_field)
        is_completed = timestamp is not None
        is_current = i == current_status_index
        
        # Format time
        time_str = timestamp.strftime("%I:%M %p") if timestamp else None
        
        timeline.append(OrderTrackingTimelineStep(
            title=title,
            subtitle=subtitle,
            time=time_str,
            is_completed=is_completed,
            is_current=is_current
        ))
        
    # 2. Delivery Partner (Mock if not assigned)
    delivery_partner_data = None
    if order.delivery_partner:
        delivery_partner_data = DeliveryPartnerResponse.from_orm(order.delivery_partner)
    elif order.status in ["picked_up", "delivered"]:
         # Mock for demo if no partner assigned but status implies it
         delivery_partner_data = DeliveryPartnerResponse(
             id=999,
             full_name="Rajesh Kumar",
             phone_number="+919876543210",
             vehicle_number="DL 01 AB 1234",
             rating=Decimal("4.8"),
             profile_photo="https://randomuser.me/api/portraits/men/32.jpg"
         )

    # 3. Estimated Arrival Time (Mock logic)
    estimated_arrival = "30 min"
    if order.status == "delivered":
        estimated_arrival = "Arrived"
    elif order.status == "picked_up":
        estimated_arrival = "14 min"
        
    # 4. Bill Details
    item_total = sum(item.price * item.quantity for item in order.items)
    
    response_data = OrderTrackingResponse(
        order_id=order.id,
        order_number=order.order_number,
        status=order.status,
        estimated_arrival_time=estimated_arrival,
        delivery_partner=delivery_partner_data,
        timeline=timeline,
        restaurant_name=order.restaurant.restaurant_name,
        items=[OrderItemResponse.from_orm(item) for item in order.items],
        item_total=item_total,
        delivery_fee=order.delivery_fee,
        tax_amount=order.tax_amount,
        discount_amount=order.discount_amount,
        total_amount=order.total_amount
    )
    
    return APIResponse(
        success=True,
        message="Order tracking details fetched",
        data=response_data.dict()
    )




#============= Delivery Partner Location Tracking =============

@router.get("/orders/{order_id}/track-location", response_model=APIResponse)
def track_delivery_partner_location(
    order_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """
    Track delivery partner's real-time location for an active order.
    Returns the current GPS location of the delivery partner assigned to this order.
    """
    from sqlalchemy import text
    from math import radians, sin, cos, sqrt, atan2
    
    # Get order
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_customer.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if order has delivery partner assigned
    if not order.delivery_partner_id:
        return APIResponse(
            success=True,
            message="No delivery partner assigned yet",
            data={
                "tracking_available": False,
                "message": "Delivery partner will be assigned soon"
            }
        )
    
    # Get delivery partner's latest location
    try:
        query = text("""
            SELECT latitude, longitude, accuracy, bearing, speed, created_at
            FROM delivery_partner_locations
            WHERE delivery_partner_id = :partner_id
            AND (order_id = :order_id OR order_id IS NULL)
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        result = db.execute(query, {
            "partner_id": order.delivery_partner_id,
            "order_id": order_id
        }).fetchone()
        
        if result:
            partner_lat, partner_lng, accuracy, bearing, speed, updated_at = result
            
            # Calculate distance if customer address has coordinates
            # For now, return basic location data
            # In production, you'd geocode the delivery address
            
            # Simple ETA estimation (very basic)
            avg_speed_kmh = (speed * 3.6) if speed and speed > 0 else 20  # Convert m/s to km/h, default 20 km/h
            estimated_distance_km = 2.0  # Mock distance, should calculate from addresses
            eta_minutes = int((estimated_distance_km / avg_speed_kmh) * 60)
            
            return APIResponse(
                success=True,
                message="Delivery partner location retrieved",
                data={
                    "tracking_available": True,
                    "delivery_partner": {
                        "id": order.delivery_partner.id,
                        "name": order.delivery_partner.full_name,
                        "phone": order.delivery_partner.phone_number,
                        "vehicle_type": order.delivery_partner.vehicle_type,
                        "vehicle_number": order.delivery_partner.vehicle_number,
                        "rating": float(order.delivery_partner.rating) if order.delivery_partner.rating else 5.0
                    },
                    "location": {
                        "latitude": partner_lat,
                        "longitude": partner_lng,
                        "accuracy": accuracy,
                        "bearing": bearing,
                        "speed_mps": speed,
                        "speed_kmh": round(speed * 3.6, 2) if speed else None,
                        "last_updated": updated_at.isoformat() if updated_at else None
                    },
                    "eta_minutes": eta_minutes,
                    "order_status": order.status
                }
            )
        else:
            return APIResponse(
                success=True,
                message="Delivery partner location not available",
                data={
                    "tracking_available": False,
                    "delivery_partner": {
                        "id": order.delivery_partner.id,
                        "name": order.delivery_partner.full_name,
                        "phone": order.delivery_partner.phone_number
                    },
                    "message": "Location will be available once delivery starts"
                }
            )
    except Exception as e:
        # Table doesn't exist yet or other error
        return APIResponse(
            success=True,
            message="Location tracking will be available soon",
            data={
                "tracking_available": False,
                "delivery_partner": {
                    "id": order.delivery_partner.id,
                    "name": order.delivery_partner.full_name,
                    "phone": order.delivery_partner.phone_number
                } if order.delivery_partner else None,
                "note": "Location tracking feature coming soon"
            }
        )
