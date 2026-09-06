from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_restaurant
from app.schemas import APIResponse, DashboardResponse, DashboardSummary, QuickAction
from app.models import Restaurant, get_enum_val
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/today-summary", response_model=APIResponse)
def get_today_summary(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get today's dashboard summary"""
    summary_data = DashboardService.get_today_summary(db, restaurant.id)
    
    return APIResponse(
        success=True,
        message="Dashboard summary retrieved successfully",
        data=summary_data
    )


@router.get("/quick-actions", response_model=APIResponse)
def get_quick_actions():
    """Get quick action items"""
    actions = DashboardService.get_quick_actions()
    
    return APIResponse(
        success=True,
        message="Quick actions retrieved successfully",
        data={"actions": actions}
    )


@router.get("/overview", response_model=APIResponse)
def get_dashboard_overview(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get complete dashboard overview with all-time statistics"""
    total_summary = DashboardService.get_total_summary(db, restaurant.id)
    actions = DashboardService.get_quick_actions()
    
    return APIResponse(
        success=True,
        message="Dashboard overview retrieved successfully",
        data={
            "summary": total_summary,
            "quick_actions": actions
        }
    )


@router.get("/restaurant-status", response_model=APIResponse)
def get_restaurant_status(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get restaurant status with location for dashboard header"""
    # Get restaurant address for location
    location = None
    if restaurant.address:
        location = {
            "latitude": float(restaurant.address.latitude) if restaurant.address.latitude else None,
            "longitude": float(restaurant.address.longitude) if restaurant.address.longitude else None,
            "address": restaurant.address.address_line_1,
            "city": restaurant.address.city
        }
    
    return APIResponse(
        success=True,
        message="Restaurant status retrieved successfully",
        data={
            "restaurant_id": restaurant.id,
            "restaurant_name": restaurant.restaurant_name,
            "is_open": restaurant.is_open,
            "location": location,
            "opening_time": str(restaurant.opening_time) if restaurant.opening_time else None,
            "closing_time": str(restaurant.closing_time) if restaurant.closing_time else None,
            "verification_status": get_enum_val(restaurant.verification_status)
        }
    )


@router.put("/toggle-status", response_model=APIResponse)
def toggle_restaurant_status(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Toggle restaurant online/offline status"""
    try:
        # Toggle the status
        restaurant.is_open = not restaurant.is_open
        db.commit()
        db.refresh(restaurant)
        
        status_text = "online" if restaurant.is_open else "offline"
        
        return APIResponse(
            success=True,
            message=f"Restaurant is now {status_text}",
            data={
                "restaurant_id": restaurant.id,
                "restaurant_name": restaurant.restaurant_name,
                "is_open": restaurant.is_open,
                "status": status_text
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle restaurant status: {str(e)}"
        )
