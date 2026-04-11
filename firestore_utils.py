import firebase_admin
from firebase_admin import credentials, firestore
import os

FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH', 'firebase_service_account.json')

firestore_db = None

def initialize_firestore():
    global firestore_db
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CRED_PATH)
        firebase_admin.initialize_app(cred)
    firestore_db = firestore.client()

# Call this at app startup
initialize_firestore()

def save_user_itinerary(uid, itinerary_data):
    """
    Store itinerary data for a user in Firestore.
    """
    doc_ref = firestore_db.collection('user_itineraries').document(uid)
    doc_ref.set({'itinerary': itinerary_data}, merge=True)


def get_user_itinerary(uid):
    """
    Retrieve itinerary data for a user from Firestore.
    """
    doc_ref = firestore_db.collection('user_itineraries').document(uid)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict().get('itinerary', None)
    return None
