
import os
import sys
# Add current directory to path
sys.path.append(os.getcwd())

from app.services.firebase_service import FirebaseService

def verify_firebase():
    print("Testing Firebase initialization...")
    result = FirebaseService.initialize()
    if result:
        print("\n✅ SUCCESS: Firebase Admin SDK initialized correctly!")
    else:
        print("\n❌ FAILED: Firebase initialization failed. Check logs.")

if __name__ == "__main__":
    verify_firebase()
