#!/usr/bin/env python
"""
ATIG App Diagnostic Script
Tests if the Flask app can start and routes are registered
"""

import os
import sys

atig_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, atig_path)

print("="*60)
print("ATIG APPLICATION INITIALIZATION TEST")
print("="*60)

# Test 1: Check if app module exists
print("\n✓ Test 1: Checking app module...")
try:
    from app import create_app
    print("  ✓ App factory imported successfully")
except Exception as e:
    print(f"  ✗ Error importing app: {e}")
    sys.exit(1)

# Test 2: Check if Flask can create app
print("\n✓ Test 2: Creating Flask app...")
try:
    app = create_app('development')
    print("  ✓ App created successfully")
except Exception as e:
    print(f"  ✗ Error creating app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check registered routes
print("\n✓ Test 3: Checking registered routes...")
routes = {}
for rule in app.url_map.iter_rules():
    if rule.endpoint != 'static':
        routes[rule.rule] = rule.methods
        print(f"  ✓ {rule.rule} → {rule.endpoint} {rule.methods}")

# Test 4: Check if templates exist
print("\n✓ Test 4: Checking templates...")
template_path = os.path.join(atig_path, 'app', 'templates')
if os.path.exists(template_path):
    templates = os.listdir(template_path)
    print(f"  ✓ Template folder exists: {template_path}")
    print(f"  ✓ Templates found: {len(templates)}")
    for t in templates:
        print(f"    - {t}")
else:
    print(f"  ✗ Template folder not found: {template_path}")

# Test 5: Check if data exists
print("\n✓ Test 5: Checking data files...")
data_path = os.path.join(atig_path, 'data')
if os.path.exists(data_path):
    files = os.listdir(data_path)
    print(f"  ✓ Data folder exists: {data_path}")
    for f in files:
        print(f"    - {f}")
else:
    print(f"  ✗ Data folder not found: {data_path}")

# Test 6: Check if attractions data exists
print("\n✓ Test 6: Checking attractions data...")
attractions_file = os.path.join(data_path, 'jaipur_attractions.json')
if os.path.exists(attractions_file):
    import json
    try:
        with open(attractions_file, 'r') as f:
            data = json.load(f)
        print(f"  ✓ Attractions file loaded")
        print(f"  ✓ Total attractions: {len(data.get('attractions', []))}")
    except Exception as e:
        print(f"  ✗ Error loading attractions: {e}")
else:
    print(f"  ✗ Attractions file not found: {attractions_file}")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
print("\nTo start the app, run:")
print("  python start.py")
