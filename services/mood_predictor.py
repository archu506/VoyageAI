"""Rule-based mood prediction from user interactions and context."""

class MoodPredictor:
    """Predict user mood based on trip characteristics."""
    
    # Mood scores (0-100)
    MOODS = {
        "adventurous": 80,
        "relaxed": 50,
        "cultural": 60,
        "active": 85,
        "chill": 40
    }
    
    @staticmethod
    def predict_mood(weather, aqi, crowd_level, energy_level, attraction_types):
        """
        Predict mood based on conditions and user state.
        Returns: mood_str, mood_score (0-100)
        """
        score = 50  # Base neutral
        mood_factors = []
        
        # Weather impact
        if weather.get("rain_prob", 0) > 0.6:
            score -= 15
            mood_factors.append("rainy")
        elif weather.get("temperature", 25) > 35:
            score -= 10
            mood_factors.append("hot")
        elif weather.get("condition", "").lower() in ["clear", "sunny"]:
            score += 15
            mood_factors.append("sunny")
        
        # AQI impact
        aqi_level = aqi.get("level", "Fair")
        if aqi_level in ["Poor", "Very Poor"]:
            score -= 20
            mood_factors.append("polluted")
        elif aqi_level == "Good":
            score += 10
            mood_factors.append("clean_air")
        
        # Crowd impact
        if crowd_level > 80:
            score -= 15
            mood_factors.append("crowded")
        elif crowd_level < 30:
            score += 10
            mood_factors.append("peaceful")
        
        # Energy impact
        if energy_level > 80:
            score += 15
            mood_factors.append("energetic")
        elif energy_level < 30:
            score -= 20
            mood_factors.append("tired")
        
        # Attraction type impact
        if "adventure" in attraction_types:
            score += 20
            mood = "adventurous"
        elif "cultural" in attraction_types and crowd_level < 50:
            score += 10
            mood = "cultural"
        elif "beach" in attraction_types:
            score += 15
            mood = "relaxed"
        else:
            mood = "chill"
        
        # Final normalization
        final_score = max(0, min(100, score))
        
        return mood, final_score, mood_factors
    
    @staticmethod
    def get_mood_recommendation(mood, score):
        """Get recommendation based on predicted mood."""
        if mood == "adventurous" and score > 70:
            return "Ready for thrilling experiences! Consider hiking or adventure sports."
        elif mood == "relaxed" and score > 50:
            return "Perfect mood for beaches and leisure activities."
        elif mood == "cultural" and score > 50:
            return "Great for exploring museums and heritage sites."
        elif mood == "active" and score > 60:
            return "You're energized! Consider temple trails or sport activities."
        elif score < 40:
            return "Consider indoor activities or rest periods."
        else:
            return "You're in a balanced mood. Enjoy a mixed itinerary."

# Global instance
predictor = MoodPredictor()

def predict_mood(weather, aqi, crowd_level, energy_level, attraction_types):
    """Convenience function."""
    return predictor.predict_mood(weather, aqi, crowd_level, energy_level, attraction_types)

def get_recommendation(mood, score):
    """Get recommendation message."""
    return predictor.get_mood_recommendation(mood, score)
