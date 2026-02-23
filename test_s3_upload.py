#!/usr/bin/env python3
"""
Test S3 image upload for restaurant 8668109712
Usage:
  Step 1 (send OTP):  python3 test_s3_upload.py
  Step 2 (use OTP):   python3 test_s3_upload.py <OTP>
"""

import requests
import sys
import json
from datetime import datetime

BASE_URL = "https://dharaidelivery.online"
PHONE = "8668109712"

print("=" * 60)
print("🧪 FastFoodie S3 Upload Test")
print(f"📱 Restaurant: {PHONE}")
print(f"🌐 Server: {BASE_URL}")
print("=" * 60)

# ─── Step 1: Send OTP ────────────────────────────────────────
if len(sys.argv) < 2:
    print("\n[1/1] Sending OTP to phone...")
    r = requests.post(f"{BASE_URL}/auth/send-otp", json={"phone_number": PHONE})
    print(f"  Status: {r.status_code}")
    data = r.json()
    otp_hint = data.get("data", {}).get("otp", "")
    if otp_hint:
        print(f"  ✅ OTP (dev mode): {otp_hint}")
    else:
        print(f"  ✅ OTP sent to {PHONE}")
    print(f"\n  Now run: python3 test_s3_upload.py <OTP>")
    sys.exit(0)

otp = sys.argv[1]
print(f"\n  Using OTP: {otp}")

# ─── Step 2: Verify OTP ──────────────────────────────────────
print(f"\n[1/4] Verifying OTP...")
r = requests.post(f"{BASE_URL}/auth/verify-otp", json={"phone_number": PHONE, "otp": otp})
print(f"  Status: {r.status_code}")
data = r.json()

token = data.get("data", {}).get("access_token") or data.get("access_token")
if not token:
    print(f"  ❌ Login failed: {json.dumps(data, indent=2)}")
    sys.exit(1)
print(f"  ✅ Token obtained!")

headers = {"Authorization": f"Bearer {token}"}

# ─── Step 3: Get Presigned URL ───────────────────────────────
print("\n[2/4] Getting S3 presigned URL...")
r = requests.get(
    f"{BASE_URL}/restaurant/documents/presigned-url",
    params={"document_type": "menu_images", "filename": "test_menu.jpg"},
    headers=headers
)
print(f"  Status: {r.status_code}")
data = r.json()
print(f"  Response: {json.dumps(data, indent=2)[:500]}")

presigned_url = data.get("data", {}).get("upload_url") or data.get("upload_url") or data.get("data", {}).get("url")
file_key = data.get("data", {}).get("file_key") or data.get("file_key")
file_url = data.get("data", {}).get("file_url") or data.get("file_url")

if not presigned_url:
    print("  ❌ No presigned URL in response")
    sys.exit(1)

print(f"  ✅ Got presigned URL!")
print(f"  📁 Key: {file_key}")
# Check which region/bucket is in the URL
if "ap-south-1" in presigned_url:
    print(f"  🌏 Region: ap-south-1 (Mumbai) ✅")
elif "us-east-1" in presigned_url:
    print(f"  🌎 Region: us-east-1 (N. Virginia) ⚠️  Check bucket region!")
else:
    print(f"  🔗 URL prefix: {presigned_url[:80]}")

# ─── Step 4: Upload test image to S3 ─────────────────────────
print("\n[3/4] Uploading test image to S3...")
# Minimal valid 1x1 JPEG
test_image = bytes([
    0xFF,0xD8,0xFF,0xE0,0x00,0x10,0x4A,0x46,0x49,0x46,0x00,0x01,0x01,0x00,
    0x00,0x01,0x00,0x01,0x00,0x00,0xFF,0xDB,0x00,0x43,0x00,0x08,0x06,0x06,
    0x07,0x06,0x05,0x08,0x07,0x07,0x07,0x09,0x09,0x08,0x0A,0x0C,0x14,0x0D,
    0x0C,0x0B,0x0B,0x0C,0x19,0x12,0x13,0x0F,0x14,0x1D,0x1A,0x1F,0x1E,0x1D,
    0x1A,0x1C,0x1C,0x20,0x24,0x2E,0x27,0x20,0x22,0x2C,0x23,0x1C,0x1C,0x28,
    0x37,0x29,0x2C,0x30,0x31,0x34,0x34,0x34,0x1F,0x27,0x39,0x3D,0x38,0x32,
    0x3C,0x2E,0x33,0x34,0x32,0xFF,0xC0,0x00,0x0B,0x08,0x00,0x01,0x00,0x01,
    0x01,0x01,0x11,0x00,0xFF,0xC4,0x00,0x1F,0x00,0x00,0x01,0x05,0x01,0x01,
    0x01,0x01,0x01,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x02,
    0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0A,0x0B,0xFF,0xDA,0x00,0x08,0x01,
    0x01,0x00,0x00,0x3F,0x00,0xFB,0xFF,0xD9
])

upload_resp = requests.put(
    presigned_url,
    data=test_image,
    headers={"Content-Type": "image/jpeg"}
)
print(f"  Status: {upload_resp.status_code}")
if upload_resp.status_code in [200, 204]:
    print("  ✅ Image uploaded to S3 successfully!")
else:
    print(f"  ❌ Upload failed: {upload_resp.text[:300]}")
    sys.exit(1)

# ─── Step 5: Add menu item ───────────────────────────────────
print("\n[4/4] Adding test menu item with image...")
menu_item = {
    "name": f"Test Item {datetime.now().strftime('%H:%M')}",
    "description": "Test item for S3 upload verification",
    "price": 99.0,
    "image_url": file_url,
    "is_vegetarian": True,
    "is_available": True
}
r = requests.post(f"{BASE_URL}/menu/item/add", json=menu_item, headers=headers)
print(f"  Status: {r.status_code}")
data = r.json()
print(f"  Response: {json.dumps(data, indent=2)}")

if r.status_code == 200 and data.get("success"):
    item_id = data.get("data", {}).get("id")
    print(f"\n🎉 ALL TESTS PASSED! Menu item created with S3 image.")
    print(f"  🖼️  Image URL: {file_url}")
    print(f"  🍽️  Menu Item ID: {item_id}")
    # Cleanup
    del_r = requests.delete(f"{BASE_URL}/menu/item/delete/{item_id}", headers=headers)
    print(f"  🗑️  Test item deleted: {'✅' if del_r.status_code == 200 else '❌'}")
else:
    print("\n⚠️  S3 upload worked but menu item creation failed.")

print("\n" + "=" * 60)
