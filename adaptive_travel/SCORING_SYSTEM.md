# Scoring-Based Adaptation Engine - Technical Guide

## Overview

The upgraded adaptation engine uses a **transparent scoring system** to intelligently reorder travel itineraries based on real-time conditions. Instead of simple if-else logic, each attraction receives a final score that determines its position in the adapted plan.

## Scoring System

### Base Score
- **Starting Score**: 100 points for all attractions
- **Final Score** = Base (100) + Adjustments
- **Minimum Score**: 0 (cannot go below zero)

### Scoring Formula
```
final_score(attraction) = 100 + weather_adjustment + crowd_adjustment + aqi_adjustment
```

### Score Adjustments

#### 1. Weather Impact 🌧️
**Condition**: `weather_raining = true`

| Affected Attractions | Penalty |
|---|---|
| Outdoor attractions | -30 |
| Indoor attractions | No change |

**Example**: Hawa Mahal (outdoor) with base score 100 → 70 if raining

#### 2. Crowd Impact 👥
**Condition**: `crowd_level = 'high'`

| Affected Attractions | Penalty |
|---|---|
| High popularity attractions | -25 |
| Medium popularity attractions | No change |
| Low popularity attractions | No change |

**Example**: City Palace (high popularity) with base score 100 → 75 if high crowds

#### 3. AQI Impact 💨
**Condition**: `aqi_level > 120`

| Affected Attractions | Penalty |
|---|---|
| Outdoor attractions | -20 |
| Pollution-sensitive attractions | -30 |
| Indoor + non-sensitive | No change |

**Note**: These penalties stack if an attraction is both outdoor AND pollution-sensitive.

**Example**: City Palace (outdoor + high pollution sensitivity) with base score 100 → 50 if AQI > 120

#### 4. Combined Impact 🎯

All adjustments are **cumulative**. An attraction can receive multiple penalties:

```
Hawa Mahal (outdoor + high pollution-sensitive + high popularity):
- Base: 100
- Rain penalty: -30 (outdoor)
- AQI penalty: -20 (outdoor) + -30 (sensitive) = -50
- Crowd penalty: -25 (high popularity)
- Final Score: 100 - 30 - 50 - 25 = -5 → 0 (clamped)

vs.

Albert Hall Museum (indoor + low sensitivity):
- Base: 100
- Rain penalty: 0 (indoor)
- AQI penalty: 0 (indoor + low sensitivity)
- Crowd penalty: 0 (medium popularity)
- Final Score: 100 (unchanged)

Result: Albert Hall Museum (100) ranked MUCH higher than Hawa Mahal (0)
```

## Energy System ⚡

### Energy Budget
- **Initial Energy**: 100 points
- **Energy Cost per Attraction**: Base energy cost (10-30 points)
- **Threshold for Reduction**: < 50 points remaining

### Energy Deduction
Each selected attraction costs energy based on its `base_energy_cost`:
- Light activities (temples, galleries): 14-20 points
- Medium activities (museums, gardens): 20-26 points
- Heavy activities (forts, bazaars): 26-30 points

### Energy Management Logic

1. **Calculate total energy needed** = sum of all `base_energy_cost` values
2. **If energy < 50**:
   - Find the attraction with the **highest energy cost**
   - **Remove it** from the plan
   - **Recalculate** remaining energy
   - **Repeat** if still < 50

### Example
```
User selects 5 attractions:
- Nahargarh Fort: 30 cost (removed first if needed)
- City Palace: 28 cost (removed second if needed)
- Jantar Mantar: 22 cost
- Albert Hall Museum: 20 cost
- Govind Dev Ji Temple: 14 cost

Total cost: 114 points (> 100, so over energy)
After removal: 114 - 30 = 84 points (still > 50)
Final plan: 4 attractions, 84 energy used, 16 remaining
```

## Attraction Metadata

Each attraction has scoring-relevant metadata:

```json
{
  "id": 1,
  "name": "City Palace",
  "type": "outdoor",              // indoor or outdoor
  "duration": 120,                 // minutes
  "base_energy_cost": 28,          // energy points (10-30)
  "popularity": "high",            // low, medium, or high
  "pollution_sensitivity": "high", // low, medium, or high (stored as "medium" internally)
  "description": "..."
}
```

## Attraction Rankings

### By Susceptibility to Conditions

**High Risk (Outdoor + High Sensitivity + High Popularity)**:
- City Palace
- Hawa Mahal
- Johari Bazaar

**Medium Risk (Outdoor + Mixed Attributes)**:
- Jantar Mantar
- Nahargarh Fort
- Sisodia Rani Garden
- Chaugan Stadium

**Low Risk (Indoor + Low Sensitivity)**:
- Albert Hall Museum
- City Palace Art Gallery

**Very Low Risk (Outdoor + Low Sensitivity)**:
- Govind Dev Ji Temple

## Adaptation Process

### Step 1: Score All Attractions
For each selected attraction, calculate final_score based on current conditions.

### Step 2: Sort by Score (Descending)
Attractions with higher scores appear first in the adapted plan.

### Step 3: Check Energy
Sum up the energy costs of selected attractions in order.

### Step 4: Remove High-Cost Items if Needed
If total energy > 100, remove the highest-cost attraction and recalculate.

