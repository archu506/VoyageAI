# ATIG Architecture & Design Document

## 📐 System Architecture Overview

ATIG is built on a **modular, service-oriented architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACES                      │
├──────────────┬──────────────┬──────────────┬────────────┤
│    Home      │   Planner    │ Attractions  │ Dashboard  │
│ (index.html) │ (plan.html)  │(attractions) │(dashboard) │
└──────────────┴──────────────┴──────────────┴────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│              FLASK WEB FRAMEWORK                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Routes (blueprints): main.py | api.py | dashboard │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│            AI SERVICES LAYER                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │  crowd_model.py    → Prophet Forecasting         │   │
│  │  route_optimizer.py → NetworkX TSP Solving       │   │
│  │  sustainability.py → Eco-scoring & Carbon        │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│              DATA LAYER                                 │
│  ┌────────────────┬──────────────────────────────────┐  │
│  │ jaipur_        │ footfall_history.json            │  │
│  │ attractions.   │ (90 days × 10 attractions)      │  │
│  │ json           │                                  │  │
│  └────────────────┴──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Component Breakdown

### 1. **Frontend Layer** (HTML/CSS/JS)

**Files**:
- `app/templates/base.html` - Master template
- `app/templates/index.html` - Homepage
- `app/templates/plan.html` - Itinerary planner
- `app/templates/dashboard.html` - Government dashboard
- `app/templates/attractions.html` - Attractions listing
- `app/templates/about.html` - Project info
- `app/static/css/style.css` - Styling (1000+ lines)
- `app/static/js/main.js` - Client-side utilities

**Technologies**:
- Leaflet.js (maps)
- Chart.js (forecasting charts)
- Fetch API (AJAX calls)
- Responsive CSS Grid

**Key Pages**:

| Page | Route | Purpose |
|------|-------|---------|
| Home | `/` | Overview & stats |
| Plan | `/plan` | Interactive itinerary builder |
| Attractions | `/attractions` | Browse all sites |
| Dashboard | `/dashboard` | Real-time analytics |
| About | `/about` | ATIG explanation |

---

### 2. **Application Layer** (Flask)

**Core**: `app/__init__.py`
```python
def create_app(config_name="development"):
    app = Flask(__name__)
    # Register blueprints
    app.register_blueprint(main_bp)          # Web pages
    app.register_blueprint(api_bp, ...)      # REST API
    app.register_blueprint(dashboard_bp, ...) # Gov dashboard
    return app
```

**Blueprints**:

#### A. `app/routes/main.py` - Web Pages
```
GET  /              → Homepage
GET  /plan          → Itinerary planner
GET  /attractions   → Attractions listing
GET  /about         → About page
```

#### B. `app/routes/api.py` - REST API
```
GET  /api/attractions              → All attractions (JSON)
GET  /api/crowd-forecast           → 24h predictions
POST /api/optimize-itinerary       → Route optimization
GET  /api/attraction/<id>/optimal-time
GET  /api/city-congestion          → Heatmap data
GET  /api/health                   → Health check
```

#### C. `app/routes/dashboard.py` - Government
```
GET  /dashboard                    → Dashboard page
GET  /dashboard/api/heatmap-data   → Live heatmap
GET  /dashboard/api/analytics      → City analytics
```

---

### 3. **Service Layer** (AI/ML Logic)

#### A. Crowd Prediction Service
**File**: `app/services/crowd_model.py`

**Class**: `CrowdPredictionModel`

**Methods**:
```python
train(attractions_path)                    # Train on historical data
predict_24h(attraction_id, hours=24)      # Forecast for next N hours
get_crowd_level(footfall, baseline)       # Classify: LOW, MODERATE, BUSY, CROWDED
get_city_forecast(hours=24)               # Aggregate all attractions
```

**Uses**:
- Facebook Prophet (ARIMA + seasonality)
- Fallback: Hour-based heuristics
- Input: 90 days of hourly footfall
- Output: Predictions with 95% confidence intervals

