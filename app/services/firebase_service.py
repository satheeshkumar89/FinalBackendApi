import firebase_admin
from firebase_admin import credentials, auth
import os
from app.config import get_settings

settings = get_settings()


class FirebaseService:
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK"""
        if cls._initialized:
            return True
            
        # Check if already initialized by another service or previously
        try:
            firebase_admin.get_app()
            cls._initialized = True
            return True
        except ValueError:
            # App not initialized yet, proceed
            pass

        try:
            # List of possible locations for the service account key
            possible_paths = [
                os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY"),
                "firebase-service-account.json",
                "/app/firebase-service-account.json",
                os.path.join(os.getcwd(), "firebase-service-account.json"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "firebase-service-account.json")
            ]
            
            cred_path = None
            for path in possible_paths:
                if path and os.path.exists(path):
                    cred_path = path
                    break
            
            if cred_path:
                abs_path = os.path.abspath(cred_path)
                cred = credentials.Certificate(abs_path)
                firebase_admin.initialize_app(cred)
                cls._initialized = True
                print(f"✅ Firebase Admin SDK initialized successfully using {abs_path}")
                return True
            else:
                print(f"⚠ Firebase service account key not found. Checked: {possible_paths}")
                print("  Firebase services will be simulated in development mode")
                return False
        except Exception as e:
            if "The default Firebase app already exists" in str(e):
                cls._initialized = True
                return True
            print(f"⚠ Firebase initialization failed: {e}")
            return False
    
    @staticmethod
    def send_otp_via_firebase(phone_number: str) -> dict:
        """
        Send OTP via Firebase Authentication
        Returns session info for verification
        """
        try:
            # In a real implementation, Firebase handles OTP on the client side
            # The backend just verifies the token
            # This is a placeholder for the flow
            
            if not FirebaseService._initialized:
                # Development mode - simulate OTP
                import random
                otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                print(f"\n{'='*50}")
                print(f"📱 DEVELOPMENT MODE - OTP for {phone_number}: {otp}")
                print(f"{'='*50}\n")
                return {
                    "success": True,
                    "mode": "development",
                    "otp": otp,  # Only in development
                    "message": "OTP sent (development mode)"
                }
            
            # Production mode with Firebase
            # Note: Firebase Auth typically handles OTP on client side
            # Backend receives the ID token for verification
            return {
                "success": True,
                "mode": "production",
                "message": "OTP sent via Firebase"
            }
            
        except Exception as e:
            print(f"Error sending Firebase OTP: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def verify_firebase_token(id_token: str) -> dict:
        """
        Verify Firebase ID token
        Returns decoded token with user info
        """
        try:
            if not FirebaseService._initialized:
                # Development mode - skip verification
                return {
                    "success": True,
                    "mode": "development",
                    "uid": "dev_user_123",
                    "phone_number": "+1234567890"
                }
            
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            return {
                "success": True,
                "mode": "production",
                "uid": decoded_token.get('uid'),
                "phone_number": decoded_token.get('phone_number'),
                "email": decoded_token.get('email')
            }
            
        except Exception as e:
            print(f"Error verifying Firebase token: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Initialize Firebase on module import
FirebaseService.initialize()
