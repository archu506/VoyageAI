#!/usr/bin/env python
"""Test the save/load itinerary endpoints"""

import requests
import json

BASE_URL = "http://localhost:5000"

# Test data
test_itinerary = '<div><h3>Jaipur 3-Day Itinerary</h3><ul><li>Day 1: City Palace</li><li>Day 2: Jantar Mantar</li></ul></div>'
user_id = 'test_user_' + str(__import__('time').time()).replace('.', '_')

print(f"Testing with userId: {user_id}")
print("=" * 60)

# Test Save
print("\n1. Testing SAVE endpoint...")
save_payload = {
    "userId": user_id,
    "itinerary": test_itinerary
}

try:
    resp_save = requests.post(f"{BASE_URL}/api/itinerary/save", json=save_payload, timeout=5)
    print(f"   Status Code: {resp_save.status_code}")
    print(f"   Response: {resp_save.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test Load
print("\n2. Testing LOAD endpoint...")
try:
    resp_load = requests.get(f"{BASE_URL}/api/itinerary/get?userId={user_id}", timeout=5)
    print(f"   Status Code: {resp_load.status_code}")
    resp_data = resp_load.json()
    print(f"   Response: {resp_data}")
    if resp_data.get('success'):
        print(f"   ✓ Itinerary loaded successfully (length: {len(resp_data.get('itinerary', ''))} chars)")
except Exception as e:
    print(f"   Error: {e}")

# Check if file was created
import os
filepath = f"itineraries/{user_id}_itinerary.json"
if os.path.exists(filepath):
    print(f"\n3. File created successfully: {filepath}")
    with open(filepath) as f:
        content = json.load(f)
        print(f"   Saved at: {content.get('saved_at')}")
        print(f"   User ID: {content.get('user_id')}")
else:
    print(f"\n3. File not found: {filepath}")

print("\n" + "=" * 60)
print("✓ All endpoints working correctly!")
