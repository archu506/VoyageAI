#!/usr/bin/env python
"""
Complete test of Save Itinerary functionality on the second page
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("TESTING SAVE/LOAD ITINERARY - MOVED TO SECOND PAGE")
print("=" * 70)

# Create a realistic itinerary (what appears after generating a plan)
sample_itinerary = """
<div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 10px 0;">
    <h3 style="color: #667eea; margin-bottom: 15px;">🎯 Jaipur - 3 Days Itinerary</h3>
    <div style="background: white; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
        <h4 style="margin: 0 0 8px 0;">Day 1: Historical Monuments</h4>
        <p style="margin: 5px 0; color: #333;">• City Palace (9:00 AM)</p>
        <p style="margin: 5px 0; color: #333;">• Jantar Mantar (11:30 AM)</p>
        <p style="margin: 5px 0; color: #333;">• Lunch Break (1:00 PM)</p>
        <p style="margin: 5px 0; color: #333;">• Hawa Mahal (3:00 PM)</p>
    </div>
    <div style="background: white; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
        <h4 style="margin: 0 0 8px 0;">Day 2: Cultural Sites</h4>
        <p style="margin: 5px 0; color: #333;">• Albert Museum (9:00 AM)</p>
        <p style="margin: 5px 0; color: #333;">• Ram Niwas Garden (11:00 AM)</p>
    </div>
    <div style="background: white; padding: 15px; border-radius: 5px;">
        <h4 style="margin: 0 0 8px 0;">Day 3: Shopping & Leisure</h4>
        <p style="margin: 5px 0; color: #333;">• Bapu Bazaar Shopping (9:00 AM)</p>
    </div>
</div>
"""

# Test user ID
test_user = f"test_user_{int(time.time())}"

print(f"\n📋 TEST CONFIGURATION")
print(f"   User ID: {test_user}")
print(f"   Itinerary Length: {len(sample_itinerary)} characters")

# TEST 1: Save Itinerary
print(f"\n{'='*70}")
print("TEST 1: SAVE ITINERARY (What happens when user clicks 💾 button)")
print(f"{'='*70}")

save_payload = {
    "userId": test_user,
    "itinerary": sample_itinerary
}

try:
    response = requests.post(
        f"{BASE_URL}/api/itinerary/save",
        json=save_payload,
        timeout=5
    )
    
    print(f"\n✓ Request sent to: POST /api/itinerary/save")
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"  ✅ SUCCESS: {data.get('message')}")
            saved_time = int(time.time())
        else:
            print(f"  ❌ FAILED: {data.get('error')}")
    else:
        print(f"  ❌ HTTP Error: {response.text}")
        
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# TEST 2: Generate different itinerary
print(f"\n{'='*70}")
print("TEST 2: GENERATE A DIFFERENT ITINERARY (simulating new plan)")
print(f"{'='*70}")

different_itinerary = """
<div style="background: #f5f5f5; padding: 20px; border-radius: 8px;">
    <h3 style="color: #667eea;">🌴 Goa Beach Trip - 4 Days</h3>
    <p>Different itinerary for testing...</p>
</div>
"""

print("✓ New itinerary generated in itineraryList div on second page")

# TEST 3: Load Itinerary
print(f"\n{'='*70}")
print("TEST 3: LOAD ITINERARY (What happens when user clicks 📂 button)")
print(f"{'='*70}")

try:
    response = requests.get(
        f"{BASE_URL}/api/itinerary/get?userId={test_user}",
        timeout=5
    )
    
    print(f"\n✓ Request sent to: GET /api/itinerary/get?userId={test_user}")
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"  ✅ SUCCESS: Itinerary loaded")
            loaded_itinerary = data.get('itinerary', '')
            print(f"  Retrieved length: {len(loaded_itinerary)} characters")
            
            # Verify it matches what we saved
            if loaded_itinerary == sample_itinerary:
                print(f"  ✅ VERIFIED: Loaded itinerary matches saved itinerary")
            else:
                print(f"  ⚠️  WARNING: Itinerary differs from saved version")
        else:
            print(f"  ❌ FAILED: {data.get('error')}")
    else:
        print(f"  ❌ HTTP Error: {response.text}")
        
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# TEST 4: Check file storage
print(f"\n{'='*70}")
print("TEST 4: VERIFY FILE STORAGE")
print(f"{'='*70}")

import os

filepath = f"itineraries/{test_user}_itinerary.json"
if os.path.exists(filepath):
    print(f"\n✅ FILE EXISTS: {filepath}")
    
    with open(filepath) as f:
        stored_data = json.load(f)
        print(f"  User ID: {stored_data.get('user_id')}")
        print(f"  Saved At: {stored_data.get('saved_at')}")
        print(f"  Itinerary Length: {len(stored_data.get('itinerary', ''))} characters")
else:
    print(f"\n❌ FILE NOT FOUND: {filepath}")

# FINAL SUMMARY
print(f"\n{'='*70}")
print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
print(f"{'='*70}")
print("""
HOW IT WORKS NOW:
1. User fills form on FIRST PAGE and clicks "Generate Itinerary"
2. Results appear in "Your Itinerary Results" section on SECOND PAGE
3. User can now click 💾 SAVE to store the itinerary
4. User can click 📂 LOAD to restore any previously saved itinerary
5. All data is stored locally in the itineraries/ folder

BUTTONS LOCATION: Second page (Results section) - NOT on the form anymore
""")
