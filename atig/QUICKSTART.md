# ATIG - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Install Python Dependencies
```bash
cd c:\Users\SK\OneDrive\Desktop\smart_tourism\atig

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

**Expected time**: 3-5 minutes  
*(Prophet library is large, ~ 200MB)*

### Step 2: Generate Mock Data
```bash
cd data
python generate_footfall.py
cd ..
```

**Output**:
```
Generated 21600 footfall records
Saved to data/footfall_history.json
```

### Step 3: Run Application
```bash
python run.py
```

**Success Output**:
```
╔══════════════════════════════════════════════════════════════╗
║  ATIG - Adaptive Tourism Intelligence Grid (MVP)            ║
║  Jaipur Smart Tourism System                                ║
║                                                              ║
║  🌍 Running on: http://localhost:5000                       ║
║  📊 Dashboard: http://localhost:5000/dashboard              ║
║  📍 API: http://localhost:5000/api                          ║
╚══════════════════════════════════════════════════════════════╝
```

### Step 4: Open in Browser
- **Home**: http://localhost:5000
- **Plan Itinerary**: http://localhost:5000/plan
- **Dashboard**: http://localhost:5000/dashboard
- **Attractions List**: http://localhost:5000/attractions

---

## 🧪 Test the System

### Test 1: View All Attractions
1. Click "Attractions" in menu
2. See all 10 Jaipur attractions with details
3. Click "Add to Plan" button

### Test 2: Plan Smart Itinerary
1. Go to "Plan Trip" page
2. Select 3 attractions:
   - ✓ Hawa Mahal
   - ✓ City Palace
   - ✓ Albert Hall Museum
3. Set time budget: 8 hours
4. Choose transport: Auto-rickshaw
5. Click "Optimize Itinerary"
6. **Result**: See optimized route, sustainability score, map

### Test 3: Check Crowd Forecast
1. Go to "Government Dashboard"
2. View heatmap (red = crowded, green = quiet)
3. See 24-hour forecast
4. Check heritage alerts

### Test 4: API Testing
```bash
# Get attractions
curl http://localhost:5000/api/attractions

# Get crowd forecast
curl http://localhost:5000/api/crowd-forecast

# Optimize route
curl -X POST http://localhost:5000/api/optimize-itinerary ^
  -H "Content-Type: application/json" ^
  -d "{\"attractions\":[\"A001\",\"A003\"],\"time_budget_hours\":8,\"transport_mode\":\"auto\"}"
```

---

## 📊 What to Expect

### Sustainability Score Breakdown
- **Carbon Score** (30%): CO₂ emissions from travel
- **Crowd Impact** (40%): Environmental strain from overcrowding
- **Heritage Score** (20%): Preservation value of sites visited
- **Time Efficiency** (10%): Balanced pace without rushing

### Typical Results
- **Good Itinerary**: 70-80/100 score
- **Excellent Itinerary**: 80+/100 score
- **Recommendations**: Be offered 2-4 personalized suggestions

---

## 🛠️ Configuration

### Change Port
```bash
set FLASK_ENV=development
set PORT=5001
python run.py
```

### Use Different Transport Mode
When optimizing, select from:
- **Auto** (0.12 kg CO₂/km) - Tuk-tuk
- **Bus** (0.05 kg CO₂/km) - Public transport (greenest)
- **Car** (0.21 kg CO₂/km) - Personal vehicle
- **Bike** (0 kg CO₂/km) - Carbon-free

---

## 📋 File Structure

```
atig/
├── app/                    # Main Flask app
│   ├── routes/            # Flask blueprints
│   ├── services/          # AI services
│   ├── templates/         # HTML files
│   └── static/            # CSS & JS
├── data/
│   ├── jaipur_attractions.json      # 10 attractions
│   ├── footfall_history.json        # 90 days of data (generated)
│   └── generate_footfall.py         # Data generator
├── run.py                 # Start server
├── config.py              # Configuration
├── requirements.txt       # Dependencies
└── README.md              # Full documentation
```

---

## 🐛 Common Issues

### Issue: "ModuleNotFoundError: No module named 'prophet'"
**Solution**:
```bash
pip install --no-cache-dir fbprophet
pip install cmdstanpy==1.0.8
```

### Issue: Port 5000 already in use
**Solution**:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use different port
set PORT=5001
python run.py
```

### Issue: No footfall data
**Solution**:
```bash
cd data
python generate_footfall.py
python run.py
```

---

## 💡 Key Features Demo

### 1. Crowd Prediction
- Prophet models predict next 24 hours
- Shows peak hours per attraction
- Confidence intervals included

### 2. Route Optimization
- Solves TSP with crowd constraints
- Reorders attractions for optimal flow
- Calculates travel times and distances

### 3. Sustainability Scoring
- Carbon footprint calculation
- Crowd impact assessment
- Heritage site protection score
- Recommendations for greener choices

### 4. Government Dashboard
- Real-time congestion heatmap
- City analytics (attractions, visitors)
- Heritage site alerts
- Data exportable for policy

---

## 📞 Support

**Check these first**:
1. Make sure virtual environment is activated
2. Verify Python 3.8+ installed: `python --version`
3. Check all dependencies installed: `pip list | findstr Flask`
4. Ensure data files exist in `/data` folder

**If still stuck**:
1. Check console output for error messages
2. Try re-generating footfall data
3. Check logs at bottom of command window

---

## 🎯 Next Steps

### Explore Features
- [ ] Create 5 different itineraries
- [ ] Compare sustainability scores
- [ ] Test all attractions
- [ ] Check dashboard heatmaps

### Customize
- [ ] Add your own attractions to `jaipur_attractions.json`
- [ ] Modify carbon factors in `sustainability.py`
- [ ] Change time budget ranges in `plan.html`

### Extend
- [ ] Add real-time sensor data
- [ ] Integrate weather API
- [ ] Deploy to cloud (AWS/GCP)
- [ ] Create mobile app

---

## 📊 Demos to Show

### Demo 1: Intelligence (2 min)
1. Go to Dashboard
2. Show heatmap (explain colors)
3. Explain analytics metrics

### Demo 2: Tourism UX (3 min)
1. Go to Attractions page
2. Select 3 sites
3. Click "Optimize"
4. Show reordered itinerary
5. Highlight sustainability score

### Demo 3: API (2 min)
1. Open terminal
2. Run curl command to optimize itinerary
3. Show JSON response with full data

---

## 🏆 Smart India Hackathon Ready

✅ **All Requirements Met**:
- AI-powered (Prophet + NetworkX)
- Real-world city (Jaipur)
- Demonstrable features (working MVP)
- Clean architecture (modular design)
- Sustainable focus (eco-scoring)
- Government use case (dashboard)

---

**Total Setup Time**: ~10 minutes  
**Demo Time**: ~5 minutes  
**Total Lines of Code**: ~3500+  
**AI Models**: 2 (Prophet + TSP)  
**REST APIs**: 6 endpoints  

**Status**: ✅ Ready to deploy
