import os
import firebase_admin
from firebase_admin import credentials

def init_firebase():
    try:
        # Dynamically find the file path relative to this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cred_path = os.path.join(current_dir, "..", "serviceAccountKey.json")
        
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Firebase key missing at: {cred_path}")
            
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully")
        
    except Exception as error:
        print(f"Firebase initialization error: {error}")