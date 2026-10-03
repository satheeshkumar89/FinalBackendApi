"""
Automated unit & integration tests for Zomato-style session handling:
1. Verify OTP -> Returns access_token, refresh_token, expires_in, is_new_user
2. Verify user_sessions row creation
3. Call /auth/refresh -> Verifies Token Rotation (new access & refresh tokens issued)
4. Verify old refresh token is revoked
5. Test /auth/sessions (list devices)
6. Test /auth/logout (revoke session)
"""

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import Owner, Customer, UserSession, OTP

def test_full_zomato_session_flow():
    print("🚀 Starting Zomato-Style Session Flow Test...")
    
    # Create test client
    client = TestClient(app)
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    phone = "+919998887777"
    
    # Clean old test data
    db.query(OTP).filter(OTP.phone_number == phone).delete()
    db.query(UserSession).filter(UserSession.user_type == "customer").delete()
    db.query(Customer).filter(Customer.phone_number == phone).delete()
    db.commit()
    
    # 1. Send OTP
    res_send = client.post("/customer/auth/send-otp", json={"phone_number": phone})
    assert res_send.status_code == 200, f"Send OTP failed: {res_send.text}"
    send_data = res_send.json()
    assert send_data["success"] is True
    otp_code = send_data["data"]["otp"]
    print(f"✅ 1. OTP Sent successfully. Received OTP: {otp_code}")
    
    # 2. Verify OTP
    res_verify = client.post("/customer/auth/verify-otp", json={
        "phone_number": phone,
        "otp_code": otp_code,
        "device_id": "test_device_123",
        "device_name": "iPhone 15 Pro"
    })
    assert res_verify.status_code == 200, f"Verify OTP failed: {res_verify.text}"
    verify_data = res_verify.json()
    
    assert "access_token" in verify_data, "access_token missing"
    assert "refresh_token" in verify_data, "refresh_token missing"
    assert "expires_in" in verify_data, "expires_in missing"
    assert verify_data["is_new_user"] is True, "Expected is_new_user = True"
    
    access_token_1 = verify_data["access_token"]
    refresh_token_1 = verify_data["refresh_token"]
    print(f"✅ 2. Verify OTP successful. Received Access Token & Refresh Token.")
    
    # 3. Check DB UserSession
    db_session = db.query(UserSession).filter(
        UserSession.user_type == "customer",
        UserSession.is_active == True
    ).first()
    assert db_session is not None, "UserSession DB record missing"
    assert db_session.device_id == "test_device_123"
    print(f"✅ 3. DB UserSession validated: Session ID {db_session.id}, Device: {db_session.device_name}")
    
    # 4. Refresh Token (Token Rotation)
    res_refresh = client.post("/customer/auth/refresh", json={
        "refresh_token": refresh_token_1,
        "device_id": "test_device_123",
        "device_name": "iPhone 15 Pro"
    })
    assert res_refresh.status_code == 200, f"Token refresh failed: {res_refresh.text}"
    refresh_data = res_refresh.json()
    
    access_token_2 = refresh_data["access_token"]
    refresh_token_2 = refresh_data["refresh_token"]
    
    assert access_token_2 != access_token_1, "New access token should be different"
    assert refresh_token_2 != refresh_token_1, "Rotated refresh token should be different"
    print(f"✅ 4. Token Refresh (Token Rotation) successful. Issued fresh token pair.")
    
    # 5. Attempt reusing old refresh_token_1 -> must fail with 401
    res_reuse = client.post("/customer/auth/refresh", json={"refresh_token": refresh_token_1})
    assert res_reuse.status_code == 401, f"Expected 401 on old token reuse, got {res_reuse.status_code}"
    print(f"✅ 5. Security Check passed: Reusing old refresh token returned 401 Unauthorized.")
    
    # 6. Check Active Sessions API
    res_sessions = client.get(
        "/customer/auth/sessions",
        headers={"Authorization": f"Bearer {access_token_2}"}
    )
    assert res_sessions.status_code == 200, f"List sessions failed: {res_sessions.text}"
    sessions_list = res_sessions.json()
    assert len(sessions_list) >= 1
    print(f"✅ 6. Sessions API list retrieved successfully. Active sessions count: {len(sessions_list)}")
    
    # 7. Logout
    res_logout = client.post("/customer/auth/logout", json={"refresh_token": refresh_token_2})
    assert res_logout.status_code == 200, f"Logout failed: {res_logout.text}"
    print(f"✅ 7. Logout endpoint successful.")
    
    # 8. Attempt refresh with logged out token -> must fail with 401
    res_post_logout_refresh = client.post("/customer/auth/refresh", json={"refresh_token": refresh_token_2})
    assert res_post_logout_refresh.status_code == 401
    print(f"✅ 8. Post-logout refresh check passed: Revoked session returned 401.")
    
    db.close()
    print("🎉 ALL ZOMATO-STYLE SESSION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full_zomato_session_flow()