### Step 5: Build Timeline
Assign time slots to adapted plan in the new order.

## Transparency & Explanations

The system provides:

1. **Scoring Details**: 
   - Base score: 100
   - Adjustments applied
   - Final score for each attraction

2. **Explanations**:
   - Which conditions affected the plan
   - Why attractions were reordered
   - Which attractions were removed and why
   - Energy status

3. **Timeline**:
   - Start time: 9:00 AM
   - End time: calculated based on duration + 1-hour breaks
   - Activity score for reference

## API Response Format

```json
{
  "original_plan": [...],           // User's initial selection
  "adapted_plan": [...],            // Reordered by final_score descending
  "removed_attractions": [...],     // Removed due to energy constraints
  "energy_remaining": 45,           // Remaining energy budget
  "total_energy_used": 55,          // Energy consumed by adapted plan
  "explanations": [                 // Human-readable reasons
    "🌧️ Rain detected - outdoor activities penalized",
    "🔄 Re-ordered by attraction scores for optimal experience",
    "✅ All activities fit within energy budget (remaining: 45/100)"
  ],
  "schedule_modified": true,        // Whether plan was reordered
  "conditions": {
    "weather_raining": true,
    "crowd_level": "high",
    "aqi_level": 180,
    "aqi_classification": "Moderately Polluted"
  },
  "scoring_details": {              // Score breakdowns per attraction
    "City Palace": {
      "base": 100,
      "adjustments": -105,          // Total penalties
      "reasons": [
        "Rain penalty (-30)",
        "AQI outdoor penalty (-20)",
        "Pollution sensitivity penalty (-30)",
        "High crowd penalty (-25)"
      ]
    },
    ...
  },
  "timeline": [...]                 // Time-slot itinerary
}
```

## Real-World Scenarios

### Scenario 1: Monsoon Season (Heavy Rain, High AQI)
- **Conditions**: Rain + AQI 250 (Poor)
- **Expected Result**: All outdoor attractions severely penalized
- **Recommended Plan**: Indoor-first itinerary (museums, galleries)
- **Energy Impact**: Few activities needed due to energy constraints

### Scenario 2: Festival Day (High Crowds)
- **Conditions**: No rain + AQI 100 (Good) + High crowds
- **Expected Result**: Popular attractions penalized
- **Recommended Plan**: Less-known attractions (gardens, temples)
- **Energy Impact**: More activities fit into energy budget

### Scenario 3: Perfect Day (Clear Weather, Low AQI)
- **Conditions**: Clear sky + AQI 50 (Good) + Low crowds
- **Expected Result**: Minimal reordering
- **Recommended Plan**: All attractions highly ranked
- **Energy Impact**: Fit more attractions into the day

### Scenario 4: Low User Energy
- **Conditions**: Any weather + User selects 5+ heavy activities
- **Expected Result**: Energy < 50 triggers removal logic
- **Recommended Plan**: Highest-cost items removed first
- **Energy Impact**: Reduced plan of 2-3 activities

## Implementation Details

### Key Functions

1. **`calculate_attraction_adjustments(attraction)`**
   - Returns (adjustment_value, reason_list)
   - Checks weather, crowd, AQI conditions
   - Applies appropriate penalties

2. **`score_attractions(attractions)`**
   - Scores all attractions
   - Returns attractions with final_score and breakdown

3. **`calculate_energy_remaining(attractions, removed_ids)`**
   - Recursive function to handle energy constraints
   - Removes highest-cost attraction if needed
   - Returns (energy, cost, removed_ids)

4. **`adapt_itinerary(selected_attractions)`**
   - Main orchestration function
   - Calls score, sort, and energy functions
   - Returns complete adaptation result

5. **`generate_timeline(adapted_plan)`**
   - Creates time-slotted view
   - Starts at 9 AM, adds 1-hour breaks

### Code Quality
- ✅ **Modular**: Each function has single responsibility
- ✅ **Transparent**: All logic explained in comments
- ✅ **Testable**: Pure functions with clear inputs/outputs
- ✅ **No ML**: Pure logic-based scoring (no algorithms, no models)
- ✅ **Scalable**: Easy to add new conditions or attractions

## Testing the System

### Test Case 1: Basic Scoring
```
Select: City Palace, Albert Hall Museum
Weather: Clear, Crowds: Low, AQI: 100
Expected: Minimal score changes, order unchanged
```

### Test Case 2: Rain Impact
```
Select: Hawa Mahal, Sisodia Rani Garden, Museum
Weather: Raining, Crowds: Low, AQI: 100
Expected: Museum moves to first position
```

### Test Case 3: Energy Limit
```
Select: Nahargarh Fort, City Palace, Jantar Mantar, Museum, Temple (all 5)
Weather: Clear, Crowds: Low, AQI: 100
Expected: Nahargarh Fort removed (highest cost = 30)
Result: 4 attractions, ~70 energy used
```

### Test Case 4: Combined Conditions
```
Select: City Palace, Hawa Mahal, Johari Bazaar, Museum (3 high-risk, 1 safe)
Weather: Raining, Crowds: High, AQI: 200
Expected: Museum ranked first, outdoor attractions penalized heavily
```

---

**Last Updated**: February 26, 2026
**Version**: 1.0 (Scoring-Based)
**Status**: ✅ Production Ready
