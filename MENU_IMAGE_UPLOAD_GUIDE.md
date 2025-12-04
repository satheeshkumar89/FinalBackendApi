# Menu Item Image Upload Guide

To upload an image for a menu item, you need to follow a 2-step process. You cannot send the image file directly to the `/menu/item/add` endpoint.

## Step 1: Get Presigned URL & Upload Image

First, upload the image to S3 using a presigned URL.

### 1. Request Presigned URL
**POST** `/restaurant/documents/presigned-url`

**Query Parameters:**
- `document_type`: `menu_item_image`
- `filename`: `pizza.jpg` (your file name)
- `content_type`: `image/jpeg` (your file mime type)

**Response:**
```json
{
  "success": true,
  "data": {
    "upload_url": "https://s3.amazonaws.com/...",  // Use this to upload
    "public_url": "https://bucket.s3.../image.jpg", // SAVE THIS for Step 2
    "file_key": "menu_item_image/..."
  }
}
```

### 2. Upload File to S3
Make a `PUT` request to the `upload_url` you received.
- **URL**: `data['upload_url']`
- **Method**: `PUT`
- **Headers**: `Content-Type: <your_image_mime_type>` (e.g., image/jpeg)
- **Body**: The binary file data (bytes of the image).

---

## Step 2: Create Menu Item with Image URL

Once the upload is successful, use the `public_url` from Step 1 in your create item request.

**POST** `/menu/item/add`

**Body:**
```json
{
  "name": "Test Item",
  "description": "test desc",
  "price": 120.0,
  "discount_price": 0,
  "image_url": "https://bucket.s3.../image.jpg",  <-- PASTE PUBLIC_URL HERE
  "category_id": 80,
  "is_vegetarian": false,
  "is_available": true,
  "preparation_time": 10
}
```

## Flutter Example Code

```dart
Future<void> addMenuItemWithImage(File imageFile) async {
  // 1. Get Presigned URL
  final presignedRes = await api.post(
    '/restaurant/documents/presigned-url', 
    params: {
      'document_type': 'menu_item_image',
      'filename': 'item.jpg',
      'content_type': 'image/jpeg',
    }
  );
  
  String uploadUrl = presignedRes['data']['upload_url'];
  String publicUrl = presignedRes['data']['public_url'];

  // 2. Upload Image to S3
  await http.put(
    Uri.parse(uploadUrl),
    headers: {'Content-Type': 'image/jpeg'},
    body: await imageFile.readAsBytes(),
  );

  // 3. Create Menu Item
  await api.post('/menu/item/add', data: {
    "name": "Test Item",
    "price": 120.0,
    "image_url": publicUrl, // <--- Use the URL here
    "category_id": 80,
    // ... other fields
  });
}
```
