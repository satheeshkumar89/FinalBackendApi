from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class DeliveryPartnerLocation(Base):
    """Track real-time location of delivery partners"""
    __tablename__ = "delivery_partner_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    delivery_partner_id = Column(Integer, ForeignKey("delivery_partners.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)  # Active order being delivered
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)  # GPS accuracy in meters
    bearing = Column(Float, nullable=True)  # Direction of movement (0-360 degrees)
    speed = Column(Float, nullable=True)  # Speed in m/s
    
    # Address details (reverse geocoded)
    address = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    delivery_partner = relationship("DeliveryPartner", backref="location_history")
    order = relationship("Order", backref="delivery_tracking")


class CustomerLocation(Base):
    """Track customer's delivery address location"""
    __tablename__ = "customer_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text, nullable=False)
    landmark = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer")
    order = relationship("Order")

    @property
    def customer_name(self):
        return self.customer.full_name if self.customer else None
