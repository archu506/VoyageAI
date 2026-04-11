
from typing import Dict

class CrowdPredictor:
    """
    Predicts crowd levels based on time of day, weekend status, and weather.

    Methods
    -------
    predict(time_of_day: str, is_weekend: bool, weather: str) -> dict
        Returns a crowd score and level.
    """

    # Class-level constants for easy configuration
    TIME_SCORES = {
        'morning': 30,
        'afternoon': 60,
        'evening': 80,
        'night': 20
    }
    DEFAULT_TIME_SCORE = 40

    WEATHER_ADJUST = {
        'clear': 10,
        'cloudy': 0,
        'rainy': -20,
        'stormy': -30
    }

    def __init__(self):
        pass

    def predict(self, time_of_day: str, is_weekend: bool, weather: str) -> Dict[str, int | str]:
        """
        Predict crowd score and level.

        Parameters
        ----------
        time_of_day : str
            One of 'morning', 'afternoon', 'evening', 'night'.
        is_weekend : bool
            Whether it is a weekend.
        weather : str
            One of 'clear', 'cloudy', 'rainy', 'stormy'.

        Returns
        -------
        dict
            {'crowd_score': int, 'crowd_level': str}
        """
        score = self.TIME_SCORES.get(time_of_day, self.DEFAULT_TIME_SCORE)
        score += 20 if is_weekend else -10
        score += self.WEATHER_ADJUST.get(weather, 0)
        score = self._clamp_score(score)
        level = self._get_crowd_level(score)
        return {'crowd_score': score, 'crowd_level': level}

    @staticmethod
    def _clamp_score(score: int) -> int:
        """Clamp score to 0-100."""
        return max(0, min(100, score))

    @staticmethod
    def _get_crowd_level(score: int) -> str:
        """Return crowd level string based on score."""
        if score < 30:
            return 'low crowd'
        elif score < 70:
            return 'medium crowd'
        return 'high crowd'

if __name__ == "__main__":
    # Example usage
    predictor = CrowdPredictor()
    result = predictor.predict('afternoon', True, 'clear')
    print(result)
