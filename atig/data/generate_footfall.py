"""
Generate mock historical footfall data for Jaipur attractions.
Simulates 90 days of hourly footfall data with seasonal patterns.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_footfall_dataset(days=90, output_file="footfall_history.json"):
    """
    Generate synthetic footfall data with realistic patterns.
    """
    # Load attractions
    with open("jaipur_attractions.json", "r") as f:
        data = json.load(f)
    
    footfall_records = []
    
    # Generate data for past 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    for attraction in data["attractions"]:
        baseline = attraction["baseline_footfall"]
        congestion = attraction["congestion_factor"]
        
        current_date = start_date
        while current_date <= end_date:
            hour = current_date.hour
            day_of_week = current_date.weekday()
            
            # Weekend multiplier
            weekend_mult = 1.4 if day_of_week >= 5 else 1.0
            
            # Hour-based variation (peak hours get more visitors)
            hour_mult = 1.0
            if "09" in attraction["peak_hours"] or "10" in attraction["peak_hours"]:
                if 9 <= hour <= 10:
                    hour_mult = 1.8
            if "14" in attraction["peak_hours"] or "15" in attraction["peak_hours"]:
                if 14 <= hour <= 16:
                    hour_mult = 1.6
            if "08" in attraction["peak_hours"]:
                if 8 <= hour <= 9:
                    hour_mult = 1.5
            if "17" in attraction["peak_hours"] or "18" in attraction["peak_hours"]:
                if 17 <= hour <= 19:
                    hour_mult = 1.4
            
            # Morning/evening trends
            if 7 <= hour <= 9:
                hour_mult = max(hour_mult, 1.3)
            elif 18 <= hour <= 20:
                hour_mult = max(hour_mult, 1.2)
            elif hour < 7 or hour > 20:
                hour_mult = 0.1
            elif 11 <= hour <= 13:
                hour_mult = 0.8  # Lunch time dip
            
            # Add random noise
            noise = np.random.normal(1.0, 0.15)
            
            footfall = int(baseline * congestion * weekend_mult * hour_mult * noise)
            footfall = max(0, footfall)
            
            record = {
                "timestamp": current_date.isoformat(),
                "attraction_id": attraction["id"],
                "attraction_name": attraction["name"],
                "footfall": footfall,
                "hour": hour,
                "day_of_week": day_of_week,
                "is_weekend": day_of_week >= 5
            }
            
            footfall_records.append(record)
            current_date += timedelta(hours=1)
    
    # Save to JSON
    output_path = os.path.join(os.path.dirname(__file__), output_file)
    with open(output_path, "w") as f:
        json.dump(footfall_records, f, indent=2)
    
    print(f"Generated {len(footfall_records)} footfall records")
    print(f"Saved to {output_path}")
    
    return footfall_records

if __name__ == "__main__":
    generate_footfall_dataset()
