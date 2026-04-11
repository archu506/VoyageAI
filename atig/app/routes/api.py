"""
API Routes - REST Endpoints
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.crowd_model import CrowdPredictionModel
from app.services.route_optimizer import RouteOptimizer
from app.services.sustainability import SustainabilityCalculator
import json
import os

api_bp = Blueprint('api', __name__)

# Initialize services
_crowd_model = None
_route_optimizer = None
_sustainability_calc = None

def get_data_path():
    """Get path to data directory."""
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_path, 'data')

def get_crowd_model():
    """Lazy initialization of crowd model."""
    global _crowd_model
    if _crowd_model is None:
        data_path = get_data_path()
        footfall_file = os.path.join(data_path, 'footfall_history.json')
        attractions_file = os.path.join(data_path, 'jaipur_attractions.json')
        
        _crowd_model = CrowdPredictionModel(
            data_path=footfall_file if os.path.exists(footfall_file) else None
        )
        _crowd_model.train(attractions_file)
    
    return _crowd_model

def get_route_optimizer():
    """Lazy initialization of route optimizer."""
    global _route_optimizer
    if _route_optimizer is None:
        data_path = get_data_path()
        attractions_file = os.path.join(data_path, 'jaipur_attractions.json')
        _route_optimizer = RouteOptimizer(attractions_file)
    
    return _route_optimizer

def get_sustainability_calc():
    """Lazy initialization of sustainability calculator."""
    global _sustainability_calc
    if _sustainability_calc is None:
        data_path = get_data_path()
        attractions_file = os.path.join(data_path, 'jaipur_attractions.json')
        _sustainability_calc = SustainabilityCalculator(attractions_file)
    
    return _sustainability_calc

@api_bp.route('/attractions', methods=['GET'])
def get_attractions():
    """Get all attractions."""
    try:
        data_path = get_data_path()
        with open(os.path.join(data_path, 'jaipur_attractions.json'), 'r') as f:
            data = json.load(f)
        
        return jsonify({
            "success": True,
            "data": data['attractions'],
            "count": len(data['attractions'])
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/crowd-forecast', methods=['GET'])
def get_crowd_forecast():
    """Get 24-hour crowd forecast for all attractions."""
    try:
        hours = request.args.get('hours', 24, type=int)
        model = get_crowd_model()
        
        data_path = get_data_path()
        with open(os.path.join(data_path, 'jaipur_attractions.json'), 'r') as f:
            attractions_data = json.load(f)
        
        forecasts = []
        for attr in attractions_data['attractions']:
            forecast = model.predict_24h(attr['id'], hours)
            forecasts.append(forecast)
        
        # Get city-wide forecast
        city_forecast = model.get_city_forecast(hours)
        
        return jsonify({
            "success": True,
            "city_forecast": city_forecast,
            "attraction_forecasts": forecasts
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/optimize-itinerary', methods=['POST'])
def optimize_itinerary():
    """Optimize itinerary based on selected attractions."""
    try:
        data = request.get_json()
        selected_attractions = data.get('attractions', [])
        time_budget = data.get('time_budget_hours', 8)
        transport_mode = data.get('transport_mode', 'auto')
        
        if not selected_attractions:
            return jsonify({"success": False, "error": "No attractions selected"}), 400
        
        # Get crowd predictions
        crowd_model = get_crowd_model()
        data_path = get_data_path()
        with open(os.path.join(data_path, 'jaipur_attractions.json'), 'r') as f:
            attractions_data = json.load(f)
        
        crowd_predictions = {}
        for attr in attractions_data['attractions']:
            forecast = crowd_model.predict_24h(attr['id'], 24)
            if forecast['predictions']:
                # Get average crowd level for next 24h
                avg_footfall = sum(p['predicted_footfall'] for p in forecast['predictions']) / len(forecast['predictions'])
                baseline = attr['baseline_footfall']
                crowd_predictions[attr['id']] = crowd_model.get_crowd_level(int(avg_footfall), baseline)
        
        # Optimize route
        optimizer = get_route_optimizer()
        itinerary = optimizer.optimize_itinerary(
            selected_attractions,
            crowd_predictions,
            time_budget
        )
        
        # Calculate sustainability
        sustainability = get_sustainability_calc()
        eco_score = sustainability.calculate_sustainability_score(
            itinerary,
            crowd_predictions,
            transport_mode
        )
        
        return jsonify({
            "success": True,
            "itinerary": itinerary,
            "sustainability": eco_score,
            "crowd_predictions": crowd_predictions
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/attraction/<attr_id>/optimal-time', methods=['GET'])
def get_optimal_visit_time(attr_id):
    """Get optimal visit time for an attraction."""
    try:
        sustainability = get_sustainability_calc()
        optimal_time = sustainability.find_optimal_visit_time(attr_id)
        
        if not optimal_time:
            return jsonify({"success": False, "error": "Attraction not found"}), 404
        
        return jsonify({
            "success": True,
            "data": optimal_time
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/city-congestion', methods=['GET'])
def get_city_congestion():
    """Get city-wide congestion heatmap data."""
    try:
        model = get_crowd_model()
        city_forecast = model.get_city_forecast(24)
        
        data_path = get_data_path()
        with open(os.path.join(data_path, 'jaipur_attractions.json'), 'r') as f:
            attractions_data = json.load(f)
        
        # Create heatmap data
        heatmap_data = []
        for attr in attractions_data['attractions']:
            forecast = model.predict_24h(attr['id'], 24)
            if forecast['predictions']:
                avg_footfall = sum(p['predicted_footfall'] for p in forecast['predictions']) / len(forecast['predictions'])
                baseline = attr['baseline_footfall']
                congestion_ratio = avg_footfall / baseline if baseline > 0 else 0
                
                heatmap_data.append({
                    "id": attr['id'],
                    "name": attr['name'],
                    "latitude": attr['latitude'],
                    "longitude": attr['longitude'],
                    "congestion_ratio": round(congestion_ratio, 2),
                    "predicted_footfall": int(avg_footfall),
                    "baseline_footfall": baseline,
                    "category": attr['category']
                })
        
        return jsonify({
            "success": True,
            "heatmap_data": heatmap_data,
            "city": "Jaipur"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "ATIG API"
    })
