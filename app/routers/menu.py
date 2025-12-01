from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.dependencies import get_current_restaurant
from app.schemas import (
    MenuItemCreate, MenuItemUpdate, MenuItemResponse, APIResponse, MenuItemAvailability,
    CategoryResponse
)
from app.models import Restaurant, MenuItem, Category

router = APIRouter(prefix="/menu", tags=["Menu"])


# ============= Category Endpoints =============

@router.get("/categories", response_model=APIResponse)
def get_menu_categories(
    db: Session = Depends(get_db)
):
    """Get all active menu categories"""
    categories = db.query(Category).filter(
        Category.is_active == True
    ).order_by(Category.display_order, Category.name).all()
    
    category_list = [CategoryResponse.from_orm(cat).dict() for cat in categories]
    
    return APIResponse(
        success=True,
        message="Menu categories retrieved successfully",
        data={"categories": category_list}
    )


# ============= Menu Item Endpoints =============

@router.get("/items", response_model=APIResponse)
def get_menu_items(
    category_id: Optional[int] = Query(None, alias="category_id"),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get menu items, optionally filtered by category"""
    query = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant.id)
    
    if category_id:
        query = query.filter(MenuItem.category_id == category_id)
    
    items = query.all()
    
    return APIResponse(
        success=True,
        message="Menu items retrieved successfully",
        data={"items": [MenuItemResponse.from_orm(item).dict() for item in items]}
    )


@router.get("/items/grouped", response_model=APIResponse)
def get_menu_items_grouped(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Get menu items grouped by categories (for UI display)"""
    from collections import defaultdict
    
    # Check if categories exist, if not, try to seed them (Auto-Healing)
    category_count = db.query(Category).count()
    if category_count == 0:
        try:
            # Basic seed if table is empty
            default_cats = [
                "Starters", "Main Course", "Breads", "Rice & Biryani", 
                "Desserts", "Beverages", "Snacks", "Combos"
            ]
            for i, name in enumerate(default_cats):
                db.add(Category(name=name, display_order=i+1, is_active=True))
            db.commit()
        except Exception:
            db.rollback() # Ignore errors if seeding fails (e.g. concurrent request)

    # Get all menu items for this restaurant
    items = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant.id
    ).all()
    
    # Group items by category
    grouped_items = defaultdict(list)
    uncategorized_items = []
    
    for item in items:
        # Robust check: Ensure category_id is valid and category exists
        if item.category_id:
            # We fetch category name eagerly or fallback to "Unknown"
            # Ideally, we should join, but for now let's be safe
            if item.category:
                 category_key = item.category.name
                 grouped_items[category_key].append(MenuItemResponse.from_orm(item).dict())
            else:
                 # Category ID exists but record missing (Foreign Key issue?)
                 uncategorized_items.append(MenuItemResponse.from_orm(item).dict())
        else:
            uncategorized_items.append(MenuItemResponse.from_orm(item).dict())
    
    # Build response with category groups
    categories_with_items = []
    
    # Get all categories that have items
    for category_name, category_items in sorted(grouped_items.items()):
        # Get category details
        category = db.query(Category).filter(Category.name == category_name).first()
        
        categories_with_items.append({
            "category": CategoryResponse.from_orm(category).dict() if category else {"id": 0, "name": category_name, "is_active": True, "display_order": 0},
            "items": category_items,
            "item_count": len(category_items)
        })
    
    # Add uncategorized items if any
    if uncategorized_items:
        categories_with_items.append({
            "category": None,
            "items": uncategorized_items,
            "item_count": len(uncategorized_items)
        })
    
    return APIResponse(
        success=True,
        message="Menu items grouped by categories retrieved successfully",
        data={
            "categories": categories_with_items,
            "total_categories": len(categories_with_items),
            "total_items": len(items)
        }
    )



