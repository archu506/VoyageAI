"""
Sustainability Scoring Service
Calculates eco-impact and suggests optimal visit times.
"""

import json
from typing import Dict, List
import math

class SustainabilityCalculator:
    """
    Calculates sustainability scores for tourism activities.
    """
    
    def __init__(self, attractions_path: str = None):
        """
        Initialize calculator.
        
        Args:
            attractions_path: Path to jaipur_attractions.json
        """
        self.attractions = {}
        self.carbon_factors = {
            "car": 0.21,  # kg CO2 per km
            "auto": 0.12,  # Tuk-tuk
            "bus": 0.05,   # Public transport
            "bike": 0.0    # Cycle
        }
        
        if attractions_path:
            with open(attractions_path, "r") as f:
                data = json.load(f)
                self.attractions = {a["id"]: a for a in data["attractions"]}
    
    def calculate_carbon_footprint(self, 
                                   itinerary: Dict,
                                   transport_mode: str = "auto") -> float:
        """
        Calculate carbon emissions for a journey.
        
        Args:
            itinerary: Dict with route information
            transport_mode: "car", "auto", "bus", or "bike"
        
        Returns:
            Total CO2 in kg
        """
        distance = itinerary.get("total_distance_km", 0)
        carbon_factor = self.carbon_factors.get(transport_mode, 0.12)
        
        # Double distance (there and back)
        total_emissions = distance * 2 * carbon_factor
        
        return round(total_emissions, 2)
    
    def calculate_crowd_impact(self, 
                              itinerary: Dict,
                              crowd_predictions: Dict) -> float:
        """
        Calculate environmental impact from overcrowding.
        
        Factors:
        - Infrastructure strain
        - Waste generation
        - Energy consumption
        
        Score: 0-100 (lower = better)
        """
        impact = 0
        
        for attraction in itinerary.get("attractions", []):
            attr_id = attraction["id"]
            
            if attr_id not in self.attractions:
                continue
            
            attr_data = self.attractions[attr_id]
            eco_impact_factor = {"low": 1, "medium": 2, "high": 3}.get(
                attr_data.get("eco_impact", "medium"), 2
            )
            
            # Get predicted crowd level
            crowd_level = crowd_predictions.get(attr_id, "MODERATE")
            crowd_multiplier = {
                "LOW": 0.5,
                "MODERATE": 1.0,
                "BUSY": 1.5,
                "CROWDED": 2.0
            }.get(crowd_level, 1.0)
            
            # Calculate impact
            visit_hours = attraction.get("visit_duration_hours", 1)
            site_impact = eco_impact_factor * crowd_multiplier * visit_hours
            
            impact += site_impact
        
        # Normalize to 0-100 scale
        normalized_impact = min(100, impact * 5)
        
        return round(normalized_impact, 1)
    
    def calculate_sustainability_score(self,
                                      itinerary: Dict,
                                      crowd_predictions: Dict,
                                      transport_mode: str = "auto") -> Dict:
        """
        Calculate overall sustainability score.
        
        Factors:
        - Carbon emissions (30%)
        - Overcrowding impact (40%)
        - Heritage preservation (20%)
        - Time efficiency (10%)
        """
        # Carbon score (inverse: lower emissions = higher score)
        carbon_emissions = self.calculate_carbon_footprint(itinerary, transport_mode)
        # Max reasonable emission: 50kg CO2
        carbon_score = max(0, 100 - (carbon_emissions / 50 * 100))
        
        # Crowd impact (inverse of impact score)
        crowd_impact = self.calculate_crowd_impact(itinerary, crowd_predictions)
        crowd_score = 100 - crowd_impact
        
        # Heritage preservation (based on selected attractions)
        heritage_score = self._calculate_heritage_score(itinerary)
        
        # Time efficiency (balanced pace)
        time_score = self._calculate_time_efficiency(itinerary)
        
        # Weighted average
        overall_score = (
            carbon_score * 0.30 +
            crowd_score * 0.40 +
            heritage_score * 0.20 +
            time_score * 0.10
        )
        
        return {
            "overall_score": round(overall_score, 1),
            "carbon_score": round(carbon_score, 1),
            "crowd_impact_score": round(crowd_score, 1),
            "heritage_score": round(heritage_score, 1),
            "time_efficiency_score": round(time_score, 1),
            "carbon_emissions_kg": carbon_emissions,
            "transport_mode": transport_mode,
            "recommendations": self._generate_recommendations(
                overall_score, carbon_emissions, crowd_impact, itinerary
            )
        }
    
    def _calculate_heritage_score(self, itinerary: Dict) -> float:
        """Calculate heritage preservation score."""
        if not itinerary.get("attractions"):
            return 0
        
        total_priority = 0
        count = 0
        
        for attraction in itinerary["attractions"]:
            attr_id = attraction["id"]
            if attr_id in self.attractions:
                priority = self.attractions[attr_id].get("heritage_priority", 5)
                total_priority += priority
                count += 1
        
        if count == 0:
            return 50
        
        # Normalize: 0-10 -> 0-100
        avg_priority = total_priority / count
        heritage_score = (avg_priority / 10) * 100
        
        return min(100, round(heritage_score, 1))
    
    def _calculate_time_efficiency(self, itinerary: Dict) -> float:
        """
        Score based on balanced time allocation.
        Avoids rushing through sites.
        """
        attractions = itinerary.get("attractions", [])
        
        if not attractions:
            return 50
        
        # Ideal visit time per site: 1.5 hours
        ideal_time = 1.5
        
        time_differences = []
        for attraction in attractions:
            visit_time = attraction.get("visit_duration_hours", 1)
            diff = abs(visit_time - ideal_time)
            time_differences.append(diff)
        
        avg_difference = sum(time_differences) / len(time_differences)
        
        # Less difference = higher score
        efficiency_score = 100 - (avg_difference / ideal_time * 100)
        
        return max(0, round(efficiency_score, 1))
    
    def _generate_recommendations(self, 
                                 overall_score: float,
                                 carbon_emissions: float,
                                 crowd_impact: float,
                                 itinerary: Dict) -> List[str]:
        """Generate sustainability recommendations."""
        recommendations = []
        
        # Carbon recommendations
        if carbon_emissions > 30:
            recommendations.append("🚌 Consider public transport or cycling to reduce CO2")
        
        # Crowd recommendations
        if crowd_impact > 60:
            recommendations.append("⏰ Visit attractions during off-peak hours (11:30-13:30 or after 19:00)")
        
        # Heritage recommendations
        heritage_count = len([a for a in itinerary.get("attractions", []) 
                            if self.attractions.get(a["id"], {}).get("heritage_priority", 0) >= 8])
        if heritage_count < len(itinerary.get("attractions", [])) * 0.5:
            recommendations.append("🏛️ Include more UNESCO/heritage sites for cultural preservation")
        
        # Time efficiency
        long_gaps = [a for a in itinerary.get("attractions", []) 
                    if a.get("visit_duration_hours", 0) > 2.5]
        if long_gaps:
            recommendations.append("⏱️ Break up long visits with shorter, more frequent stops")
        
        if overall_score >= 80:
            recommendations.append("✅ Excellent sustainability! You're a responsible tourist")
        elif overall_score >= 60:
            recommendations.append("👍 Good effort. Small changes can maximize your impact")
        
        return recommendations
    
    def find_optimal_visit_time(self, attraction_id: str, hours: int = 24) -> Dict:
        """
        Find optimal time to visit based on crowds and eco-impact.
        
        Returns:
            Best visit time window with sustainability score
        """
        if attraction_id not in self.attractions:
            return {}
        
        attr_data = self.attractions[attraction_id]
        peak_hours = attr_data.get("peak_hours", "10-12, 14-16")
        
        optimal_windows = []
        
        # Morning (least crowded typically)
        optimal_windows.append({
            "window": "06:00-08:00",
            "eco_score": 95,
            "reasons": ["Lowest crowds", "Fresh air", "Better photography"]
        })
        
        # Late evening (second best)
        optimal_windows.append({
            "window": "18:00-20:00",
            "eco_score": 90,
            "reasons": ["Moderate crowds", "Golden hour light", "Sunset views"]
        })
        
        # Avoid peak
        optimal_windows.append({
            "window": "12:00-13:00",
            "eco_score": 40,
            "reasons": ["Lunch time (avoid completely)", "Midday heat", "High congestion risk"]
        })
        
        return {
            "attraction_id": attraction_id,
            "attraction_name": attr_data["name"],
            "optimal_visit_windows": optimal_windows,
            "peak_hours_to_avoid": peak_hours
        }
