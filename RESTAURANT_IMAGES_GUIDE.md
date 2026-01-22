# How to Check and Add Restaurant Images

## Problem
Your restaurants are showing placeholder images (mountain icon) because they don't have banner photos uploaded.

## Where Restaurant Images Are Stored

Restaurant banner images are stored in the **`documents`** table with:
- `document_type` = `'restaurant_photo'`
- `file_url` = URL to the image (S3 or any public URL)

## Solution 1: Check via API Documentation

1. Open: `https://dharaifooddelivery.in/docs`
2. Find the **Restaurant** section
3. Look for `GET /restaurant/documents` endpoint
4. You'll see which restaurants have photos

## Solution 2: Add Images via Restaurant Partner App

The Restaurant Partner App should have an option to upload banner images during onboarding or in settings.

**API Endpoint**: `POST /restaurant/documents/upload`

**Steps**:
1. Restaurant owner logs into the app
2. Goes to Profile/Settings
3. Uploads banner image
4. Image is stored in S3 and URL saved to database

## Solution 3: Add Images Directly via Database (Quick Fix)

If you want to add placeholder images quickly for testing:

```sql
-- Add a banner image for restaurant ID 1
INSERT INTO documents (restaurant_id, document_type, file_url, file_name)
VALUES (
    1,  -- Restaurant ID
    'restaurant_photo',
    'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800',  -- Sample restaurant image
    'banner.jpg'
);

-- Add for restaurant ID 2
INSERT INTO documents (restaurant_id, document_type, file_url, file_name)
VALUES (
    2,
    'restaurant_photo',
    'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800',
    'banner.jpg'
);

-- Add for restaurant ID 3
INSERT INTO documents (restaurant_id, document_type, file_url, file_name)
VALUES (
    3,
    'restaurant_photo',
    'https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=800',
    'banner.jpg'
);
```

## Solution 4: Update Customer App API Response

The customer app needs to fetch restaurant photos from the documents table.

**Current Issue**: The `/customer/home` endpoint returns restaurants but doesn't include their banner images.

**Fix Needed**: Update the API response to include `banner_url` field.

### Update Backend Code

**File**: `app/routers/customer.py`

**In the `/customer/home` endpoint** (around line 47-78), modify the restaurant serialization:

```python
@router.get("/home", response_model=APIResponse)
def get_home_data(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    """Get home screen data"""
    # Get categories
    categories = db.query(Category).filter(Category.is_active == True).order_by(Category.display_order).all()
    
    # Get restaurants
    restaurants = db.query(Restaurant).filter(
        Restaurant.is_active == True, 
        Restaurant.is_open == True
    ).all()
    
    # Build restaurant list with banner images
    restaurants_data = []
    for r in restaurants:
        r_dict = RestaurantResponse.from_orm(r).dict()
        
        # Get banner image from documents
        from app.models import Document
        banner = db.query(Document).filter(
            Document.restaurant_id == r.id,
            Document.document_type == 'restaurant_photo'
        ).first()
        
        r_dict['banner_url'] = banner.file_url if banner else None
        restaurants_data.append(r_dict)
    
    # Construct response
    data = {
        "categories": [CategoryResponse.from_orm(c).dict() for c in categories],
        "restaurants": restaurants_data,  # Use modified list
        "offers": [...]
    }
    
    return APIResponse(...)
```

## Solution 5: Sample Restaurant Images (For Testing)

Here are some free restaurant images you can use:

```
https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800  # Restaurant interior
https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800  # Restaurant food
https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=800  # Restaurant dining
https://images.unsplash.com/photo-1552566626-52f8b828add9?w=800  # Restaurant kitchen
https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800  # Restaurant ambiance
```

## Quick Test

After adding images, test in the Customer App:
1. Pull to refresh the home screen
2. Restaurant cards should now show banner images instead of placeholders
3. If still showing placeholders, check:
   - API response includes `banner_url` field
   - Flutter app is using the `banner_url` field
   - Image URLs are accessible (not blocked by CORS)

## Flutter App Update (If Needed)

If your Flutter app is not showing images even after adding them to the database, update the restaurant card widget:

```dart
// In restaurant_card.dart or similar
CachedNetworkImage(
  imageUrl: restaurant.bannerUrl ?? '',
  placeholder: (context, url) => CircularProgressIndicator(),
  errorWidget: (context, url, error) => Icon(Icons.restaurant),
  fit: BoxFit.cover,
)
```

Make sure the `Restaurant` model has a `bannerUrl` field:

```dart
class Restaurant {
  final int id;
  final String restaurantName;
  final String? bannerUrl;  // Add this field
  
  Restaurant.fromJson(Map<String, dynamic> json)
      : id = json['id'],
        restaurantName = json['restaurant_name'],
        bannerUrl = json['banner_url'];  // Parse from API
}
```

---

## Summary

**Root Cause**: Restaurants don't have banner images in the `documents` table.

**Quick Fix**: Add sample images using SQL INSERT statements above.

**Proper Fix**: 
1. Update backend API to include `banner_url` in restaurant responses
2. Ensure Restaurant Partner App allows uploading banner images
3. Update Customer App to display the banner images

**Test**: After adding images, refresh the Customer App home screen.
