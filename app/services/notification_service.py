import firebase_admin
from firebase_admin import credentials, messaging
import os
from sqlalchemy.orm import Session
from app.models import Notification, DeviceToken
from typing import Optional, List

from app.services.firebase_service import FirebaseService

def _initialize_firebase():
    return FirebaseService.initialize()

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
            title = "Order Rejected"
            message = "Sorry, the restaurant cannot fulfill your order right now."
        elif status == "accepted":
            title = "Order Confirmed! 🎉"
            message = f"Restaurant has accepted your order #{order_id}."
        elif status == "preparing":
            title = "Chef is preparing your food 👨‍🍳"
            message = "Your delicious meal is being cooked with care."
        elif status == "ready":
            title = "Food is ready! 🛍️"
            message = "Your order is packed and waiting for the delivery partner."
        elif status == "picked_up":
            title = "Partner is on the way! 🛵"
            message = "Your delivery partner has picked up your order and is coming to you."
        elif status == "delivered":
            title = "Order Delivered! 🍽️"
            message = "Enjoy your meal! Don't forget to rate your experience."
        else:
            title = "Order Update"
            message = f"Your order #{order_id} is now {status.replace('_', ' ')}."
        
        if status == "new":
            owner_notification_type = "new_order"
            owner_title = "New Order Received! 🛍️"
            owner_message = f"You have a new order #{order_id}."
        else:
            owner_notification_type = "order_update"
            owner_title = f"Order #{order_id} Update"
            owner_message = f"Order status changed to {status}"

        # Save to database for each relevant user
        if customer_id:
            await NotificationService.create_notification(
                db, 
                customer_id=customer_id,
                title=title,
                message=message,
                notification_type="order_update",
                order_id=order_id,
                status=status
            )
            
        if owner_id:
            await NotificationService.create_notification(
                db, 
                owner_id=owner_id,
                title=owner_title,
                message=owner_message,
                notification_type=owner_notification_type,
                order_id=order_id,
                status=status
            )

        if delivery_partner_id:
            await NotificationService.create_notification(
                db,
                delivery_partner_id=delivery_partner_id,
                title=title,
                message=message,
                notification_type="order_update",
                order_id=order_id,
                status=status
            )
        
        # Notify nearby online delivery partners if order is available for pickup
        if status in ["new", "accepted", "preparing", "ready", "handed_over"] and not delivery_partner_id:
            from app.models import DeliveryPartner, Order, Address
            import math

            # 1. Get Restaurant Location
            order = db.query(Order).filter(Order.id == order_id).first()
            restaurant_location = None
            if order:
                restaurant_address = db.query(Address).filter(Address.restaurant_id == order.restaurant_id).first()
                if restaurant_address and restaurant_address.latitude and restaurant_address.longitude:
                    restaurant_location = (float(restaurant_address.latitude), float(restaurant_address.longitude))

            # 2. Get all online partners
            online_partners = db.query(DeliveryPartner).filter(
                DeliveryPartner.is_online == True,
                DeliveryPartner.is_active == True
            ).all()
            
            for partner in online_partners:
                should_notify = True # Default to True if coordinates missing for backward compatibility
                
                # 3. Calculate Distance if both have coordinates
                if restaurant_location and partner.latitude and partner.longitude:
                    partner_loc = (float(partner.latitude), float(partner.longitude))
                    
                    # Haversine formula for distance calculation (in kilometers)
                    R = 6371.0 # Earth radius
                    lat1, lon1 = math.radians(restaurant_location[0]), math.radians(restaurant_location[1])
                    lat2, lon2 = math.radians(partner_loc[0]), math.radians(partner_loc[1])
                    
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    
                    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                    distance = R * c
                    
                    # Only notify if within 5.0 KM
                    if distance > 5.0:
                        should_notify = False
                
                if should_notify:
                    await NotificationService.create_notification(
                        db,
                        delivery_partner_id=partner.id,
                        title=f"New Order #{order_id} Available!",
                        message="A new order is available nearby. Tap to see details.",
                        notification_type="new_available_order",
                        order_id=order_id,
                        status=status
                    )
        
        # BROADCAST TO ADMINS (via FCM Topic)
        # Any admin app subscribed to 'admin_updates' will receive this
        await NotificationService._broadcast_to_topic(
            topic="admin_updates",
            title=f"Order #{order_id}: {status}",
            message=f"Order {order_id} has moved to {status}",
            data={
                "notification_type": "admin_order_refresh",
                "order_id": str(order_id),
                "status": status
            }
        )

        print(f"Notifications sent for Order #{order_id} - Status: {status}")
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
        order_id: Optional[int] = None,
        status: Optional[str] = None
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
                "order_id": str(order_id) if order_id else "",
                "status": status or "",
                "click_action": "FLUTTER_NOTIFICATION_CLICK"
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
                # Clean up dead tokens
                tokens_to_deactivate = []
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        error_msg = str(resp.exception)
                        print(f"   - Error for token {tokens[idx][:20]}...: {error_msg}")
                        # If token is invalid or not found, mark it as inactive
                        if "not-found" in error_msg.lower() or "invalid-registration" in error_msg.lower() or "Requested entity was not found" in error_msg:
                            tokens_to_deactivate.append(tokens[idx])
                
                if tokens_to_deactivate:
                    db.query(DeviceToken).filter(DeviceToken.token.in_(tokens_to_deactivate)).update({"is_active": False}, synchronize_session=False)
                    db.commit()
                    print(f"   - Deactivated {len(tokens_to_deactivate)} dead tokens from database")

        except Exception as e:
            print(f"❌ Error during FCM multicast send: {e}")

    @staticmethod
    async def _broadcast_to_topic(topic: str, title: str, message: str, data: dict = None):
        """Send FCM notification to all devices subscribed to a topic (e.g., admins)"""
        if not _initialize_firebase():
            return
        
        try:
            fcm_message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=message
                ),
                topic=topic,
                data=data or {}
            )
            response = messaging.send(fcm_message)
            print(f"✅ Successfully broadcasted to topic '{topic}': {response}")
        except Exception as e:
            print(f"❌ Error during topic broadcast: {e}")