**Algorithm**:
```
Historical Data (90 days)
    ↓
Prophet Model
    ├─ Yearly seasonality: Disabled (no years)
    ├─ Daily seasonality: Enabled
    └─ Interval width: 0.95 (95% confidence)
    ↓
24-hour Forecast with bounds
```

#### B. Route Optimizer Service
**File**: `app/services/route_optimizer.py`

**Class**: `RouteOptimizer`

**Methods**:
```python
optimize_itinerary(selected, crowd_preds, time_budget)  # Main optimization
get_distance(from_id, to_id)                           # Haversine distance
_nearest_neighbor_tsp(attractions, scores)             # Greedy TSP
_brute_force_tsp(attractions, scores)                  # Optimal TSP (n≤5)
_add_timing(route, total_hours, max_travel)           # Schedule timing
```

**Problem**:
- Input: N attractions, crowd predictions, time budget
- Output: Ordered route with timing
- Constraints: Distance, time, crowd avoidance

**Algorithm**:
```
For N ≤ 5:
  Permutation-based optimal solution
  (Checks all N! combinations)

For N > 5:
  Nearest Neighbor Heuristic:
  1. Start at highest-score attraction
  2. Greedily pick closest unvisited
  3. Repeat until all visited
  
Cost = Distance + Heritage_Weight - Crowd_Penalty
```

**Distance Calculation**:
```python
# Haversine formula for lat/long
a = sin²(Δlat/2) + cos(lat1) · cos(lat2) · sin²(Δlon/2)
c = 2 · atan2(√a, √(1−a))
distance = R · c  # R = 6371 km
```

#### C. Sustainability Service
**File**: `app/services/sustainability.py`

**Class**: `SustainabilityCalculator`

**Scoring Model**:
```
Overall Score (0-100) = 
    (30% × carbon_score) +
    (40% × crowd_score) +
    (20% × heritage_score) +
    (10% × time_efficiency_score)
```

**Methods**:
```python
calculate_sustainability_score(itinerary, crowd_preds, mode)
calculate_carbon_footprint(itinerary, transport_mode)
calculate_crowd_impact(itinerary, crowd_predictions)
find_optimal_visit_time(attraction_id)
```

**Carbon Factors** (kg CO₂ per km, round-trip):
```python
"car": 0.21    # Personal vehicle (lowest eco)
"auto": 0.12   # Tuk-tuk (medium)
"bus": 0.05    # Public bus (good)
"bike": 0.0    # Bicycle (best)
```

**Crowd Impact Calculation**:
- Base eco impact: Low (1) | Medium (2) | High (3)
- Multiplier by crowd level:
  - LOW: 0.5× (better)
  - MODERATE: 1.0× (baseline)
  - BUSY: 1.5× (worse)
  - CROWDED: 2.0× (harmful)

**Recommendations Generated**:
- Carbon: Suggest bus if emissions > 30kg
- Crowd: Suggest off-peak if impact > 60
- Heritage: Suggest more cultural sites
- Time: Balance long vs short visits

---

## 📊 Data Layer

### Data Files

#### `data/jaipur_attractions.json`
```json
{
  "city": "Jaipur",
  "attractions": [
    {
      "id": "A001",
      "name": "City Palace",
      "latitude": 26.9250,
      "longitude": 75.8231,
      "category": "Heritage",
      "baseline_footfall": 850,
      "peak_hours": "10-12, 14-16",
      "congestion_factor": 1.2,
      "heritage_priority": 9,
      "eco_impact": "high"
    },
    ...
  ]
}
```

**Schema**:
| Field | Type | Purpose |
|-------|------|---------|
| id | str | Unique identifier |
| name | str | Display name |
| latitude/longitude | float | GPS coordinates |
| baseline_footfall | int | Baseline visitors/hour |
| peak_hours | str | Peak congestion times |
| congestion_factor | float | Multiplier on baseline |
| heritage_priority | int | 1-10 (UNESCO priority) |
| eco_impact | str | low/medium/high |

