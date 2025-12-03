from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Union, Any
from datetime import datetime
from decimal import Decimal
import enum


# ============= Common Response Schema =============
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Union[dict, list, Any]] = None


# ============= Owner Schemas =============
class OwnerCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{9,14}$')


class OwnerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None


class OwnerResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone_number: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Customer Schemas =============
class CustomerCreate(BaseModel):
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    profile_photo: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    full_name: Optional[str]
    email: Optional[str]
    phone_number: str
    profile_photo: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True



# ============= Restaurant Schemas =============
class RestaurantCreate(BaseModel):
    restaurant_name: str = Field(..., min_length=2, max_length=255)
    restaurant_type: str
    fssai_license_number: str = Field(..., min_length=10, max_length=50)
    opening_time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    closing_time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')


class RestaurantUpdate(BaseModel):
    restaurant_name: Optional[str] = Field(None, min_length=2, max_length=255)
    restaurant_type: Optional[str] = None
    opening_time: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    closing_time: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')


class RestaurantResponse(BaseModel):
    id: int
    restaurant_name: str
    restaurant_type: str
    fssai_license_number: str
    opening_time: str
    closing_time: str
    description: Optional[str]
    cost_for_two: Optional[int]
    is_active: bool

    is_open: bool
    average_rating: Decimal
    verification_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Cuisine Schemas =============
class CuisineResponse(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None
    
    class Config:
        from_attributes = True


class RestaurantCuisineCreate(BaseModel):
    cuisine_ids: List[int]


# ============= Address Schemas =============
class AddressCreate(BaseModel):
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)
    address_line_1: str = Field(..., min_length=5, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., pattern=r'^\d{6}$')
    landmark: Optional[str] = Field(None, max_length=255)


class AddressUpdate(AddressCreate):
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    address_line_1: Optional[str] = Field(None, min_length=5, max_length=255)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    pincode: Optional[str] = Field(None, pattern=r'^\d{6}$')


class AddressResponse(BaseModel):
    id: int
    latitude: Decimal
    longitude: Decimal
    address_line_1: str
    address_line_2: Optional[str]
    city: str
    state: str
    pincode: str
    landmark: Optional[str]
    
    class Config:
        from_attributes = True


class CustomerAddressCreate(BaseModel):
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)
    address_line_1: str = Field(..., min_length=5, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., pattern=r'^\d{6}$')
    landmark: Optional[str] = Field(None, max_length=255)
    address_type: str = "home"
    is_default: bool = False


class CustomerAddressResponse(BaseModel):
    id: int
    customer_id: int
    latitude: Decimal
    longitude: Decimal
    address_line_1: str
    address_line_2: Optional[str]
    city: str
    state: str
    pincode: str
    landmark: Optional[str]
    address_type: str
    is_default: bool
    
    class Config:
        from_attributes = True



# ============= Document Schemas =============
class DocumentUploadResponse(BaseModel):
    id: int
    document_type: str
    file_url: str
    file_name: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class PresignedUrlResponse(BaseModel):
    upload_url: str
    file_key: str
    expires_in: int


# ============= Auth Schemas =============
class SendOTPRequest(BaseModel):
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')


class VerifyOTPRequest(BaseModel):
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    otp_code: str = Field(..., min_length=4, max_length=10)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    owner: OwnerResponse


class CustomerTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    customer: CustomerResponse



# ============= Category Schemas =============
class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None
    is_active: bool
    display_order: int
    
    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    icon: Optional[str] = None
    display_order: int = 0


# ============= Menu Item Schemas =============
class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    discount_price: Optional[Decimal] = Field(None, ge=0)
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    is_vegetarian: bool = False
    is_available: bool = True
    preparation_time: Optional[int] = Field(None, gt=0)


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    discount_price: Optional[Decimal] = Field(None, ge=0)
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    is_vegetarian: Optional[bool] = None
    is_available: Optional[bool] = None
    preparation_time: Optional[int] = Field(None, gt=0)


class MenuItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    discount_price: Optional[Decimal]
    image_url: Optional[str]
    category_id: Optional[int]
    category: Optional[CategoryResponse] = None
    is_vegetarian: bool
    is_available: bool
    is_bestseller: bool
    rating: Decimal
    preparation_time: Optional[int]

    created_at: datetime
    
    class Config:
        from_attributes = True


