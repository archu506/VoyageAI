import requests
try:
    resp = requests.post("http://127.0.0.1:5000/plan", data={"city": "Jaipur", "days": "3", "crowd_level": "50", "energy": "100"}, timeout=5)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 500:
        print("Crash detected!")
    elif "Jaipur" in resp.text:
        print("Successfully generated itinerary!")
    else:
        print("Page loaded but missing expected text.")
except Exception as e:
    print(f"Failed: {e}")
