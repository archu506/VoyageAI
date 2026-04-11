from typing import List, Dict
from datetime import datetime
from .logger import logger, log_fallback

class AdaptationEngine:
    """
    Intelligent itinerary adaptation with weighted scoring.
    Considers: weather, AQI, time of day, crowd level, user energy.
    Activates fallback logic for extreme conditions.
    """
    
    # Scoring weights (sum = 100)
    WEIGHT_WEATHER = 25
    WEIGHT_AQI = 20
    WEIGHT_CROWD = 15
    WEIGHT_TIME_OF_DAY = 15
    WEIGHT_ENERGY = 25
    
    # Thresholds for fallback logic
    RAIN_THRESHOLD = 0.6  # 60% chance = prioritize indoor
    POOR_AQI_THRESHOLD = 150  # AQI > 150 = avoid outdoor
    HEAT_THRESHOLD = 38  # 38°C = avoid physical activities
    LOW_ENERGY_THRESHOLD = 30  # 30% energy = reduce distance
    
    def __init__(self):
        self.weather = None
        self.aqi = None
        self.crowd_level = 0
        self.user_energy = 100
        self.current_hour = datetime.now().hour
        self.fallback_mode = False
        self.fallback_reasons = []
    
    def adapt(self, attractions: List[Dict], weather: Dict, aqi: Dict, 
              crowd_level: int, user_energy: int,
              heat_tolerance: float = 38.0,
              rain_tolerance: float = 0.6,
              aqi_tolerance: int = 150) -> Dict:
        """
        Main adaptation with intelligent scoring and fallback.
        Returns: ranked attractions, selected items, timeline, metadata.
        """
        self.weather = weather
        self.aqi = aqi
        self.crowd_level = crowd_level
        self.user_energy = user_energy
        self.heat_tolerance = heat_tolerance
        self.rain_tolerance = rain_tolerance
        self.aqi_tolerance = aqi_tolerance
        self.current_hour = datetime.now().hour
        self.fallback_reasons = []
        
        # Check for extreme conditions (activate fallback)
        self._check_fallback_conditions()
        
        # Score all attractions
        scored = self._score_attractions(attractions)
        
        # Apply fallback reordering if needed
        if self.fallback_mode:
            scored = self._apply_fallback_logic(scored)
        
        # Sort by score
        ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
        
        # Select attractions by energy budget
        selected = self._select_by_energy(ranked)
        
        # Generate timeline
        timeline = self._generate_timeline(selected)
        
        return {
            "ranked_attractions": ranked,
            "selected": selected,
            "timeline": timeline,
            "total_energy_used": sum(a.get("energy_cost", 0) for a in selected),
            "energy_remaining": user_energy - sum(a.get("energy_cost", 0) for a in selected),
            "weather_source": weather.get("source", "unknown"),
            "aqi_level": aqi.get("level", "Unknown"),
            "fallback_active": self.fallback_mode,
            "fallback_reasons": self.fallback_reasons
        }
    
    def _check_fallback_conditions(self):
        """Check if extreme conditions require fallback logic."""
        self.fallback_mode = False
        self.fallback_reasons = []
        
        # Rain threshold
        if self.weather.get("rain_prob", 0) > self.rain_tolerance:
            self.fallback_mode = True
            self.fallback_reasons.append(f"Heavy rain ({int(self.weather['rain_prob']*100)}%) → Prioritize indoor")
            log_fallback(f"Rain probability {self.weather['rain_prob']} > {self.rain_tolerance}")
        
        # Poor AQI threshold
        if self.aqi.get("numeric_value", 0) > self.aqi_tolerance:
            self.fallback_mode = True
            self.fallback_reasons.append(f"Poor AQI ({self.aqi['numeric_value']}) → Avoid outdoor")
            log_fallback(f"AQI {self.aqi['numeric_value']} > {self.aqi_tolerance}")
        
        # Heat threshold
        if self.weather.get("temperature", 0) > self.heat_tolerance:
            self.fallback_mode = True
            self.fallback_reasons.append(f"Extreme heat ({int(self.weather['temperature'])}°C) → Reduce intensity")
            log_fallback(f"Temperature {self.weather['temperature']} > {self.heat_tolerance}")
        
        # Low energy
        if self.user_energy < self.LOW_ENERGY_THRESHOLD:
            self.fallback_mode = True
            self.fallback_reasons.append(f"Low energy ({self.user_energy}%) → Easy walks only")
            log_fallback(f"User energy {self.user_energy} < {self.LOW_ENERGY_THRESHOLD}")
    
    def _score_attractions(self, attractions: List[Dict]) -> List[Dict]:
        """Score attractions using weighted multi-factor algorithm."""
        scored = []
        
        for attr in attractions:
            # Initialize scores
            weather_score = self._score_weather(attr)
            aqi_score = self._score_aqi(attr)
            crowd_score = self._score_crowd(attr)
            time_score = self._score_time_of_day(attr)
            energy_score = self._score_energy(attr)
            
            # Weighted total (0-100)
            total_score = (
                weather_score * (self.WEIGHT_WEATHER / 100) +
                aqi_score * (self.WEIGHT_AQI / 100) +
                crowd_score * (self.WEIGHT_CROWD / 100) +
                time_score * (self.WEIGHT_TIME_OF_DAY / 100) +
                energy_score * (self.WEIGHT_ENERGY / 100)
            )
            
            # Energy cost based on physical intensity
            intensity = attr.get("physical_intensity", 5)
            energy_cost = int(intensity / 2) + 5  # 7-20 range
            
            scored.append({
                **attr,
                "score": max(0, total_score),
                "energy_cost": energy_cost,
                "weather_score": weather_score,
                "aqi_score": aqi_score,
                "crowd_score": crowd_score,
                "time_score": time_score,
                "energy_score": energy_score
            })
        
        return scored
    
    def _score_weather(self, attr: Dict) -> float:
        """Weather suitability score (0-100)."""
        base = 100
        temp = self.weather.get("temperature", 25)
        rain = self.weather.get("rain_prob", 0)
        indoor_ratio = attr.get("indoor", 0)
        weather_sensitive = attr.get("weather_sensitive", True)
        
        # Indoor attractions protected
        if indoor_ratio > 0.5:
            return 100
        
        # Outdoor penalties
        if not weather_sensitive:
            return 100
        
        # Rain penalty for outdoor
        if rain > 0.3:
            base -= int(rain * 50)
        
        # Temperature penalties
        if temp > 35:
            base -= 20  # Heat
        elif temp < 10:
            base -= 15  # Cold
        
        return max(10, base)
    
    def _score_aqi(self, attr: Dict) -> float:
        """AQI suitability score (0-100)."""
        aqi_level = self.aqi.get("level", "Fair")
        aqi_sensitive = attr.get("aqi_sensitive", True)
        indoor_ratio = attr.get("indoor", 0)
        
        # Indoor protected
        if indoor_ratio > 0.5:
            return 100
        
        # If not AQI sensitive, no penalty
        if not aqi_sensitive:
            return 100
        
        # Outdoor penalties based on AQI
        if aqi_level == "Very Poor":
            return 20
        elif aqi_level == "Poor":
            return 40
        elif aqi_level == "Moderate":
            return 70
        else:  # Good/Fair
            return 100
    
    def _score_crowd(self, attr: Dict) -> float:
        """Crowd tolerance score (0-100)."""
        crowd = self.crowd_level
        
        # Less crowded = better
        if crowd < 30:
            return 100
        elif crowd < 50:
            return 90
        elif crowd < 70:
            return 70
        else:
            return 40
    
    def _score_time_of_day(self, attr: Dict) -> float:
        """Time of day suitability (0-100)."""
        best_time = attr.get("best_time", "afternoon")
        hour = self.current_hour
        
        # Map hours to time periods
        if 6 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 17:
            period = "afternoon"
        elif 17 <= hour < 21:
            period = "evening"
        else:
            period = "night"
        
        if period == best_time:
            return 100
        elif (period == "morning" and best_time in ["afternoon"]) or \
             (period == "afternoon" and best_time in ["morning", "evening"]):
            return 70
        else:
            return 50
    
    def _score_energy(self, attr: Dict) -> float:
        """Energy compatibility score (0-100)."""
        intensity = attr.get("physical_intensity", 5)
        energy = self.user_energy
        
        # Normalize intensity (1-10) to energy cost
        required_energy = intensity * 10
        
        if energy >= required_energy:
            return 100
        elif energy >= required_energy * 0.7:
            return 80
        elif energy >= required_energy * 0.5:
            return 60
        else:
            return 30
    
    def _apply_fallback_logic(self, scored: List[Dict]) -> List[Dict]:
        """Reorder attractions based on fallback conditions."""
        fallback_scored = []
        
        for attr in scored:
            score = attr["score"]
            indoor_ratio = attr.get("indoor", 0)
            intensity = attr.get("physical_intensity", 5)
            
            # Heavy rain → boost indoor
            if self.weather.get("rain_prob", 0) > self.RAIN_THRESHOLD:
                score += (score * indoor_ratio * 0.3)
            
            # Poor AQI → boost indoor
            if self.aqi.get("numeric_value", 0) > self.POOR_AQI_THRESHOLD:
                score += (score * indoor_ratio * 0.4)
            
            # Heat → prefer low intensity
            if self.weather.get("temperature", 0) > self.HEAT_THRESHOLD:
                if intensity < 5:
                    score += 15
                elif intensity > 7:
                    score -= 25
            
            # Low energy → prefer low intensity
            if self.user_energy < self.LOW_ENERGY_THRESHOLD:
                if intensity < 4:
                    score += 20
                elif intensity > 6:
                    score -= 30
            
            attr["score"] = max(0, score)
            fallback_scored.append(attr)
        
        return fallback_scored
    
    def _select_by_energy(self, ranked: List[Dict]) -> List[Dict]:
        """Select attractions within energy budget."""
        selected = []
        energy_used = 0
        
        for attr in ranked:
            cost = attr.get("energy_cost", 10)
            if energy_used + cost <= self.user_energy:
                selected.append(attr)
                energy_used += cost
        
        return selected
    
    def _generate_timeline(self, selected: List[Dict]) -> List[Dict]:
        """Generate hourly timeline starting at 9 AM."""
        timeline = []
        current_hour = 9
        
        for attr in selected:
            if current_hour > 20:  # Stop at 8 PM
                break
            
            timeline.append({
                "time": f"{current_hour:02d}:00",
                "attraction": attr.get("name", "Unknown"),
                "type": attr.get("type", ""),
                "indoor": attr.get("indoor", 0),
                "intensity": attr.get("physical_intensity", 5),
                "duration_mins": 60
            })
            current_hour += 1
            
            # Lunch break at noon
            if current_hour == 12:
                timeline.append({
                    "time": "12:00",
                    "attraction": "Lunch Break ☕",
                    "type": "break",
                    "duration_mins": 60
                })
                current_hour += 1
        
        return timeline

# Global instance
_engine = AdaptationEngine()

def adapt_itinerary(attractions: List[Dict], weather: Dict, aqi: Dict, 
                    crowd_level: int = 50, user_energy: int = 100,
                    heat_tolerance: float = 38.0, rain_tolerance: float = 0.6, aqi_tolerance: int = 150) -> Dict:
    """Convenience function with logging."""
    result = _engine.adapt(attractions, weather, aqi, crowd_level, user_energy, 
                           heat_tolerance, rain_tolerance, aqi_tolerance)
    logger.info(
        f"Adaptations - Weather: {weather['condition']}, AQI: {aqi['level']}, "
        f"Crowd: {crowd_level}%, Energy: {user_energy}%, "
        f"Selected: {len(result['selected'])}, Fallback: {result['fallback_active']}"
    )
    return result

