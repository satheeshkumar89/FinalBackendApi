import sys
import os
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base
from app.models import Restaurant, Address, Customer, CustomerAddress, CustomerLocation, Cart, CartItem, MenuItem, Category
from app.routers.customer import calculate_cart_totals

def run_test():
    print("=" * 60)
    print("🧪 Testing Delivery Fee Calculation Logic")
    print("=" * 60)

    # 1. Setup SQLite memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Create category, customer, restaurant, menu item
        customer = Customer(phone_number="+919876543210", full_name="Test Customer")
        db.add(customer)
        db.flush()

        restaurant = Restaurant(
            owner_id=1,
            restaurant_name="Test Restaurant",
            restaurant_type="restaurant",
            fssai_license_number="12345678901234",
            opening_time="09:00",
            closing_time="22:00",
            is_active=True,
            is_open=True
        )
        db.add(restaurant)
        db.flush()

        # Restaurant Address: Latitude 12.9716, Longitude 77.5946 (MG Road Bengaluru)
        res_addr = Address(
            restaurant_id=restaurant.id,
            latitude=Decimal("12.9716"),
            longitude=Decimal("77.5946"),
            address_line_1="MG Road",
            city="Bengaluru",
            state="Karnataka",
            pincode="560001"
        )
        db.add(res_addr)

        category = Category(name="Fast Food", is_active=True)
        db.add(category)
        db.flush()

        menu_item = MenuItem(
            restaurant_id=restaurant.id,
            category_id=category.id,
            name="Burger",
            price=Decimal("100.00"),
            is_available=True
        )
        db.add(menu_item)
        db.flush()

        # Create cart
        cart = Cart(customer_id=customer.id, restaurant_id=restaurant.id)
        db.add(cart)
        db.flush()

        cart_item = CartItem(cart_id=cart.id, menu_item_id=menu_item.id, quantity=1)
        db.add(cart_item)
        db.commit()

        # Refresh cart from DB with relationship
        cart = db.query(Cart).filter(Cart.customer_id == customer.id).first()

        # --- TEST 1: Fallback (No customer address or coordinates) ---
        print("\nTest 1: Fallback (No customer address)")
        totals = calculate_cart_totals(cart, db)
        print(f"Calculated delivery fee: {totals.delivery_fee}")
        assert totals.delivery_fee == Decimal("40.0"), f"Expected 40.0, got {totals.delivery_fee}"
        print("✅ Test 1 Passed!")

        # --- TEST 2: Local distance (< 3 km) ---
        # Customer address: Latitude 12.9800, Longitude 77.5900 (around 1.1 km away)
        print("\nTest 2: Local distance (< 3 km)")
        addr_local = CustomerAddress(
            customer_id=customer.id,
            latitude=Decimal("12.9800"),
            longitude=Decimal("77.5900"),
            address_line_1="Cubbon Park",
            city="Bengaluru",
            state="Karnataka",
            pincode="560001",
            is_default=True
        )
        db.add(addr_local)
        db.commit()

        # Refresh cart & test
        totals = calculate_cart_totals(cart, db)
        print(f"Calculated delivery fee: {totals.delivery_fee}")
        assert totals.delivery_fee == Decimal("40.0"), f"Expected 40.0, got {totals.delivery_fee}"
        print("✅ Test 2 Passed!")

        # --- TEST 3: Long distance (>= 3 km) ---
        # Customer address: Latitude 13.0350, Longitude 77.5970 (around 7.07 km away)
        # Distance extra = 7.07 - 3.0 = 4.07 km
        # Expected fee = 40.0 + 4.07 * 7.0 = 40.0 + 28.49 = 68.49
        print("\nTest 3: Long distance (>= 3 km)")
        # Unset default of previous address
        addr_local.is_default = False
        
        addr_long = CustomerAddress(
            customer_id=customer.id,
            latitude=Decimal("13.0350"),
            longitude=Decimal("77.5970"),
            address_line_1="Hebbal",
            city="Bengaluru",
            state="Karnataka",
            pincode="560024",
            is_default=True
        )
        db.add(addr_long)
        db.commit()

        # Calculate distance mathematically to verify exact expectations:
        # Haversine distance for Hebbal:
        # r_lat = 12.9716, r_lng = 77.5946
        # c_lat = 13.0350, c_lng = 77.5970
        # extra_km = distance - 3.0
        # fee = 40.0 + round(extra_km * 7.0, 2)
        import math
        dlat = math.radians(13.0350 - 12.9716)
        dlon = math.radians(77.5970 - 77.5946)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(12.9716)) * math.cos(math.radians(13.0350)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        dist = 6371.0 * c
        expected_fee = Decimal("40.0") + Decimal(str(round((dist - 3.0) * 7.0, 2)))

        totals = calculate_cart_totals(cart, db)
        print(f"Distance calculated: {dist:.2f} km")
        print(f"Calculated delivery fee: {totals.delivery_fee}")
        print(f"Expected delivery fee: {expected_fee}")
        assert totals.delivery_fee == expected_fee, f"Expected {expected_fee}, got {totals.delivery_fee}"
        print("✅ Test 3 Passed!")

        # --- TEST 4: Specific address_id passed ---
        print("\nTest 4: Specific address_id")
        # Pass Cubbon park address (id = addr_local.id) explicitly
        totals = calculate_cart_totals(cart, db, address_id=addr_local.id)
        print(f"Calculated delivery fee (explicit Cubbon Park): {totals.delivery_fee}")
        assert totals.delivery_fee == Decimal("40.0"), f"Expected 40.0, got {totals.delivery_fee}"
        print("✅ Test 4 Passed!")

        # --- TEST 5: Fallback to CustomerLocation ---
        print("\nTest 5: Fallback to CustomerLocation")
        # Remove addresses to test fallback to CustomerLocation
        db.delete(addr_local)
        db.delete(addr_long)
        db.commit()

        # Add CustomerLocation: Latitude 13.0350, Longitude 77.5970
        loc = CustomerLocation(
            customer_id=customer.id,
            latitude=13.0350,
            longitude=77.5970,
            address="Hebbal"
        )
        db.add(loc)
        db.commit()

        totals = calculate_cart_totals(cart, db)
        print(f"Calculated delivery fee (using location): {totals.delivery_fee}")
        assert totals.delivery_fee == expected_fee, f"Expected {expected_fee}, got {totals.delivery_fee}"
        print("✅ Test 5 Passed!")

        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
        return True

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ TEST FAILED: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    run_test()
