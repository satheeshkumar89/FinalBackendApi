# FastFoodie Restaurant Partner API

A complete backend API for FastFoodie restaurant partner application built with FastAPI, SQLAlchemy, MySQL, JWT Authentication, S3 Uploads, and WebSockets.

## 🚀 Features

- **JWT Authentication** with OTP-based login
- **Role-based Access Control** (Restaurant Partner only)
- **S3 File Uploads** for FSSAI license and restaurant photos
- **WebSocket Support** for live order notifications
- **Complete KYC Flow** for restaurant verification
- **Dashboard Metrics** with real-time statistics
- **Order Management** with status tracking
- **Menu Management** with CRUD operations

## 📋 Tech Stack

- **Framework**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0.23
- **Database**: MySQL
- **Authentication**: JWT (python-jose)
- **File Storage**: AWS S3 (boto3)
- **WebSockets**: Native FastAPI WebSocket support
- **Validation**: Pydantic

## 📁 Project Structure

```
fastfoodie-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── dependencies.py         # Auth dependencies
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── owner.py           # Owner profile endpoints
│   │   ├── restaurant.py      # Restaurant KYC endpoints
│   │   ├── dashboard.py       # Dashboard endpoints
│   │   ├── menu.py            # Menu management endpoints
│   │   └── orders.py          # Order management endpoints
│   └── services/
│       ├── __init__.py
│       ├── jwt_service.py     # JWT token management
│       ├── otp_service.py     # OTP generation/verification
│       ├── s3_service.py      # S3 upload service
│       ├── dashboard_service.py
│       └── verification_service.py
├── migrate.py                  # Database migration script
├── database_schema.sql         # MySQL schema
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md
```

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- MySQL 8.0+
- AWS Account (for S3)
- Redis (optional, for WebSocket pub/sub)

### Setup Steps

1. **Clone the repository**
   ```bash
   cd /Users/satheeshkumar/.gemini/antigravity/scratch/fastfoodie-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup MySQL Database**
   ```bash
   # Login to MySQL
   mysql -u root -p
   
   # Run the schema file
   source database_schema.sql
   ```

5. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

6. **Run Database Migration**
   ```bash
   python migrate.py
   ```

7. **Start the Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🔐 Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/fastfoodie

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=fastfoodie-uploads

# OTP
OTP_EXPIRY_MINUTES=5
OTP_LENGTH=6

# Redis
REDIS_URL=redis://localhost:6379

# Environment
ENVIRONMENT=development
```

## 📚 API Documentation

Once the server is running, access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/send-otp` | Send OTP to phone number |
| POST | `/auth/verify-otp` | Verify OTP and get JWT token |
| POST | `/auth/resend-otp` | Resend OTP |

### Owner Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/owner/details` | Create owner details |
| PUT | `/owner/details` | Update owner details |
| GET | `/owner/details` | Get owner details |

### Restaurant KYC

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/restaurant/types` | Get restaurant types |
| POST | `/restaurant/details` | Create restaurant details |
| PUT | `/restaurant/details` | Update restaurant details |
| GET | `/restaurant/details` | Get restaurant details |
| GET | `/restaurant/cuisines/available` | Get available cuisines |
| POST | `/restaurant/cuisines` | Add cuisines to restaurant |
| POST | `/restaurant/address` | Create restaurant address |
| PUT | `/restaurant/address` | Update restaurant address |
| POST | `/restaurant/documents/presigned-url` | Get S3 presigned URL |
| POST | `/restaurant/documents/confirm-upload` | Confirm document upload |
| POST | `/restaurant/submit-kyc` | Submit for verification |
| GET | `/restaurant/verification-status` | Get verification status |
| GET | `/restaurant/refresh-status` | Refresh verification status |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/today-summary` | Get today's summary |
| GET | `/dashboard/quick-actions` | Get quick actions |
| GET | `/dashboard/overview` | Get complete overview |

### Menu Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/menu/items` | Get all menu items |
| POST | `/menu/add-item` | Add new menu item |
| PUT | `/menu/update-item/{item_id}` | Update menu item |
| DELETE | `/menu/delete-item/{item_id}` | Delete menu item |
| GET | `/menu/item/{item_id}` | Get menu item details |

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders/new` | Get new orders |
| GET | `/orders/ongoing` | Get ongoing orders |
| GET | `/orders/completed` | Get completed orders |
| POST | `/orders/{order_id}/accept` | Accept order |
| POST | `/orders/{order_id}/reject` | Reject order |
| PUT | `/orders/{order_id}/update-status` | Update order status |
| GET | `/orders/{order_id}` | Get order details |
| WS | `/orders/live` | WebSocket for live orders |

## 🔄 Response Format

All API responses follow this standard format:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data here
  }
}
```

## 🔌 WebSocket Usage

Connect to live orders using WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/orders/live?token=YOUR_JWT_TOKEN');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New order:', data);
};

// Send ping to keep connection alive
setInterval(() => {
  ws.send('ping');
}, 30000);
```

## 📦 Database Models

- **Owner**: Restaurant owner details
- **Restaurant**: Restaurant information
- **Cuisine**: Available cuisines
- **RestaurantCuisine**: Restaurant-cuisine mapping
- **Address**: Restaurant address
- **Document**: Uploaded documents (FSSAI, photos)
- **OTP**: OTP records
- **DeviceToken**: Push notification tokens
- **MenuItem**: Menu items
- **Order**: Customer orders
- **OrderItem**: Order line items

## 🔒 Authentication Flow

1. User enters phone number
2. System sends OTP via SMS
3. User verifies OTP
4. System returns JWT token
5. Client includes token in Authorization header: `Bearer <token>`

## 📤 S3 Upload Flow

1. Request presigned URL: `POST /restaurant/documents/presigned-url`
2. Upload file directly to S3 using presigned URL
3. Confirm upload: `POST /restaurant/documents/confirm-upload`

## 🚦 Order Status Flow

```
NEW → ACCEPTED → PREPARING → READY → PICKED_UP → DELIVERED
  ↓
REJECTED
```

## 🧪 Testing

```bash
# Run with pytest (install pytest first)
pip install pytest pytest-asyncio httpx
pytest
```

## 🚀 Deployment

### Using Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📝 License

MIT License

## 👥 Support

For issues and questions, please contact the development team.

## 🔄 Version History

- **v1.0.0** - Initial release with complete API functionality
# FinalBackendApi