@router.post("/item/add", response_model=APIResponse)
def add_menu_item(
    item_data: MenuItemCreate,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Add new menu item"""
    try:
        # Validate category_id if provided
        if item_data.category_id:
            category = db.query(Category).filter(Category.id == item_data.category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with id {item_data.category_id} not found"
                )
        
        menu_item = MenuItem(
            restaurant_id=restaurant.id,
            name=item_data.name,
            description=item_data.description,
            price=item_data.price,
            discount_price=item_data.discount_price,
            image_url=item_data.image_url,
            category_id=item_data.category_id,
            is_vegetarian=item_data.is_vegetarian,
            is_available=item_data.is_available,
            preparation_time=item_data.preparation_time
        )
        
        db.add(menu_item)
        db.commit()
        db.refresh(menu_item)
        
        return APIResponse(
            success=True,
            message="Menu item added successfully",
            data=MenuItemResponse.from_orm(menu_item).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add menu item: {str(e)}"
        )


@router.put("/item/update/{item_id}", response_model=APIResponse)
def update_menu_item(
    item_id: int,
    item_data: MenuItemUpdate,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Update menu item"""
    try:
        # Get menu item
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant.id
        ).first()
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        # Validate category_id if provided
        if item_data.category_id is not None:
            if item_data.category_id > 0:
                category = db.query(Category).filter(Category.id == item_data.category_id).first()
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Category with id {item_data.category_id} not found"
                    )
        
        # Update fields
        update_data = item_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(menu_item, field, value)
        
        db.commit()
        db.refresh(menu_item)
        
        return APIResponse(
            success=True,
            message="Menu item updated successfully",
            data=MenuItemResponse.from_orm(menu_item).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update menu item: {str(e)}"
        )


@router.delete("/item/delete/{item_id}", response_model=APIResponse)
def delete_menu_item(
    item_id: int,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Delete menu item"""
    try:
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant.id
        ).first()
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        # Check if item is in any active orders
        # (You might want to add this check based on your business logic)
        
        db.delete(menu_item)
        db.commit()
        
        return APIResponse(
            success=True,
            message="Menu item deleted successfully",
            data={"deleted_item_id": item_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete menu item: {str(e)}"
        )


@router.put("/item/availability/{item_id}", response_model=APIResponse)
def update_item_availability(
    item_id: int,
    availability: MenuItemAvailability,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Update menu item availability"""
    try:
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant.id
        ).first()
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        menu_item.is_available = availability.is_available
        db.commit()
        db.refresh(menu_item)
        
        status_text = "available" if availability.is_available else "unavailable"
        
        return APIResponse(
            success=True,
            message=f"Menu item marked as {status_text}",
            data=MenuItemResponse.from_orm(menu_item).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update availability: {str(e)}"
        )


@router.put("/item/out-of-stock/{item_id}", response_model=APIResponse)
def mark_item_out_of_stock(
    item_id: int,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Mark menu item as out of stock (unavailable)"""
    try:
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant.id
        ).first()
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        menu_item.is_available = False
        db.commit()
        db.refresh(menu_item)
        
        return APIResponse(
            success=True,
            message="Menu item marked as out of stock",
            data=MenuItemResponse.from_orm(menu_item).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark item as out of stock: {str(e)}"
        )


@router.post("/item/duplicate/{item_id}", response_model=APIResponse)
def duplicate_menu_item(
    item_id: int,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    """Duplicate a menu item"""
    try:
        original_item = db.query(MenuItem).filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant.id
        ).first()
        
        if not original_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        # Create duplicate
        duplicate_item = MenuItem(
            restaurant_id=restaurant.id,
            name=f"{original_item.name} (Copy)",
            description=original_item.description,
            price=original_item.price,
            discount_price=original_item.discount_price,
            image_url=original_item.image_url,
            category_id=original_item.category_id,
            is_vegetarian=original_item.is_vegetarian,
            is_available=original_item.is_available,
            preparation_time=original_item.preparation_time
        )
        
        db.add(duplicate_item)
        db.commit()
        db.refresh(duplicate_item)
        
        return APIResponse(
            success=True,
            message="Menu item duplicated successfully",
            data=MenuItemResponse.from_orm(duplicate_item).dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to duplicate menu item: {str(e)}"
        )
