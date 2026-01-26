from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Float, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
from app.models_location import CustomerLocation, DeliveryPartnerLocation



class VerificationStatusEnum(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class RestaurantTypeEnum(str, enum.Enum):
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    BAKERY = "bakery"
    FAST_FOOD = "fast_food"
    FINE_DINING = "fine_dining"
    CLOUD_KITCHEN = "cloud_kitchen"


class OrderStatusEnum(str, enum.Enum):
    # Initial Status
    PENDING = "pending"                           # Order created, waiting for restaurant
    
    # Restaurant Workflow Statuses
    ACCEPTED = "accepted"                         # Step 1: Restaurant accepted order
    PREPARING = "preparing"                       # Step 2: Restaurant is preparing food (with time update)
    READY = "ready"                              # Step 3: Food is ready for pickup
    HANDED_OVER = "handed_over"                  # Step 4: Restaurant handed over to delivery partner (Done for restaurant)
    
    # Delivery Partner Workflow Statuses
    ASSIGNED = "assigned"                        # Step 1: Delivery partner assigned/accepted order
    REACHED_RESTAURANT = "reached_restaurant"    # Step 2: Delivery partner reached hotel/restaurant
    PICKED_UP = "picked_up"                      # Step 3: Order picked up from restaurant
    DELIVERED = "delivered"                      # Step 4: Order delivered to customer (Done for delivery)
    
    # Terminal/Error Statuses
    REJECTED = "rejected"                        # Restaurant rejected order
    CANCELLED = "cancelled"                      # Order cancelled
    
    # Legacy status for backward compatibility (to be removed)
    RELEASED = "released"                        # Deprecated - use HANDED_OVER instead


class Owner(Base):
    __tablename__ = "owners"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(15), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    restaurants = relationship("Restaurant", back_populates="owner")
    otps = relationship("OTP", back_populates="owner")
    device_tokens = relationship("DeviceToken", back_populates="owner")
    notifications = relationship("Notification", back_populates="owner")


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone_number = Column(String(15), unique=True, nullable=False, index=True)
    profile_photo = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    otps = relationship("OTP", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    addresses = relationship("CustomerAddress", back_populates="customer")
    cart = relationship("Cart", back_populates="customer", uselist=False)
    device_tokens = relationship("DeviceToken", back_populates="customer")
    notifications = relationship("Notification", back_populates="customer")




class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=False)
    restaurant_name = Column(String(255), nullable=False)
    restaurant_type = Column(Enum(RestaurantTypeEnum), nullable=False)
    fssai_license_number = Column(String(50), unique=True, nullable=False)
    opening_time = Column(String(10), nullable=False)  # Format: HH:MM
    closing_time = Column(String(10), nullable=False)  # Format: HH:MM
    description = Column(Text, nullable=True)
    cost_for_two = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)

    is_open = Column(Boolean, default=False)
    average_rating = Column(DECIMAL(3, 2), default=0.0)
    total_reviews = Column(Integer, default=0)
    verification_status = Column(Enum(VerificationStatusEnum), default=VerificationStatusEnum.PENDING)
    verification_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("Owner", back_populates="restaurants")
    cuisines = relationship("RestaurantCuisine", back_populates="restaurant")
    address = relationship("Address", back_populates="restaurant", uselist=False)
    documents = relationship("Document", back_populates="restaurant")
    menu_items = relationship("MenuItem", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")
    reviews = relationship("Review", back_populates="restaurant")



class Cuisine(Base):
    __tablename__ = "cuisines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    icon = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    restaurants = relationship("RestaurantCuisine", back_populates="cuisine")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    icon = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    menu_items = relationship("MenuItem", back_populates="category")


class RestaurantCuisine(Base):
    __tablename__ = "restaurant_cuisines"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    cuisine_id = Column(Integer, ForeignKey("cuisines.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="cuisines")
    cuisine = relationship("Cuisine", back_populates="restaurants")


class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), unique=True, nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    landmark = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="address")


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    landmark = Column(String(255), nullable=True)
    address_type = Column(String(50), default="home")  # home, work, other
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="addresses")



class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    document_type = Column(String(50), nullable=False)  # fssai_license, restaurant_photo
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)  # in bytes
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="documents")


class OTP(Base):
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    delivery_partner_id = Column(Integer, ForeignKey("delivery_partners.id"), nullable=True)
    phone_number = Column(String(15), nullable=False, index=True)
    otp_code = Column(String(10), nullable=False)
    is_verified = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("Owner", back_populates="otps")
    customer = relationship("Customer", back_populates="otps")
    delivery_partner = relationship("DeliveryPartner", back_populates="otps")




