from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from decimal import Decimal
from app.models import Order, OrderStatusEnum, Restaurant


class DashboardService:
    @staticmethod
    def get_today_summary(db: Session, restaurant_id: int) -> dict:
        """Get today's dashboard summary"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Get restaurant
        restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        
        # Total orders today
        total_orders = db.query(func.count(Order.id)).filter(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.created_at >= today_start,
                Order.created_at < today_end
            )
        ).scalar() or 0
        
        # Total earnings today (only from delivered orders)
        total_earnings = db.query(func.sum(Order.total_amount)).filter(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.created_at >= today_start,
                Order.created_at < today_end,
                Order.status == OrderStatusEnum.DELIVERED
            )
        ).scalar() or Decimal('0.00')
        
        # Pending orders count (awaiting restaurant acceptance)
        new_orders_count = db.query(func.count(Order.id)).filter(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatusEnum.PENDING
            )
        ).scalar() or 0
        
        # Ongoing orders count (accepted, preparing, ready - restaurant's active orders)
        ongoing_orders_count = db.query(func.count(Order.id)).filter(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status.in_([
                    OrderStatusEnum.ACCEPTED,
                    OrderStatusEnum.PREPARING,
                    OrderStatusEnum.READY
                ])
            )
        ).scalar() or 0
        
        # Yesterday's orders for growth calculation
        yesterday_start = today_start - timedelta(days=1)
        yesterday_orders = db.query(func.count(Order.id)).filter(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.created_at >= yesterday_start,
                Order.created_at < today_start
            )
        ).scalar() or 0
        
        today_growth = 0.0
        if yesterday_orders > 0:
            today_growth = ((total_orders - yesterday_orders) / yesterday_orders) * 100
        elif total_orders > 0:
            today_growth = 100.0
            
        return {
            "total_orders": total_orders,
            "total_earnings": total_earnings,
            "avg_rating": restaurant.average_rating if restaurant else Decimal('0.00'),
            "today_growth": round(today_growth, 2),
            "quick_action": DashboardService.get_quick_actions(),
            "new_orders_count": new_orders_count,
            "ongoing_orders_count": ongoing_orders_count
        }
    
    @staticmethod
    def get_quick_actions() -> list:
        """Get quick action items for dashboard"""
        return [
            {
                "id": "view_menu",
                "title": "View Menu",
                "icon": "menu_book",
                "route": "/menu"
            },
            {
                "id": "add_item",
                "title": "Add Item",
                "icon": "add_circle",
                "route": "/menu/add"
            },
            {
                "id": "view_orders",
                "title": "View Orders",
                "icon": "receipt_long",
                "route": "/orders"
            },
            {
                "id": "settings",
                "title": "Settings",
                "icon": "settings",
                "route": "/settings"
            }
        ]
    
    @staticmethod
    def get_total_summary(db: Session, restaurant_id: int) -> dict:
        """Get all-time (total) dashboard summary"""
        # Get restaurant
        restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        
        # Total orders (all time)
        total_orders = db.query(func.count(Order.id)).filter(
            Order.restaurant_id == restaurant_id
        ).scalar() or 0
        
        # Total earnings (all time - only delivered orders)
        total_earnings = db.query(func.sum(Order.total_amount)).filter(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatusEnum.DELIVERED
            )
        ).scalar() or Decimal('0.00')
        
        # Total delivered orders
        delivered_orders = db.query(func.count(Order.id)).filter(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatusEnum.DELIVERED
            )
        ).scalar() or 0
        
        # Total rejected orders
        rejected_orders = db.query(func.count(Order.id)).filter(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatusEnum.REJECTED
            )
        ).scalar() or 0
        
        # Total cancelled orders
        cancelled_orders = db.query(func.count(Order.id)).filter(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatusEnum.CANCELLED
            )
        ).scalar() or 0
        
        # Pending orders count (current)
        new_orders_count = db.query(func.count(Order.id)).filter(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatusEnum.PENDING
            )
        ).scalar() or 0
        
        # Ongoing orders count (current - restaurant's active orders)
        ongoing_orders_count = db.query(func.count(Order.id)).filter(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status.in_([
                    OrderStatusEnum.ACCEPTED,
                    OrderStatusEnum.PREPARING,
                    OrderStatusEnum.READY
                ])
            )
        ).scalar() or 0
        
        # Average order value
        avg_order_value = Decimal('0.00')
        if delivered_orders > 0:
            avg_order_value = total_earnings / delivered_orders
        
        # Success rate (delivered / total orders)
        success_rate = 0.0
        if total_orders > 0:
            success_rate = (delivered_orders / total_orders) * 100
        
        return {
            "total_orders": total_orders,
            "total_earnings": total_earnings,
            "delivered_orders": delivered_orders,
            "rejected_orders": rejected_orders,
            "cancelled_orders": cancelled_orders,
            "avg_order_value": round(avg_order_value, 2),
            "success_rate": round(success_rate, 2),
            "avg_rating": restaurant.average_rating if restaurant else Decimal('0.00'),
            "new_orders_count": new_orders_count,
            "ongoing_orders_count": ongoing_orders_count
        }
