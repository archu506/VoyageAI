# Weather Integration Guide

## Overview

The Real-Time Adaptive Travel Brain now uses **live weather data** from OpenWeatherMap API instead of manual toggles. This provides real-time, accurate weather conditions for Jaipur that automatically affect itinerary planning.

## Features

✅ **Live Weather Data**
- Fetches current temperature for Jaipur
- Gets real weather conditions (Clear, Rainy, Cloudy, etc.)
- Updates humidity information
- Automatically determines if it's raining

✅ **Smart Fallback**
- If API is unavailable, system uses realistic mock data
- Never breaks the app
- Gracefully degrades with fallback mode indicator

✅ **Secure API Key Handling**
- API key stored in environment variables (.env file)
- Never exposed in code
- Can be easily rotated

✅ **Fast & Efficient**
- 5-second timeout to prevent hanging
- Lightweight JSON parsing
- Minimal overhead

## Setup Instructions

### Step 1: Get a Free OpenWeatherMap API Key

1. Visit [OpenWeatherMap API](https://openweathermap.org/api)
2. Click "Sign Up" or "Log In"
3. Create a free account
4. Go to your API Keys page
5. Copy your API key (looks like a long string of characters)

### Step 2: Set API Key in .env File

1. Open the `.env` file in the `adaptive_travel` directory
2. Replace `your_openweathermap_api_key_here` with your actual API key
3. Save the file

```
# Before
WEATHER_API_KEY=your_openweathermap_api_key_here

# After (example)
WEATHER_API_KEY=abc123def456ghi789jkl012mno345pqr
```

### Step 3: Install Dependencies

If you haven't already, install the required packages:

```bash
pip install -r requirements.txt
```

This installs:
- `Flask==2.3.2` - Web framework
- `Werkzeug==2.3.6` - WSGI utilities
- `requests==2.31.0` - HTTP library (for API calls)
- `python-dotenv==1.0.0` - Environment variable loader

### Step 4: Run the App

```bash
python app.py
```

Navigate to `http://localhost:5000` and you should see live weather displaying!

## How It Works

### Data Flow

```
User loads app
    ↓
JavaScript calls /api/weather
    ↓
Weather Service checks for API key
    ├── If available: Calls OpenWeatherMap API
    │   ├── Fetch Jaipur weather
    │   ├── Parse temperature, condition, humidity
    │   ├── Determine is_raining (from weather condition)
    │   └── Return {temp, condition, is_raining, humidity, source:"openweathermap"}
    │
    └── If unavailable: Return mock data
        └── Return {temp, condition, is_raining, humidity, source:"fallback"}
    ↓
UI displays weather (temp, condition, humidity, rain status)
    ↓
User selects attractions and clicks "Generate Plan"
    ↓
JavaScript sends request to /api/adapt (WITHOUT weather_raining toggle)
    ↓
Flask calls fetch_weather() server-side
    ↓
Weather data passed to AdaptationEngine
    ↓
Engine scores attractions based on LIVE weather
    ↓
Adapted plan returned with real weather impact
```

### API Endpoints Added

#### GET `/api/weather`
Returns current weather for Jaipur.

**Response:**
```json
{
  "temperature": 28.5,
  "condition": "Clear sky",
  "is_raining": false,
  "humidity": 60,
  "source": "openweathermap"
}
```

**Source Values:**
- `"openweathermap"` - Live data from API
- `"fallback"` - Mock data (API unavailable)

#### POST `/api/adapt`
Updated to fetch weather server-side instead of client-side.

**Request (No longer needs weather_raining):**
```json
{
  "selected_attractions": [1, 3, 5],
  "crowd_level": "high",
  "aqi_level": 180
}
```

**Response includes new weather field:**
```json
{
  "weather": {
    "temperature": 28.5,
    "condition": "Clear sky",
    "is_raining": false,
    "humidity": 60,
    "source": "openweathermap"
  },
  "original_plan": [...],
  "adapted_plan": [...],
  ...
}
```

## API Key Security

### Best Practices

✅ **DO:**
- Keep API key in `.env` file
- Add `.env` to `.gitignore` (don't commit secrets)
- Use environment variables
- Rotate keys regularly
- Use free tier initially

❌ **DON'T:**
- Hardcode API key in Python files
- Commit `.env` to git
- Share API key publicly
- Use production key for testing

### Environment Variables

The `.env` file is loaded automatically by `python-dotenv`:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file
api_key = os.getenv('WEATHER_API_KEY')
```

## Fallback Behavior

If the API fails for any reason:

```python
# API unavailable scenarios
├── No API key set → Uses mock data
├── Network error → Uses mock data
├── API rate limit → Uses mock data
├── Invalid API key → Uses mock data
└── Timeout (5 sec) → Uses mock data
```

The system **never crashes**. It gracefully uses realistic mock data and shows the user a fallback indicator.

### Mock Data Patterns

Mock data varies by time of day:
- **6 AM - 12 PM**: Sunny, 32°C
- **12 PM - 5 PM**: Hot & Humid, 35°C
- **5 PM - 8 PM**: Partly Cloudy, 28°C
- **8 PM - 6 AM**: Cool Night, 24°C

This creates realistic variation even in fallback mode.

## User Interface

### Weather Display (When Loading)
```
🌤️ Live Weather for Jaipur
┌─────────────────────────────┐
│ Loading live weather...     │
└─────────────────────────────┘
```

### Weather Display (Live Data)
```
🌤️ Live Weather for Jaipur
┌─────────────────────────────┐
│ ☀️ 28.5°C                  │
│                             │
│ Clear sky                   │
│ 💧 Humidity: 60%            │
│ ☀️ No Rain                 │
└─────────────────────────────┘
✓ Data Source: Live Data
```

### Weather Display (Fallback)
```
🌤️ Live Weather for Jaipur
┌─────────────────────────────┐
│ ⚠️                          │
│ Unable to fetch live weather │
│ Using standard forecast mode │
└─────────────────────────────┘
```

## Real-World Examples

### Scenario 1: Rainy Day

**Live Weather:**
- Temperature: 24°C
- Condition: Light Rain
- Is Raining: true

**Effect on Planning:**
- All outdoor attractions penalized -30
- Museums and galleries moved to front
- Indoor attractions prioritized
- Rain-sensitive outdoor places doubly penalized

### Scenario 2: Hot & Humid Day

**Live Weather:**
- Temperature: 38°C
- Condition: Partly Cloudy
- Is Raining: false

**Effect on Planning:**
- All attractions ranked normally (no rain penalty)
- Outdoor activities still viable
- Humidity shown for reference
- User can adjust AQI slider based on heat

### Scenario 3: API Unavailable

**Fallback Weather:**
- Temperature: 28.0°C (mock)
- Condition: Partly Cloudy
- Is Raining: false
- Source: fallback

**Effect on Planning:**
- No rain penalty applied
- Standard itinerary planning
- User notified of forecast mode
- Still funcional, just not live

## Monitoring & Debugging

### Check API Key Setup

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('WEATHER_API_KEY')

if api_key:
    print(f"✓ API key loaded: {api_key[:10]}...")
else:
    print("✗ No API key found in .env")
```

### Test Weather Service Directly

```python
from services.weather_service import fetch_weather

weather = fetch_weather()
print(f"Temperature: {weather['temperature']}°C")
print(f"Condition: {weather['condition']}")
print(f"Is Raining: {weather['is_raining']}")
print(f"Source: {weather['source']}")
```

### Check API Call in Browser

Open browser console and run:

```javascript
fetch('/api/weather')
    .then(r => r.json())
    .then(data => console.log(data))
```

## Troubleshooting

### Problem: "Unable to fetch live weather"

**Solution 1: Check .env file**
```bash
# Make sure .env exists and has API key
cat .env  # or more .env on Windows
```

**Solution 2: Verify API key**
- Visit https://openweathermap.org
- Log in and check if API key is active
- Copy exact key (no extra spaces)

**Solution 3: Check network**
```bash
# Test OpenWeatherMap API directly
curl "https://api.openweathermap.org/data/2.5/weather?q=Jaipur,IN&appid=YOUR_KEY"
```

### Problem: Always showing "Forecast Mode"

**Solution: API key not loaded**
1. Restart Flask app
2. Kill any Python processes
3. Make sure .env has correct key
4. Check for typos in API key

### Problem: Weather doesn't update in results

**Solution: Check result includes weather field**
```javascript
// In browser console during plan generation
fetch('/api/adapt', {...})
    .then(r => r.json())
    .then(data => console.log(data.weather))
```

## Performance

- **API Call Time**: 500ms - 2000ms (depends on network)
- **Timeout**: 5 seconds (won't hang)
- **Fallback Time**: < 10ms (instant)
- **Caching**: None (always fresh, fetched once per page load + per plan generation)

## Future Enhancements

1. **Weather Caching**
   - Cache weather for 10 minutes
   - Reduce API calls
   - Still get updates

2. **Weather Forecasting**
   - Show 5-day forecast
   - Plan multi-day trips
   - Suggest best days

3. **Weather Alerts**
   - Warn about severe weather
   - Suggest indoor activities
   - Update in real-time

4. **More Weather Data**
   - Wind speed
   - UV index
   - Precipitation amount
   - Air pressure

## References

- [OpenWeatherMap API Docs](https://openweathermap.org/api)
- [API Keys Page](https://openweathermap.org/api/find)
- [Free API Tier](https://openweathermap.org/api/find#weather)

---

**Integration Date**: February 26, 2026
**Status**: ✅ Production Ready
**API Library**: requests 2.31.0
**Environment**: .env with python-dotenv
