import sys
import os
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base
from app.models import Restaurant, Address, Customer, CustomerAddress, Cart, CartItem, MenuItem, Category
from app.routers.customer import calculate_cart_totals

def run_image_flow_test():
    print("=" * 70)
    print("🧪 SIMULATION TEST: Image Flow ('Amaravati nattu kozhi Virunthu')")
    print("=" * 70)

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # 1. Create Customer
        customer = Customer(phone_number="+919876543210", full_name="Test Customer")
        db.add(customer)
        db.flush()

        # 2. Create Restaurant: Amaravati nattu kozhi Virunthu (Dharapuram, TN: 10.73, 77.52)
        restaurant = Restaurant(
            owner_id=1,
            restaurant_name="Amaravati nattu kozhi Virunthu",
            restaurant_type="restaurant",
            fssai_license_number="12345678901234",
            opening_time="09:00",
            closing_time="22:00",
            is_active=True,
            is_open=True
        )
        db.add(restaurant)
        db.flush()

        res_addr = Address(
            restaurant_id=restaurant.id,
            latitude=Decimal("10.7300"),
            longitude=Decimal("77.5200"),
            address_line_1="Main Road",
            city="Dharapuram",
            state="Tamil Nadu",
            pincode="638656"
        )
        db.add(res_addr)

        # 3. Create Category & Menu Item: Nattu kozhi Chinthamani (OG) @ ₹400.00
        category = Category(name="Non-Veg Specials", is_active=True)
        db.add(category)
        db.flush()

        menu_item = MenuItem(
            restaurant_id=restaurant.id,
            category_id=category.id,
            name="Nattu kozhi Chinthamani (OG)",
            price=Decimal("400.00"),
            is_available=True
        )
        db.add(menu_item)
        db.flush()

        # 4. Create Customer Address in North India (Delhi: 28.6139, 77.2090 ~ 1,986 km away)
        customer_addr = CustomerAddress(
            customer_id=customer.id,
            latitude=Decimal("28.6139"),
            longitude=Decimal("77.2090"),
            address_line_1="Connaught Place",
            city="New Delhi",
            state="Delhi",
            pincode="110001",
            is_default=True
        )
        db.add(customer_addr)
        db.commit()

        # 5. Create Cart & Add 1 Item
        cart = Cart(customer_id=customer.id, restaurant_id=restaurant.id)
        db.add(cart)
        db.flush()

        cart_item = CartItem(cart_id=cart.id, menu_item_id=menu_item.id, quantity=1)
        db.add(cart_item)
        db.commit()

        # Refresh cart from DB
        cart = db.query(Cart).filter(Cart.customer_id == customer.id).first()

        # 6. Calculate Totals
        cart_totals = calculate_cart_totals(cart, db)

        print("\n📊 --- BILL DETAILS BEFORE VS AFTER FIX ---")
        print(f"Restaurant Name : {restaurant.restaurant_name}")
        print(f"Cart Item       : {menu_item.name} x 1")
        print(f"--------------------------------------------------")
        print(f"Item Total      : ₹{cart_totals.item_total:.2f}  (Expected: ₹400.00)")
        print(f"Delivery Charges: ₹{cart_totals.delivery_fee:.2f}  (Old Bug: ₹13,920.64 -> Capped Fix: ₹150.00)")
        print(f"Taxes & Charges : ₹{cart_totals.tax_amount:.2f}   (Expected: ₹20.00)")
        print(f"--------------------------------------------------")
        print(f"Total Amount    : ₹{cart_totals.total_amount:.2f}  (Old Bug: ₹14,340.64 -> Capped Fix: ₹570.00)")
        print(f"==================================================")

        # Assertions
        assert cart_totals.item_total == Decimal("400.00"), f"Item Total mismatch: {cart_totals.item_total}"
        assert cart_totals.delivery_fee == Decimal("150.00"), f"Delivery fee should be capped at 150.00, got: {cart_totals.delivery_fee}"
        assert cart_totals.tax_amount == Decimal("20.00"), f"Tax amount mismatch: {cart_totals.tax_amount}"
        assert cart_totals.total_amount == Decimal("570.00"), f"Total amount mismatch: {cart_totals.total_amount}"

        print("\n✅ SIMULATION TEST PASSED PERFECTLY!")
        print("The capped delivery fee fix prevents the ₹13,920.64 bug in the cart flow!")
        return True

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n❌ SIMULATION TEST FAILED: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    run_image_flow_test()
