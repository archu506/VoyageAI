# Real-Time Adaptive Travel Brain 🌍✈️

A smart travel planner for Jaipur that dynamically adapts itineraries based on real-time environmental factors.

## Features ✨

- **Weather Adaptation**: Automatically reorders indoor/outdoor activities based on rain forecasts
- **Crowd Intelligence**: Suggests alternatives when popular attractions are crowded
- **Air Quality Awareness**: Prioritizes indoor activities when AQI levels are high
- **Energy Management**: Calculates user energy levels and suggests appropriate activity counts
- **Smart Recommendations**: Provides contextual suggestions based on combined factors
- **Visual Timeline**: Displays detailed itinerary with time slots

## Tech Stack 🛠️

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Data**: JSON (mock data)
- **Architecture**: Modular, clean service-based design

## Project Structure

```
adaptive_travel/
├── app.py                           # Main Flask application
├── attractions.json                 # Jaipur attractions database
├── requirements.txt                 # Python dependencies
├── services/
│   ├── __init__.py
│   └── adaptation_engine.py        # Core adaptation logic
├── templates/
│   ├── base.html                   # Base template
│   └── index.html                  # Main interface
└── static/
    └── css/
        └── style.css               # Styling
```

## Installation & Setup 🚀

### 1. Navigate to the project directory
```bash
cd adaptive_travel
```

### 2. Create a virtual environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

### 5. Open in browser
Navigate to: `http://localhost:5000`

## How to Use 📋

1. **Select Attractions**: Choose attractions from the list that you'd like to visit
2. **Set Conditions**: 
   - Select weather (Clear ☀️ or Raining 🌧️)
   - Choose expected crowd level (Low/Medium/High)
   - Adjust Air Quality Index using the slider
3. **Click "Generate Adapted Plan"**: System analyzes and adapts your itinerary
4. **Review Results**:
   - View energy level impact
   - Read smart recommendations
   - Compare original vs. adapted plan
   - See detailed timeline with time slots

## Key Adaptations 🔄

### Weather Impact
- **Rain Detected**: Moves indoor activities to morning, outdoor activities to late afternoon/evening

### Crowd Impact
- **High Crowds**: Suggests quieter alternatives like Nahargarh Fort or Sisodia Rani Garden

### Air Quality Impact
- **High AQI (>200)**: Prioritizes indoor attractions (museum, gallery, temple)

### Energy Impact
- **Energy < 50**: Reduces schedule to top 2 attractions
- **Energy 50-70**: Suggests lighter schedule with rest breaks

## Attractions Database 🏛️

The system includes 10 major Jaipur attractions:

1. **City Palace** - Outdoor, 120 min
2. **Jantar Mantar** - Outdoor, 90 min
3. **Hawa Mahal** - Outdoor, 60 min
4. **Albert Hall Museum** - Indoor, 120 min
5. **Govind Dev Ji Temple** - Outdoor, 60 min
6. **Sisodia Rani Garden** - Outdoor, 90 min
7. **Chaugan Stadium** - Outdoor, 60 min
8. **City Palace Art Gallery** - Indoor, 90 min
9. **Johari Bazaar** - Outdoor, 120 min
10. **Nahargarh Fort** - Outdoor, 150 min

## API Endpoints 🔌

### POST `/api/adapt`
Generates an adapted travel plan.

**Request Body:**
```json
{
  "selected_attractions": [1, 3, 4],
  "weather_raining": false,
  "crowd_level": "high",
  "aqi_level": 180
}
```

**Response:**
```json
{
  "original_plan": [...],
  "adapted_plan": [...],
  "changes": [...],
  "energy_score": 70,
  "recommendations": [...],
  "timeline": [...],
  "schedule_modified": true
}
```

### GET `/api/attractions`
Returns all available attractions.

## Energy Score Calculation ⚡

```
Energy Score = 100 - (Sum of activity energy costs)

Each activity has an energy cost:
- Light activities (temples, bazaars): 15-20
- Medium activities (museums, gardens): 20-25
- Heavy activities (forts, palace): 30-35

Score Levels:
- 80-100: Full energy, can add more activities
- 50-79: Moderate energy, balanced schedule recommended
- <50: Low energy, reduce schedule to 1-2 activities
```

## Adaptation Logic 🧠

The system applies adaptations in order:

1. Check AQI → Prioritize indoor if high
2. Check Weather → Reorder for rain protection
3. Check Crowds → Suggest alternatives
4. Check Energy → Reduce activities if low

Multiple factors are combined for intelligent suggestions.

## Customization 🎨

### Add More Attractions
Edit `attractions.json` and add new entries with:
- `id`: Unique identifier
- `name`: Attraction name
- `type`: "indoor" or "outdoor"
- `duration`: Time in minutes
- `energy_cost`: Energy points (1-35)
- `description`: Brief description

### Adjust Thresholds
In `services/adaptation_engine.py`:
- Modify AQI classification limits
- Change energy thresholds
- Adjust reordering logic

## Screenshots 📸

The interface includes:
- Clean attraction selection interface
- Real-time condition adjustments
- Side-by-side original vs adapted plan comparison
- Visual energy level indicator
- Color-coded recommendations
- Detailed timeline view

## Notes 📝

- This is an MVP without external APIs
- All data is mocked for demonstration
- No ML/AI libraries used - pure logic
- Fully runnable locally with minimal dependencies
- Responsive design works on desktop and mobile

## Future Enhancements 🔮

- Real weather API integration (OpenWeatherMap)
- Real crowd data from Google/Apple Maps
- Real AQI data from AirVisual API
- User profiles for personalized energy scoring
- Route optimization between attractions
- Database integration for persistence
- User authentication
- Multi-city support

## License 📄

MIT License - Feel free to use and modify!

---

**Built with ❤️ for smart travel planning**