#### `data/footfall_history.json` (Generated)
```json
[
  {
    "timestamp": "2024-01-01T08:00:00",
    "attraction_id": "A001",
    "attraction_name": "City Palace",
    "footfall": 950,
    "hour": 8,
    "day_of_week": 0,
    "is_weekend": false
  },
  ...
]
```

**90 Days × 24 Hours × 10 Attractions = 21,600 records**

### Data Generation

**File**: `data/generate_footfall.py`

**Process**:
1. Load attractions metadata
2. For each day in 90-day window:
   - Calculate hour-based multiplier (peak vs off-peak)
   - Apply weekend multiplier (1.4× for Sat-Sun)
   - Add random noise (±15%)
   - Handle lunch dip (12-1 PM)
3. Save as JSON

**Simulation Features**:
- Peak hours (attraction-specific)
- Weekend surge
- Morning/evening trends
- Lunch dip (reduced footfall 12-1 PM)
- Random variation (realistic noise)

---

## 🔄 Request Flow Diagrams

### Flow 1: Homepage Load
```
User visits GET /
         ↓
main.py: index()
         ↓
Render index.html
         ↓
JavaScript: fetch /api/attractions
         ↓
api.py: get_attractions()
         ↓
Load jaipur_attractions.json
         ↓
Return JSON with 10 attractions
         ↓
Display on page
```

### Flow 2: Optimize Itinerary
```
User selects 3 attractions + clicks Optimize
         ↓
POST /api/optimize-itinerary
{
  "attractions": ["A001", "A003", "A004"],
  "time_budget_hours": 8,
  "transport_mode": "auto"
}
         ↓
api.py: optimize_itinerary()
         ↓
       ┌─────────────────────────────────┐
       │ 1. Get Crowd Predictions        │
       │    crowd_model.predict_24h()    │
       │    (Prophet forecasting)        │
       └─────────────────────────────────┘
              ↓
       ┌─────────────────────────────────┐
       │ 2. Optimize Route               │
       │    route_optimizer.optimize()   │
       │    (TSP solving)                │
       └─────────────────────────────────┘
              ↓
       ┌─────────────────────────────────┐
       │ 3. Calculate Sustainability     │
       │    sustainability.calculate()   │
       │    (Eco-scoring)                │
       └─────────────────────────────────┘
              ↓
Return JSON:
{
  "itinerary": {...},
  "sustainability": {...},
  "crowd_predictions": {...}
}
         ↓
Display on frontend with map & charts
```

### Flow 3: Government Dashboard
```
User visits GET /dashboard
            ↓
dashboard.py: dashboard()
            ↓
Render dashboard.html
            ↓
JavaScript triggers 3 parallel API calls:
├─ GET /dashboard/api/heatmap-data
├─ GET /dashboard/api/analytics
└─ GET /api/crowd-forecast
            ↓
    Dashboard loads:
├─ Leaflet map with heatmap layer
├─ Statistics cards
└─ Chart.js forecast graph
            ↓
Real-time display of city congestion
```

---

## 🎯 Core Algorithms

### Algorithm 1: TSP with Crowd & Distance

**Input**:
- N attractions
- Distance matrix (N×N)
- Crowd predictions
- Heritage scores
- Time budget

**Output**:
- Ordered route
- Timing schedule
- Total metrics

**For Small N (≤5)**:
```
function Brute_Force_TSP(attractions, scores):
    best_route = attractions
    best_cost = INFINITY
    
    for each permutation of attractions:
        cost = calculate_route_cost(permutation, scores)
        if cost < best_cost:
            best_route = permutation
            best_cost = cost
    
    return best_route
```

**For Large N (>5)**:
```
function Nearest_Neighbor_TSP(attractions, scores):
    unvisited = attractions
    current = max_score_attraction(attractions)
    route = [current]
    
    while unvisited not empty:
        next = nearest_unvisited(current, unvisited)
        route.append(next)
        unvisited.remove(next)
        current = next
    
    return route
```

**Cost Function**:
```
cost(route) = sum(distances) - weighted_scores

where:
- distances = sum of haversine distances between consecutive stops
- weighted_scores = sum of attraction quality scores
  (higher score = lower cost)
```