class MenuItemAvailability(BaseModel):
    is_available: bool


# ============= Order Schemas =============
class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    price: Decimal
    special_instructions: Optional[str]
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_phone: str
    delivery_address: str
    status: str
    total_amount: Decimal
    delivery_fee: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    payment_method: Optional[str]
    payment_status: str
    special_instructions: Optional[str]
    estimated_delivery_time: Optional[datetime]
    created_at: datetime
    items: List[OrderItemResponse] = []
    restaurant: Optional[RestaurantResponse] = None
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str
    rejection_reason: Optional[str] = None


class OrderTimeline(BaseModel):
    created_at: datetime
    accepted_at: Optional[datetime] = None
    preparing_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    pickedup_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ============= Review Schemas =============
class ReviewResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    rating: int
    review_text: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Restaurant Detail Schemas =============
class RestaurantDetailResponse(RestaurantResponse):
    address: Optional[AddressResponse]
    cuisines: List[CuisineResponse]
    menu: List[MenuItemResponse]
    reviews: List[ReviewResponse]
    
    class Config:
        from_attributes = True


class OrderDetailsResponse(BaseModel):
    order_id: int
    order_number: str
    customer_name: str
    customer_phone: str
    delivery_address: str
    status: str
    items: List[OrderItemResponse]
    special_instructions: Optional[str]
    
    # Billing
    subtotal: Decimal
    tax_amount: Decimal
    delivery_fee: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    
    payment_method: Optional[str]
    payment_status: str
    
    timeline: OrderTimeline


class OrderCreateRequest(BaseModel):
    restaurant_id: int
    address_id: int
    payment_method: str
    items: Optional[List[dict]] = None # Optional if using cart



class OrderSummaryResponse(BaseModel):
    order_id: int
    item_count: int
    total_amount: Decimal
    created_at: datetime
    payment_method: Optional[str]
    status: str
    
    class Config:
        from_attributes = True


# ============= Dashboard Schemas =============
class QuickAction(BaseModel):
    id: str
    title: str
    icon: str
    route: str


class DashboardSummary(BaseModel):
    total_orders: int
    total_earnings: Decimal
    avg_rating: Decimal
    today_growth: float
    quick_action: List[QuickAction]
    new_orders_count: Optional[int] = 0
    ongoing_orders_count: Optional[int] = 0


class DashboardResponse(BaseModel):
    summary: DashboardSummary
    quick_actions: List[QuickAction]


# ============= Verification Schemas =============
class VerificationStatusEnum(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class VerificationStatusResponse(BaseModel):
    status: str
    verification_notes: Optional[str]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class OnboardingStatusResponse(BaseModel):
    owner_details_completed: bool
    restaurant_details_completed: bool
    address_details_completed: bool
    cuisine_selection_completed: bool
    document_upload_completed: bool
    next_step: str
    verification_status: str


# ============= Cart Schemas =============
class AddToCartRequest(BaseModel):
    menu_item_id: int
    quantity: int = 1
    restaurant_id: int


class UpdateCartItemRequest(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    menu_item_id: int
    menu_item: MenuItemResponse
    quantity: int
    price: Decimal
    
    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    restaurant_id: Optional[int]
    restaurant_name: Optional[str]
    items: List[CartItemResponse]
    
    # Bill Details
    item_total: Decimal
    delivery_fee: Decimal
    tax_amount: Decimal
    discount_amount: Decimal = Decimal("0.0")
    total_amount: Decimal
    
    class Config:
        from_attributes = True



class DeliveryPartnerResponse(BaseModel):
    id: int
    full_name: str
    phone_number: str
    vehicle_number: Optional[str]
    rating: Decimal
    profile_photo: Optional[str]
    
    class Config:
        from_attributes = True


class OrderTrackingTimelineStep(BaseModel):
    title: str
    subtitle: Optional[str]
    time: Optional[str]
    is_completed: bool
    is_current: bool


class OrderTrackingResponse(BaseModel):
    order_id: int
    order_number: str
    status: str
    estimated_arrival_time: Optional[str]
    
    delivery_partner: Optional[DeliveryPartnerResponse]
    timeline: List[OrderTrackingTimelineStep]
    
    # Details for bottom sheet
    restaurant_name: str
    items: List[OrderItemResponse]
    
    # Bill
    item_total: Decimal
    delivery_fee: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
