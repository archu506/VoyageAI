"""Real-time weather monitoring with itinerary re-optimization."""

from datetime import datetime, timedelta
from .logger import logger

class WeatherMonitor:
    """Monitor weather changes and trigger re-optimization."""
    
    CHANGE_THRESHOLD = {
        "temp": 5,  # 5°C change
        "rain_prob": 0.3,  # 30% change
        "aqi": 50  # AQI value change
    }
    
    def __init__(self):
        self.last_weather = None
        self.last_aqi = None
        self.last_check = None
    
    def should_reoptimize(self, current_weather, current_aqi):
        """
        Check if weather changed significantly.
        Returns: (should_reoptimize, reason)
        """
        # First check
        if self.last_weather is None:
            self.last_weather = current_weather
            self.last_aqi = current_aqi
            self.last_check = datetime.now()
            return False, None
        
        # Check time (minimum 5 minutes between re-optimizations)
        time_diff = datetime.now() - self.last_check
        if time_diff < timedelta(minutes=5):
            return False, "Recent optimization"
        
        reasons = []
        
        # Temperature change
        temp_diff = abs(current_weather.get("temperature", 0) - 
                       self.last_weather.get("temperature", 0))
        if temp_diff > self.CHANGE_THRESHOLD["temp"]:
            reasons.append(f"Temperature changed {temp_diff:.1f}°C")
        
        # Rain probability change
        rain_diff = abs(current_weather.get("rain_prob", 0) - 
                       self.last_weather.get("rain_prob", 0))
        if rain_diff > self.CHANGE_THRESHOLD["rain_prob"]:
            reasons.append(f"Rain probability changed {rain_diff*100:.0f}%")
        
        # AQI change
        aqi_diff = abs(current_aqi.get("numeric_value", 0) - 
                      self.last_aqi.get("numeric_value", 0))
        if aqi_diff > self.CHANGE_THRESHOLD["aqi"]:
            reasons.append(f"AQI changed {aqi_diff:.0f} points")
        
        if reasons:
            self.last_weather = current_weather
            self.last_aqi = current_aqi
            self.last_check = datetime.now()
            reason = " | ".join(reasons)
            logger.info(f"Re-optimization triggered: {reason}")
            return True, reason
        
        return False, None
    
    def reset(self):
        """Reset monitor state."""
        self.last_weather = None
        self.last_aqi = None
        self.last_check = None

# Global instance
monitor = WeatherMonitor()

def should_reoptimize(current_weather, current_aqi):
    """Convenience function."""
    return monitor.should_reoptimize(current_weather, current_aqi)
