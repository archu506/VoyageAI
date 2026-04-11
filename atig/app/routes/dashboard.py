"""
Dashboard Routes - Government Analytics
"""

from flask import Blueprint, render_template, jsonify, request
from app.services.crowd_model import CrowdPredictionModel
import json
import os

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@dashboard_bp.route('/api/heatmap-data')
def get_heatmap_data():
    """Get heatmap data for map visualization."""
    try:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_path = os.path.join(base_path, 'data')
        
        # Load attractions
        with open(os.path.join(data_path, 'jaipur_attractions.json'), 'r') as f:
            attractions_data = json.load(f)
        
        # Initialize crowd model
        footfall_file = os.path.join(data_path, 'footfall_history.json')
        crowd_model = CrowdPredictionModel(
            data_path=footfall_file if os.path.exists(footfall_file) else None
        )
        crowd_model.train(os.path.join(data_path, 'jaipur_attractions.json'))
        
        # Generate heatmap
        heatmap_data = []
        max_congestion = 0
        
        for attr in attractions_data['attractions']:
            forecast = crowd_model.predict_24h(attr['id'], 24)
            if forecast['predictions']:
                avg_footfall = sum(p['predicted_footfall'] for p in forecast['predictions']) / len(forecast['predictions'])
                baseline = attr['baseline_footfall']
                congestion = (avg_footfall / baseline) if baseline > 0 else 0
                max_congestion = max(max_congestion, congestion)
                
                heatmap_data.append({
                    "lat": attr['latitude'],
                    "lng": attr['longitude'],
                    "intensity": congestion,
                    "name": attr['name'],
                    "footfall": int(avg_footfall),
                    "category": attr['category'],
                    "heritage_risk": attr.get('heritage_priority', 5) >= 8
                })
        
        return jsonify({
            "success": True,
            "heatmap": heatmap_data,
            "center": {
                "lat": 26.9124,
                "lng": 75.8131
            },
            "max_congestion": max_congestion
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@dashboard_bp.route('/api/analytics')
def get_analytics():
    """Get analytics data."""
    try:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_path = os.path.join(base_path, 'data')
        
        with open(os.path.join(data_path, 'jaipur_attractions.json'), 'r') as f:
            attractions_data = json.load(f)
        
        # Load footfall history if available
        footfall_file = os.path.join(data_path, 'footfall_history.json')
        historical_data = []
        
        if os.path.exists(footfall_file):
            with open(footfall_file, 'r') as f:
                historical_data = json.load(f)
        
        # Build analytics
        total_attractions = len(attractions_data['attractions'])
        heritage_sites = len([a for a in attractions_data['attractions'] 
                            if a.get('heritage_priority', 0) >= 8])
        
        daily_visitors = 0
        if historical_data:
            from datetime import datetime, timedelta
            today = datetime.now().date()
            today_data = [d for d in historical_data 
                         if d['timestamp'].startswith(str(today))]
            daily_visitors = sum(d['footfall'] for d in today_data)
        else:
            # Estimate
            daily_visitors = sum(a['baseline_footfall'] * 10 for a in attractions_data['attractions'])
        
        return jsonify({
            "success": True,
            "analytics": {
                "total_attractions": total_attractions,
                "heritage_sites": heritage_sites,
                "estimated_daily_visitors": daily_visitors,
                "avg_congestion": 0.6,
                "sustainability_index": 72
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
