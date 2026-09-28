import json
import re
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database import db
from models.trip import SavedTrip
from services.logger import logger

itineraries_bp = Blueprint('itineraries', __name__, url_prefix='/api/itinerary')

def extract_plan_summary(itinerary_html):
    """Extract summary information from itinerary HTML"""
    summary = {
        'city': '',
        'attractions': 0,
        'energy_used': 0,
        'total_energy': 100,
        'weather': '',
    }
    
    try:
        city_match = re.search(r'<div class="weather-city">([^<]+)</div>', itinerary_html)
        if city_match: summary['city'] = city_match.group(1).strip()
        
        attractions_match = re.search(r'Attractions Selected[:\s]*</strong>\s*(\d+)', itinerary_html)
        if attractions_match: summary['attractions'] = int(attractions_match.group(1))
        
        energy_match = re.search(r'Energy Used[:\s]*</strong>\s*(\d+)/(\d+)', itinerary_html)
        if energy_match:
            summary['energy_used'] = int(energy_match.group(1))
            summary['total_energy'] = int(energy_match.group(2))
        
        weather_match = re.search(r'<div class="weather-condition">([^<]+)</div>', itinerary_html)
        if weather_match: summary['weather'] = weather_match.group(1).strip()
    except Exception as e:
        logger.error(f"Error extracting plan summary: {str(e)}")
    
    return summary

@itineraries_bp.route('/save', methods=['POST'])
@login_required
def save_itinerary():
    """Save itinerary to SQLite database"""
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({'success': False, 'error': 'Invalid or malformed JSON'}), 400
    itinerary = data.get('itinerary')
    plan_name = data.get('planName', None)

    if not itinerary:
        return jsonify({'success': False, 'error': 'Missing itinerary'}), 400

    try:
        summary = extract_plan_summary(itinerary)

        if not plan_name:
            trip_count = SavedTrip.query.filter_by(user_id=current_user.id).count()
            plan_name = f"Trip #{trip_count + 1}"

        new_trip = SavedTrip(
            user_id=current_user.id,
            name=plan_name,
            city=summary.get('city', ''),
            itinerary_html=itinerary,
            summary=json.dumps(summary)
        )

        db.session.add(new_trip)
        db.session.commit()

        return jsonify({
            'success': True, 
            'message': f'✓ Itinerary "{plan_name}" saved successfully!',
            'plan_id': new_trip.id
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving itinerary: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal Server Error'}), 500

@itineraries_bp.route('/get', methods=['GET'])
@login_required
def get_itinerary():
    """Retrieve itinerary from database"""
    plan_id = request.args.get('planId', None)

    try:
        if plan_id:
            plan = SavedTrip.query.filter_by(id=plan_id, user_id=current_user.id).first()
            if plan:
                return jsonify({'success': True, 'plan': plan.to_dict()})
            return jsonify({'success': False, 'error': 'Plan not found'}), 404

        latest_plan = SavedTrip.query.filter_by(user_id=current_user.id).order_by(SavedTrip.id.desc()).first()
        if latest_plan:
            return jsonify({'success': True, 'itinerary': latest_plan.itinerary_html})

        return jsonify({'success': False, 'error': 'No saved plans found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal Server Error'}), 500

@itineraries_bp.route('/list', methods=['GET'])
@login_required
def list_saved_plans():
    """List all saved plans for a user"""
    try:
        plans = SavedTrip.query.filter_by(user_id=current_user.id).order_by(SavedTrip.id.desc()).all()
        plan_list = [p.to_dict() for p in plans]
        return jsonify({'success': True, 'plans': plan_list})
    except Exception as e:
        return jsonify({'success': False, 'error': 'Internal Server Error'}), 500

@itineraries_bp.route('/delete', methods=['DELETE'])
@login_required
def delete_plan():
    """Delete a specific saved plan"""
    plan_id = request.args.get('planId', None)

    if not plan_id:
        return jsonify({'success': False, 'error': 'Plan ID is required'}), 400

    try:
        plan = SavedTrip.query.filter_by(id=plan_id, user_id=current_user.id).first()
        if not plan:
            return jsonify({'success': False, 'error': 'Plan not found'}), 404

        db.session.delete(plan)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Plan deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Internal Server Error'}), 500
