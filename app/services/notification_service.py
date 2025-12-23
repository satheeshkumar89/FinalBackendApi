import firebase_admin
from firebase_admin import credentials, messaging
import os
from sqlalchemy.orm import Session
from app.models import Notification, DeviceToken
from typing import Optional, List

# Global variable to track firebase initialization
_firebase_initialized = False

def _initialize_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return True
        
    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "firebase-service-account.json")
    if os.path.exists(cred_path):
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            print("✅ Firebase initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            return False
    else:
        print(f"⚠️ Firebase service account key not found at {cred_path}. Push notifications will be skipped.")
        return False

class NotificationService:
    @staticmethod
    async def send_order_update(
        db: Session,
        order_id: int, 
        status: str, 
        customer_id: Optional[int] = None, 
        owner_id: Optional[int] = None,
        delivery_partner_id: Optional[int] = None
    ):
        """
        Send order update notification and save to database.
        """
        if status == "rejected":
            title = f"Order #{order_id} Rejected"
            message = "Sorry, the restaurant cannot fulfill your order at this time."
        else:
            title = f"Order #{order_id} Update"
            message = f"Your order is now {status.replace('_', ' ')}."
        
        # Save to database for each relevant user
        if customer_id:
            await NotificationService.create_notification(
                db, 
                customer_id=customer_id,
                title=title,
                message=message,
                notification_type="order_update",
                order_id=order_id
            )
            
        if owner_id:
            await NotificationService.create_notification(
                db, 
                owner_id=owner_id,
                title=f"New Order Update #{order_id}",
                message=f"Order status changed to {status}",
                notification_type="order_update",
                order_id=order_id
            )

        print(f"Notification triggered for Order #{order_id} - Status: {status}")
        return True

    @staticmethod
    async def create_notification(
        db: Session,
        title: str,
        message: str,
        notification_type: str,
        owner_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        delivery_partner_id: Optional[int] = None,
        order_id: Optional[int] = None
    ) -> Notification:
        # 1. Save to Database
        notification = Notification(
            owner_id=owner_id,
            customer_id=customer_id,
            delivery_partner_id=delivery_partner_id,
            title=title,
            message=message,
            notification_type=notification_type,
            order_id=order_id
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # 2. Trigger FCM Push
        await NotificationService._send_fcm_push(
            db=db,
            title=title,
            message=message,
            owner_id=owner_id,
            customer_id=customer_id,
            delivery_partner_id=delivery_partner_id,
            data={
                "notification_type": notification_type,
                "order_id": str(order_id) if order_id else ""
            }
        )
        
        return notification

    @staticmethod
    def create_notification_sync(
        db: Session,
        title: str,
        message: str,
        notification_type: str,
        owner_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        delivery_partner_id: Optional[int] = None,
        order_id: Optional[int] = None
    ) -> Notification:
        # This is used in sync contexts like verification service
        notification = Notification(
            owner_id=owner_id,
            customer_id=customer_id,
            delivery_partner_id=delivery_partner_id,
            title=title,
            message=message,
            notification_type=notification_type,
            order_id=order_id
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # We don't trigger push here because this is sync, 
        # or we could try to trigger it in a fire-and-forget way if needed.
        
        return notification

    @staticmethod
    async def _send_fcm_push(
        db: Session,
        title: str,
        message: str,
        owner_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        delivery_partner_id: Optional[int] = None,
        data: Optional[dict] = None
    ):
        """Internal method to send push via Firebase"""
        if not _initialize_firebase():
            return

        # Query active device tokens
        query = db.query(DeviceToken).filter(DeviceToken.is_active == True)
        if owner_id:
            query = query.filter(DeviceToken.owner_id == owner_id)
        elif customer_id:
            query = query.filter(DeviceToken.customer_id == customer_id)
        elif delivery_partner_id:
            query = query.filter(DeviceToken.delivery_partner_id == delivery_partner_id)
        else:
            return

        tokens = [t.token for t in query.all()]
        if not tokens:
            print(f"No active device tokens found for user")
            return

        try:
            # Construct standard notification
            fcm_notification = messaging.Notification(
                title=title,
                body=message
            )
            
            # Use multicast for multiple tokens
            response = messaging.send_each_for_multicast(
                messaging.MulticastMessage(
                    notification=fcm_notification,
                    tokens=tokens,
                    data=data or {}
                )
            )
            print(f"✅ Successfully sent {response.success_count} FCM messages")
            if response.failure_count > 0:
                print(f"❌ Failed to send {response.failure_count} FCM messages")
        except Exception as e:
            print(f"❌ Error during FCM multicast send: {e}")
