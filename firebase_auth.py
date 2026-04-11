import firebase_admin
from firebase_admin import credentials, auth

import os

# Path to your Firebase service account key JSON file
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH', 'firebase_service_account.json')

firebase_app = None

def initialize_firebase():
    global firebase_app
    if not firebase_app:
        cred = credentials.Certificate(FIREBASE_CRED_PATH)
        firebase_app = firebase_admin.initialize_app(cred)

# Call this at app startup
initialize_firebase()

def verify_id_token(id_token):
    """
    Verifies the Firebase ID token sent from the client.
    Returns the decoded token if valid, else raises an exception.
    """
    return auth.verify_id_token(id_token)

# Example usage in Flask:
# from flask import request, jsonify
# @app.route('/api/auth/firebase-login', methods=['POST'])
# def firebase_login():
#     id_token = request.json.get('idToken')
#     try:
#         decoded_token = verify_id_token(id_token)
#         uid = decoded_token['uid']
#         # You can now use uid to identify the user in your backend
#         return jsonify({'success': True, 'uid': uid})
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 401
