"""
Crowd Prediction Service
Uses Prophet time-series forecasting to predict visitor footfall
for attractions in Jaipur.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import os

# Try to import Prophet, fallback to linear regression if not available
try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False
    from sklearn.linear_model import LinearRegression

class CrowdPredictionModel:
    """
    Predicts crowd levels using time-series forecasting.
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the model with historical footfall data.
        
        Args:
            data_path: Path to footfall_history.json
        """
        self.data_path = data_path
        self.models = {}
        self.attraction_data = {}
        self._load_data()
    
    def _load_data(self):
        """Load historical footfall data."""
        if not self.data_path or not os.path.exists(self.data_path):
            # Use fallback data if file not found
            self.footfall_data = []
        else:
            with open(self.data_path, "r") as f:
                self.footfall_data = json.load(f)
    
    def _load_attractions(self, attractions_path: str):
        """Load attractions metadata."""
        with open(attractions_path, "r") as f:
            data = json.load(f)
            self.attraction_data = {a["id"]: a for a in data["attractions"]}
    
    def train(self, attractions_path: str = None):
        """
        Train prediction models for each attraction.
        """
        if attractions_path:
            self._load_attractions(attractions_path)
        
        if not self.footfall_data:
            print("No historical data available. Using fallback model.")
            return
        
        df = pd.DataFrame(self.footfall_data)
        df["ds"] = pd.to_datetime(df["timestamp"])
        df["y"] = df["footfall"].astype(float)
        
        # Group by attraction and train
        for attraction_id in df["attraction_id"].unique():
            attraction_data = df[df["attraction_id"] == attraction_id][["ds", "y"]].reset_index(drop=True)
            
            if len(attraction_data) < 10:
                print(f"Skipping {attraction_id} - insufficient data")
                continue
            
            try:
                if HAS_PROPHET:
                    model = Prophet(yearly_seasonality=False, daily_seasonality=True, interval_width=0.95)
                    model.fit(attraction_data)
                    self.models[attraction_id] = ("prophet", model)
                else:
                    # Fallback: simple regression on hour pattern
                    self.models[attraction_id] = ("fallback", None)
            except Exception as e:
                print(f"Error training {attraction_id}: {e}")
    
    def predict_24h(self, attraction_id: str, hours_ahead: int = 24) -> Dict:
        """
        Predict footfall for next 24 hours.
        
        Args:
            attraction_id: ID of attraction
            hours_ahead: Number of hours to forecast
        
        Returns:
            Dictionary with predictions and confidence intervals
        """
        if attraction_id not in self.models:
            return self._fallback_prediction(attraction_id, hours_ahead)
        
        model_type, model = self.models[attraction_id]
        
        if model_type == "prophet":
            return self._prophet_predict(attraction_id, model, hours_ahead)
        else:
            return self._fallback_prediction(attraction_id, hours_ahead)
    
    def _prophet_predict(self, attraction_id: str, model, hours_ahead: int) -> Dict:
        """Generate Prophet predictions."""
        future = model.make_future_dataframe(periods=hours_ahead, freq="H")
        forecast = model.predict(future)
        
        # Get last rows (next 24h)
        forecast = forecast.tail(hours_ahead)
        
        predictions = []
        for idx, row in forecast.iterrows():
            predictions.append({
                "timestamp": row["ds"].isoformat(),
                "predicted_footfall": max(0, int(row["yhat"])),
                "upper_bound": max(0, int(row["yhat_upper"])),
                "lower_bound": max(0, int(row["yhat_lower"])),
                "confidence": 0.95
            })
        
        return {
            "attraction_id": attraction_id,
            "predictions": predictions,
            "model_type": "prophet"
        }
    
    def _fallback_prediction(self, attraction_id: str, hours_ahead: int) -> Dict:
        """
        Fallback prediction using baseline + hour patterns.
        """
        if attraction_id not in self.attraction_data:
            # Default baseline
            baseline = 500
        else:
            baseline = self.attraction_data[attraction_id]["baseline_footfall"]
        
        predictions = []
        now = datetime.now()
        
        for i in range(hours_ahead):
            future_time = now + timedelta(hours=i)
            hour = future_time.hour
            
            # Hour-based pattern
            hour_multiplier = self._get_hour_multiplier(hour)
            predicted = int(baseline * hour_multiplier * np.random.uniform(0.85, 1.15))
            
            predictions.append({
                "timestamp": future_time.isoformat(),
                "predicted_footfall": max(0, predicted),
                "upper_bound": int(predicted * 1.25),
                "lower_bound": int(predicted * 0.75),
                "confidence": 0.75
            })
        
        return {
            "attraction_id": attraction_id,
            "predictions": predictions,
            "model_type": "fallback"
        }
    
    @staticmethod
    def _get_hour_multiplier(hour: int) -> float:
        """Get footfall multiplier for hour of day."""
        if 7 <= hour <= 9:
            return 1.3
        elif 9 <= hour <= 12:
            return 1.6
        elif 12 <= hour <= 13:
            return 0.8
        elif 13 <= hour <= 17:
            return 1.4
        elif 17 <= hour <= 20:
            return 1.2
        else:
            return 0.2
    
    def get_crowd_level(self, predicted_footfall: int, baseline: int) -> str:
        """
        Classify crowd level.
        """
        ratio = predicted_footfall / baseline if baseline > 0 else 1.0
        
        if ratio < 0.7:
            return "LOW"
        elif ratio < 1.0:
            return "MODERATE"
        elif ratio < 1.3:
            return "BUSY"
        else:
            return "CROWDED"
    
    def get_city_forecast(self, hours_ahead: int = 24) -> Dict:
        """
        Get aggregated city-wide congestion forecast.
        """
        city_data = []
        
        for attraction_id in self.attraction_data.keys():
            forecast = self.predict_24h(attraction_id, hours_ahead)
            
            # Aggregate per time slot
            for pred in forecast["predictions"]:
                city_data.append({
                    "timestamp": pred["timestamp"],
                    "attraction_id": attraction_id,
                    "footfall": pred["predicted_footfall"]
                })
        
        # Group by timestamp
        df = pd.DataFrame(city_data)
        if len(df) > 0:
            city_summary = df.groupby("timestamp")["footfall"].sum().reset_index()
            city_summary.rename(columns={"footfall": "total_city_footfall"}, inplace=True)
        else:
            city_summary = pd.DataFrame({"timestamp": [], "total_city_footfall": []})
        
        return {
            "city": "Jaipur",
            "forecast_hours": hours_ahead,
            "city_forecast": city_summary.to_dict("records")
        }