### Algorithm 2: Prophet Time-Series Forecasting

**Model Setup**:
```python
Prophet(
    interval_width=0.95,           # 95% confidence
    yearly_seasonality=False,      # No yearly pattern
    daily_seasonality=True,        # Hour-of-day pattern
    seasonality_mode='additive'    # Linear addition
)
```

**Components**:
```
y(t) = Trend + Seasonality + Holiday + Noise

Where:
- Trend: Piecewise linear growth
- Seasonality: Hourly pattern (peak vs off-peak)
- Holiday: Not used (short-term only)
- Noise: Random variation
```

**Forecast**:
```
For next 24 hours:
1. Load historical 90-day data
2. Fit Prophet model
3. Create future dataframe (next 24 rows)
4. Generate predictions + uncertainty intervals
5. Return: yhat (prediction), yhat_lower, yhat_upper
```

### Algorithm 3: Sustainability Scoring

**Carbon Calculation**:
```python
carbon_emissions = distance × 2 × carbon_factor[transport_mode]
  # × 2 for round-trip
  
carbon_score = max(0, 100 - (emissions / 50 * 100))
  # Assume 50kg is maximum acceptable
```

**Crowd Impact**:
```python
for each attraction in itinerary:
    base_impact = eco_impact_factor[high/medium/low]  # 3/2/1
    crowd_multiplier = factor[crowd_level]            # 0.5-2.0
    visit_hours = duration
    
    impact += base_impact × crowd_multiplier × visit_hours

normalized_impact = min(100, impact × 5)
crowd_score = 100 - normalized_impact
```

**Composite Score**:
```python
overall = (
    0.30 × carbon_score +
    0.40 × crowd_score +
    0.20 × heritage_score +
    0.10 × time_efficiency_score
)
```

---

## 🧪 Testing Architecture

### Unit Tests
```
tests/
├── test_crowd_model.py
├── test_route_optimizer.py
├── test_sustainability.py
└── test_api.py
```

### Test Coverage
- Prediction accuracy (MAPE metric)
- Route optimality (vs brute-force)
- Sustainability calculations
- API response correctness
- Data loading/generation

---

## 🚀 Deployment Considerations

### Dev Environment
```bash
python run.py
# Runs on localhost:5000
```

### Production Ready
```bash
# WSGI server (Gunicorn)
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"

# Nginx reverse proxy
# Docker containerization
# Kubernetes scaling
```

### Scalability
- **Frontend**: Static files via CDN
- **API**: Load-balanced behind Nginx
- **Models**: Cache Prophet model (trained once)
- **Database**: Migrate to PostgreSQL for real data
- **Cache**: Redis for forecast caching

---

## 📈 Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Page load | <2s | With network |
| API attraction list | <50ms | JSON from disk |
| Crowd forecast (all) | 500ms-2s | Prophet inference |
| Route optimization | 100-500ms | TSP algorithm |
| Sustainability calc | <100ms | Math operations |
| Dashboard heatmap | <1s | Data aggregation |
| Full itinerary flow | 2-3s | All services combined |

---

## 🔐 Security

**Current State** (MVP):
- No authentication required
- No user data stored
- All data public/simulated

**Recommendations** (Future):
- Add user authentication (JWT)
- Rate limit API endpoints
- Validate all inputs
- Use HTTPS in production
- Sanitize user-provided data

---

## 📝 Code Organization

**Lines of Code**:
- Backend: ~2000 lines
- Frontend: ~800 lines
- Data/Config: ~200 lines
- **Total: ~3000 lines**

**Module Breakdown**:
- `crowd_model.py`: 250 lines
- `route_optimizer.py`: 300 lines
- `sustainability.py`: 250 lines
- `api.py`: 200 lines
- `main.py`, `dashboard.py`: 150 lines
- Templates: 600 lines
- CSS: 600 lines
- JS: 200 lines

---

**Architecture Version**: 1.0  
**Last Updated**: February 2024  
**Status**: Production-ready MVP
