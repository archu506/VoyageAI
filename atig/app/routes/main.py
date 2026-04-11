"""
Main Routes - Web Interface
"""

from flask import Blueprint, render_template, request, jsonify
import json
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage."""
    return render_template('index.html')

@main_bp.route('/plan', methods=['GET', 'POST'])
def plan_itinerary():
    """Itinerary planner page."""
    return render_template('plan.html')

@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@main_bp.route('/attractions')
def attractions_list():
    """List all attractions."""
    try:
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data',
            'jaipur_attractions.json'
        )
        
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        return render_template('attractions.html', attractions=data['attractions'])
    except Exception as e:
        return render_template('error.html', error=str(e)), 500
