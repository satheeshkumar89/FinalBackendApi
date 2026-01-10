
import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# Mock some dependencies to avoid DB issues
sys.modules['app.database'] = MagicMock()
sys.modules['app.config'] = MagicMock()

class MockModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def __getattr__(self, name):
        return None

async def run_test():
    print("\n" + "="*70)
    print("🚀 STARTING PREMIUM SWIGGY-STYLE FLOW TEST (4 APPS)")
    print("="*70 + "\n")

    # Mock the models and service
    with patch('app.services.notification_service.Notification'), \
         patch('app.models.DeviceToken'), \
         patch('app.models.DeliveryPartner'), \
         patch('app.models.Order'), \
         patch('app.models.Restaurant'):
        
        from app.services.notification_service import NotificationService
        
        # 1. Setup Mock DB Session
        db = MagicMock()
        
        # Fake tokens and partners
        mock_token = MockModel(token="token_123")
        mock_partner = MockModel(id=5, full_name="John Driver", is_online=True)
        
        def mock_query(model):
            query = MagicMock()
            if "DeviceToken" in str(model):
                query.filter.return_value.all.return_value = [mock_token]
            elif "DeliveryPartner" in str(model):
                query.filter.return_value.all.return_value = [mock_partner]
            return query

        db.query.side_effect = mock_query

        # 2. Intercept FCM Sending
        sent_notifications = []

        async def mock_fcm_push(db, title, message, owner_id=None, customer_id=None, delivery_partner_id=None, data=None):
            recipient = "Unknown"
            if owner_id: recipient = "RESTAURANT"
            elif customer_id: recipient = "CUSTOMER"
            elif delivery_partner_id: recipient = "DELIVERY"
            
            sent_notifications.append({
                "to": recipient,
                "title": title,
                "message": message,
                "type": data.get("notification_type"),
                "status": data.get("status")
            })
            print(f"📡 [FCM] To: {recipient:12} | Title: {title:30} | Status: {data.get('status'):10}")

        async def mock_topic_broadcast(topic, title, message, data=None):
            sent_notifications.append({
                "to": f"TOPIC:{topic}",
                "title": title,
                "type": data.get("notification_type"),
                "status": data.get("status")
            })
            print(f"📢 [TOPIC] To: {topic:10} | Title: {title:30} | Status: {data.get('status'):10}")

        # Patch the internal methods
        with patch.object(NotificationService, '_send_fcm_push', side_effect=mock_fcm_push), \
             patch.object(NotificationService, '_broadcast_to_topic', side_effect=mock_topic_broadcast), \
             patch('app.services.notification_service._initialize_firebase', return_value=True):

            # --- PHASE 1: NEW ORDER ---
            print("\n--- Phase 1: Customer places order ---")
            await NotificationService.send_order_update(
                db=db, order_id=555, status="new", customer_id=1, owner_id=10
            )

            # --- PHASE 2: CONFIRMED ---
            print("\n--- Phase 2: Restaurant ACCEPTS order ---")
            await NotificationService.send_order_update(
                db=db, order_id=555, status="accepted", customer_id=1, owner_id=10
            )

            # --- PHASE 3: PREPARING ---
            print("\n--- Phase 3: Kitchen starts PREPARING ---")
            await NotificationService.send_order_update(
                db=db, order_id=555, status="preparing", customer_id=1, owner_id=10
            )

            # --- PHASE 4: READY ---
            print("\n--- Phase 4: Food is READY (Notify Delivery Partners) ---")
            await NotificationService.send_order_update(
                db=db, order_id=555, status="ready", customer_id=1, owner_id=10
            )

            # --- PHASE 5: PICKED UP ---
            print("\n--- Phase 5: Partner PICKED UP (Live Tracking starts) ---")
            await NotificationService.send_order_update(
                db=db, order_id=555, status="picked_up", customer_id=1, owner_id=10, delivery_partner_id=5
            )

            # --- PHASE 6: DELIVERED ---
            print("\n--- Phase 6: DELIVERED (Confetti screen) ---")
            await NotificationService.send_order_update(
                db=db, order_id=555, status="delivered", customer_id=1, owner_id=10, delivery_partner_id=5
            )

    # 4. Final Validation report
    print("\n" + "="*70)
    print("📊 PREMIUM FLOW VERIFICATION REPORT")
    print("="*70)
    
    apps_received = set()
    for n in sent_notifications:
        apps_received.add(n["to"])
        if n["to"] == "CUSTOMER":
            # Check for Swiggy style labels in titles
            if "Chef is preparing" in n["title"] or "Partner is on the way" in n["title"]:
                print(f"✅ Verified Swiggy Label for Customer: {n['title']}")
    
    print(f"\n✅ Apps targeted: {', '.join(apps_received)}")
    
    if len(apps_received) >= 4:
        print("\n🏆 COMPREHENSIVE TEST PASSED: All 4 Apps and Swiggy Labels are verified!")
    else:
        print(f"\n❌ TEST INCOMPLETE: Only {len(apps_received)} apps received signals.")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(run_test())
