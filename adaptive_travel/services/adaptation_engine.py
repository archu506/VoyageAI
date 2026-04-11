"""
Real-Time Adaptive Travel Brain - Scoring-Based Adaptation Engine

This module implements intelligent itinerary adaptation using a scoring system
that accounts for weather, crowd levels, air quality, and user energy.

Scoring Logic:
- Each attraction starts with base_score = 100
- Adjustments are applied based on conditions (weather, AQI, crowds)
- Final score determines the order: higher scores = visit first
- Energy is tracked: total 100, divided across selected attractions
"""


class AdaptationEngine:
    """
    Scoring-based adaptation engine for travel itineraries.
    
    Uses a transparent scoring system to rank attractions based on:
    - Weather conditions (rain impacts outdoor activities)
    - Crowd levels (affects popularity-based attractions)
    - Air Quality Index (impacts all activities, especially sensitive ones)
    - User energy (removes high-cost activities if energy runs low)
    """
    
    # Scoring constants
    BASE_SCORE = 100
    WEATHER_PENALTY = 30  # Outdoor penalty if raining
    CROWD_PENALTY = 25    # Popular attraction penalty if crowds high
    AQI_OUTDOOR_PENALTY = 20  # Outdoor penalty if AQI > 120
    AQI_SENSITIVE_PENALTY = 30  # Pollution-sensitive penalty if AQI > 120
    INITIAL_ENERGY = 100
    ENERGY_THRESHOLD_LOW = 50  # Energy threshold for reduction
    
    def __init__(self):
        """Initialize adaptation engine with default conditions"""
        self.weather_raining = False
        self.crowd_level = "medium"  # low, medium, high
        self.aqi_level = 150
        self.explanations = []
    
    def set_conditions(self, weather_raining=False, crowd_level="medium", aqi_level=150):
        """
        Set current environmental conditions.
        
        Args:
            weather_raining: Boolean, True if rain expected
            crowd_level: String, one of 'low', 'medium', 'high'
            aqi_level: Integer 0-500, air quality index
        """
        self.weather_raining = weather_raining
        self.crowd_level = crowd_level
        self.aqi_level = aqi_level
        self.explanations = []
    
    @staticmethod
    def classify_aqi(aqi):
        """
        Classify AQI value into human-readable category.
        
        Args:
            aqi: Integer AQI value
            
        Returns:
            String classification
        """
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Satisfactory"
        elif aqi <= 200:
            return "Moderately Polluted"
        elif aqi <= 300:
            return "Poor"
        else:
            return "Very Poor"
    
    def calculate_attraction_adjustments(self, attraction):
        """
        Calculate score adjustments for a single attraction based on conditions.
        
        Args:
            attraction: Dictionary with attraction data
            
        Returns:
            Tuple (adjustment_value, reason_list)
        """
        adjustments = 0
        reasons = []
        
        # Weather impact: outdoor activities suffer in rain
        if self.weather_raining and attraction['type'] == 'outdoor':
            adjustments -= self.WEATHER_PENALTY
            reasons.append(f"Rain penalty (-{self.WEATHER_PENALTY})")
        
        # Crowd impact: high popularity places suffer when crowds are high
        if self.crowd_level == "high" and attraction['popularity'] == 'high':
            adjustments -= self.CROWD_PENALTY
            reasons.append(f"High crowd penalty (-{self.CROWD_PENALTY})")
        
        # AQI impact: outdoor and sensitive places suffer in high pollution
        if self.aqi_level > 120:
            if attraction['type'] == 'outdoor':
                adjustments -= self.AQI_OUTDOOR_PENALTY
                reasons.append(f"AQI outdoor penalty (-{self.AQI_OUTDOOR_PENALTY})")
            
            if attraction['pollution_sensitivity'] == 'high':
                adjustments -= self.AQI_SENSITIVE_PENALTY
                reasons.append(f"Pollution sensitivity penalty (-{self.AQI_SENSITIVE_PENALTY})")
        
        return adjustments, reasons
    
    def score_attractions(self, attractions):
        """
        Calculate final scores for all attractions based on conditions.
        
        Args:
            attractions: List of attraction dictionaries
            
        Returns:
            List of attractions with added 'final_score' and 'scoring_breakdown'
        """
        scored = []
        
        from services.crowd_predictor import CrowdPredictor
        import datetime
        predictor = CrowdPredictor()
        now = datetime.datetime.now()
        hour = now.hour
        if 5 <= hour < 12:
            time_of_day = 'morning'
        elif 12 <= hour < 17:
            time_of_day = 'afternoon'
        elif 17 <= hour < 21:
            time_of_day = 'evening'
        else:
            time_of_day = 'night'
        is_weekend = now.weekday() >= 5
        # Use weather if available, else default to clear
        weather_condition = 'clear'
        if 'weather' in attr and attr['weather']:
            weather_map = {
                'clear': 'clear',
                'sunny': 'clear',
                'cloudy': 'cloudy',
                'rain': 'rainy',
                'rainy': 'rainy',
                'storm': 'stormy',
                'stormy': 'stormy'
            }
            weather_condition = weather_map.get(str(attr['weather']).lower(), 'clear')
        crowd_result = predictor.predict(time_of_day, is_weekend, weather_condition)
        scored.append({
            **attr,
            'final_score': max(0, final_score),  # Score can't go below 0
            'scoring_breakdown': {
                'base': self.BASE_SCORE,
                'adjustments': adjustments,
                'reasons': reasons
            },
            'crowd_score': crowd_result['crowd_score'],
            'crowd_level': crowd_result['crowd_level']
        })
        
        return scored
    
    def calculate_energy_remaining(self, selected_attractions, removed_ids=None):
        """
        Calculate remaining user energy after selected activities.
        Robust: prevents infinite recursion, negative values, and handles all-attractions-removed edge case.
        Args:
            selected_attractions: List of selected attractions
            removed_ids: Set of attraction IDs removed due to low energy
        Returns:
            Tuple (energy_remaining, total_cost, removed_ids)
        """
        if removed_ids is None:
            removed_ids = set()

        energy = self.INITIAL_ENERGY
        total_cost = 0

        # Calculate total energy cost
        for attr in selected_attractions:
            if attr['id'] not in removed_ids:
                cost = max(0, attr.get('base_energy_cost', 0))
                energy -= cost
                total_cost += cost

        # Prevent negative energy
        energy = max(0, energy)

        # If energy too low, remove highest-cost attractions until energy is sufficient or none left
        while energy < self.ENERGY_THRESHOLD_LOW:
            candidates = [a for a in selected_attractions if a['id'] not in removed_ids]
            if not candidates:
                break  # All attractions removed
            highest_cost_attr = max(candidates, key=lambda x: x.get('base_energy_cost', 0), default=None)
            if highest_cost_attr is None:
                break
            removed_ids.add(highest_cost_attr['id'])
            cost = max(0, highest_cost_attr.get('base_energy_cost', 0))
            energy += cost
            total_cost -= cost
            # Recalculate energy after removal
            energy = self.INITIAL_ENERGY
            total_cost = 0
            for attr in selected_attractions:
                if attr['id'] not in removed_ids:
                    c = max(0, attr.get('base_energy_cost', 0))
                    energy -= c
                    total_cost += c
            energy = max(0, energy)

        return energy, total_cost, removed_ids
    
    def adapt_itinerary(self, selected_attractions):
        """
        Main adaptation logic: score, sort, and optimize itinerary.
        
        Args:
            selected_attractions: List of user-selected attractions
            
        Returns:
            Dictionary with original plan, adapted plan, scores, and explanations
        """
        if not selected_attractions:
            return {
                "original_plan": [],
                "adapted_plan": [],
                "removed_attractions": [],
                "energy_remaining": self.INITIAL_ENERGY,
                "explanations": [],
                "schedule_modified": False,
                "conditions": {
                    "weather_raining": self.weather_raining,
                    "crowd_level": self.crowd_level,
                    "aqi_level": self.aqi_level,
                    "aqi_classification": self.classify_aqi(self.aqi_level)
                }
            }
        
        # Store original order
        original_plan = [attr.copy() for attr in selected_attractions]
        
        # Score all attractions
        scored_attractions = self.score_attractions(selected_attractions)
        
        # Sort by final score (descending) - highest scores first
        adapted_plan = sorted(scored_attractions, key=lambda x: x['final_score'], reverse=True)
        
        # Calculate energy and remove high-cost items if needed
        energy_remaining, total_energy_cost, removed_ids = self.calculate_energy_remaining(
            adapted_plan
        )
        
        # Filter out removed attractions
        adapted_plan = [a for a in adapted_plan if a['id'] not in removed_ids]
        removed_attractions = [a for a in selected_attractions if a['id'] in removed_ids]
        
        # Build explanations
        explanations = self._build_explanations(
            scored_attractions, 
            original_plan, 
            adapted_plan, 
            removed_attractions,
            energy_remaining
        )
        
        return {
            "original_plan": original_plan,
            "adapted_plan": adapted_plan,
            "removed_attractions": removed_attractions,
            "energy_remaining": energy_remaining,
            "total_energy_used": total_energy_cost,
            "explanations": explanations,
            "schedule_modified": adapted_plan != original_plan,
            "conditions": {
                "weather_raining": self.weather_raining,
                "crowd_level": self.crowd_level,
                "aqi_level": self.aqi_level,
                "aqi_classification": self.classify_aqi(self.aqi_level)
            },
            "scoring_details": {
                attr['name']: attr['scoring_breakdown'] 
                for attr in scored_attractions
            }
        }
    
    def _build_explanations(self, scored_attractions, original, adapted, removed, energy):
        """
        Build human-readable explanations for adaptations.
        
        Args:
            scored_attractions: All attractions with scores
            original: Original plan
            adapted: Adapted plan
            removed: Removed attractions
            energy: Remaining energy
            
        Returns:
            List of explanation strings
        """
        explanations = []
        
        # Explain conditions
        if self.weather_raining:
            explanations.append("🌧️ Rain detected - outdoor activities penalized")
        
        if self.crowd_level == "high":
            explanations.append("👥 High crowd levels - popular attractions penalized")
        
        if self.aqi_level > 120:
            aqi_class = self.classify_aqi(self.aqi_level)
            explanations.append(
                f"💨 AQI {self.aqi_level} ({aqi_class}) - outdoor & sensitive places penalized"
            )
        
        # Explain reordering
        if adapted != original:
            explanations.append("🔄 Re-ordered by attraction scores for optimal experience")
        else:
            explanations.append("✅ No reordering needed - original plan is optimal")
        
        # Explain removals
        if removed:
            removed_names = ", ".join([a['name'] for a in removed])
            explanations.append(
                f"⚡ Removed {removed_names} due to low energy (remaining: {energy}/100)"
            )
        else:
            explanations.append(f"✅ All activities fit within energy budget (remaining: {energy}/100)")
        
        # Energy summary
        if energy < 30:
            explanations.append("⚠️ Low energy remaining - consider a lighter schedule")
        elif energy < 50:
            explanations.append("⚡ Moderate energy - add short activities for balance")
        
        return explanations
    
    def generate_timeline(self, adapted_plan):
        """
        Generate time-based timeline for the itinerary.
        
        Args:
            adapted_plan: List of adapted attractions (in order)
            
        Returns:
            List of timeline items with time slots
        """
        timeline = []
        start_time = 9  # Start at 9 AM
        
        for idx, attraction in enumerate(adapted_plan):
            duration = attraction.get('duration', 60)
            end_time = start_time + (duration // 60)
            
            timeline.append({
                "order": idx + 1,
                "name": attraction['name'],
                "start": f"{start_time:02d}:00",
                "end": f"{end_time:02d}:00",
                "duration": duration,
                "description": attraction['description'],
                "score": attraction.get('final_score', 0)
            })
            
            start_time = end_time + 1  # 1 hour break between activities
        
        return timeline