class DeviceToken(Base):
    __tablename__ = "device_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    delivery_partner_id = Column(Integer, ForeignKey("delivery_partners.id"), nullable=True)
    token = Column(String(500), unique=True, nullable=False)
    device_type = Column(String(50), nullable=False)  # ios, android, web
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("Owner", back_populates="device_tokens")
    customer = relationship("Customer", back_populates="device_tokens")
    delivery_partner = relationship("DeliveryPartner", back_populates="device_tokens")


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    delivery_partner_id = Column(Integer, ForeignKey("delivery_partners.id"), nullable=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50))  # e.g., 'order_update', 'promotion'
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("Owner", back_populates="notifications")
    customer = relationship("Customer", back_populates="notifications")
    delivery_partner = relationship("DeliveryPartner", back_populates="notifications")
    order = relationship("Order")


class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    discount_price = Column(DECIMAL(10, 2), nullable=True, default=0.0)
    image_url = Column(String(500), nullable=True)
    is_vegetarian = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    is_bestseller = Column(Boolean, default=False)
    rating = Column(DECIMAL(3, 2), default=0.0)
    preparation_time = Column(Integer, nullable=True)  # in minutes
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
    category = relationship("Category", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")


class DeliveryPartner(Base):
    __tablename__ = "delivery_partners"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone_number = Column(String(15), unique=True, nullable=False)
    vehicle_number = Column(String(20), nullable=True)
    vehicle_type = Column(String(50), nullable=True)  # bike, scooter, car, bicycle
    license_number = Column(String(50), nullable=True)
    rating = Column(DECIMAL(3, 2), default=5.0)
    profile_photo = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)  # Online/Offline status
    is_registered = Column(Boolean, default=False)  # Complete registration status
    verification_status = Column(Enum(VerificationStatusEnum), default=VerificationStatusEnum.PENDING)  # Admin approval
    verification_notes = Column(Text, nullable=True)  # Admin notes for approval/rejection
    last_online_at = Column(DateTime(timezone=True), nullable=True)
    last_offline_at = Column(DateTime(timezone=True), nullable=True)
    
    # Location tracking for proximity-based assignments
    latitude = Column(DECIMAL(10, 8), nullable=True)
    longitude = Column(DECIMAL(11, 8), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="delivery_partner")
    device_tokens = relationship("DeviceToken", back_populates="delivery_partner")
    notifications = relationship("Notification", back_populates="delivery_partner")
    otps = relationship("OTP", back_populates="delivery_partner")




class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    delivery_partner_id = Column(Integer, ForeignKey("delivery_partners.id"), nullable=True)


    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(15), nullable=False)
    delivery_address = Column(Text, nullable=False)
    status = Column(String(50), default=OrderStatusEnum.PENDING.value)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    delivery_fee = Column(DECIMAL(10, 2), default=0.0)
    tax_amount = Column(DECIMAL(10, 2), default=0.0)
    discount_amount = Column(DECIMAL(10, 2), default=0.0)
    payment_method = Column(String(50), nullable=True)
    payment_status = Column(String(50), default="pending")
    special_instructions = Column(Text, nullable=True)
    estimated_delivery_time = Column(DateTime(timezone=True), nullable=True)
    
    # Restaurant workflow timestamps
    accepted_at = Column(DateTime(timezone=True), nullable=True)           # When restaurant accepts
    preparing_at = Column(DateTime(timezone=True), nullable=True)          # When restaurant starts preparing
    ready_at = Column(DateTime(timezone=True), nullable=True)              # When food is ready
    handed_over_at = Column(DateTime(timezone=True), nullable=True)        # When restaurant hands over to delivery
    
    # Delivery partner workflow timestamps
    assigned_at = Column(DateTime(timezone=True), nullable=True)           # When delivery partner accepts
    reached_restaurant_at = Column(DateTime(timezone=True), nullable=True) # When delivery partner reaches restaurant
    pickedup_at = Column(DateTime(timezone=True), nullable=True)           # When delivery partner picks up order
    delivered_at = Column(DateTime(timezone=True), nullable=True)          # When order is delivered
    
    # Legacy/other timestamps
    released_at = Column(DateTime(timezone=True), nullable=True)           # Deprecated - use handed_over_at
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    delivery_partner = relationship("DeliveryPartner", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")




class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    special_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer")
    restaurant = relationship("Restaurant", back_populates="reviews")


class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="cart")
    restaurant = relationship("Restaurant")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    menu_item = relationship("MenuItem")


