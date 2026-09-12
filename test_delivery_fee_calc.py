from decimal import Decimal
import math

def calculate_delivery_fee(distance_km: float, item_total: Decimal = Decimal("100.0")) -> Decimal:
    if item_total > 0:
        if distance_km is None or distance_km <= 2.5:
            delivery_fee = Decimal("40.0")  # ₹40 base fee for up to 2.5 km
        else:
            # ₹40 base + ₹7 per extra km above 2.5 km, capped at MAX_DELIVERY_FEE (₹150.0)
            MAX_DELIVERY_FEE = Decimal("150.0")
            extra_km = distance_km - 2.5
            calculated_fee = Decimal("40.0") + Decimal(str(round(extra_km * 7.0, 2)))
            delivery_fee = min(calculated_fee, MAX_DELIVERY_FEE)
    else:
        delivery_fee = Decimal("0.0")
    return delivery_fee

def test_delivery_fee():
    cases = [
        (1.0, Decimal("40.0")),
        (2.5, Decimal("40.0")),
        (3.5, Decimal("47.0")),   # 40 + (1.0 * 7) = 47.0
        (5.5, Decimal("61.0")),   # 40 + (3.0 * 7) = 61.0
        (None, Decimal("40.0")),
    ]
    
    print("=== Testing Delivery Fee Calculation ===")
    for dist, expected in cases:
        actual = calculate_delivery_fee(dist)
        status = "PASSED" if actual == expected else f"FAILED (expected {expected})"
        dist_str = f"{dist} km" if dist is not None else "None (Fallback)"
        print(f"Distance: {dist_str:<15} | Fee: ₹{actual} | {status}")

if __name__ == "__main__":
    test_delivery_fee()
