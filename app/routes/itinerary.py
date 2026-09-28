"""
Itinerary planning routes blueprint.
"""

import json
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.forms import ItineraryForm
from app.services import ItineraryService, WeatherService, CityService
from app.models import db, City, SavedTrip

itinerary_bp = Blueprint('itinerary', __name__, url_prefix='/itinerary')


@itinerary_bp.route('/plan', methods=['GET', 'POST'])
def plan():
    """Generate travel itinerary for a city."""
    form = ItineraryForm()
    
    if form.validate_on_submit():
        city_name = form.city.data.strip().title()
        days = form.days.data
        
        # Check if city exists
        city = City.query.filter_by(name=city_name).first()
        if not city:
            flash(f'City "{form.city.data}" not found in our database.', 'warning')
            return redirect(url_for('itinerary.plan'))
        
        # Get weather
        weather = WeatherService.get_weather(city_name)
        
        # Generate itinerary
        itinerary = ItineraryService.generate_itinerary(city_name, days)

        if not itinerary:
            flash('Could not generate itinerary. Please try again.', 'danger')
            return redirect(url_for('itinerary.plan'))

        # Prepare crowd prediction
        from app.services.crowd_predictor import CrowdPredictor
        import datetime
        predictor = CrowdPredictor()

        now = datetime.datetime.now()
        hour = now.hour
        # Map hour to time_of_day
        if 5 <= hour < 12:
            time_of_day = 'morning'
        elif 12 <= hour < 17:
            time_of_day = 'afternoon'
        elif 17 <= hour < 21:
            time_of_day = 'evening'
        else:
            time_of_day = 'night'

        is_weekend = now.weekday() >= 5
        # Use weather.description to map to crowd predictor weather
        weather_map = {
            'clear': 'clear',
            'sunny': 'clear',
            'cloudy': 'cloudy',
            'rain': 'rainy',
            'rainy': 'rainy',
            'storm': 'stormy',
            'stormy': 'stormy'
        }
        weather_condition = weather_map.get(weather.description.lower(), 'clear') if weather else 'clear'

        # For each place, calculate crowd score
        crowd_results = {}
        for day, places in itinerary.items():
            crowd_results[day] = []
            for place in places:
                result = predictor.predict(time_of_day, is_weekend, weather_condition)
                suggestion = None
                if 'high' in result['crowd_level']:
                    # Find alternative nearby place (simple: pick next place in list not high crowd)
                    for alt in places:
                        if alt != place:
                            alt_result = predictor.predict(time_of_day, is_weekend, weather_condition)
                            if 'high' not in alt_result['crowd_level']:
                                suggestion = alt.name
                                break
                crowd_results[day].append({
                    'place': place,
                    'crowd_score': result['crowd_score'],
                    'crowd_level': result['crowd_level'],
                    'suggestion': suggestion
                })

        itinerary_summary = {
            day: [
                {
                    'place_name': item['place'].name,
                    'place_type': item['place'].place_type or 'Attraction',
                    'crowd_score': item['crowd_score'],
                    'crowd_level': item['crowd_level'],
                    'suggestion': item['suggestion']
                } for item in items
            ] for day, items in crowd_results.items()
        }
        itinerary_json = json.dumps(itinerary_summary)

        return render_template(
            'itinerary/result.html',
            city_name=city_name,
            itinerary=crowd_results,
            weather=weather,
            num_days=days,
            itinerary_json=itinerary_json
        )
    
    return render_template('itinerary/plan.html', form=form)


@itinerary_bp.route('/save', methods=['POST'])
@login_required
def save_trip():
    """Save generated itinerary for current authenticated user."""
    try:
        city_name = request.form.get('city_name', '').strip().title()
        num_days_raw = request.form.get('num_days', 1)
        itinerary_data_raw = request.form.get('itinerary_data', '').strip()

        if not city_name:
            flash('City name is required to save trip.', 'danger')
            return redirect(url_for('itinerary.plan'))

        try:
            num_days = int(num_days_raw)
            if num_days < 1 or num_days > 14:
                raise ValueError()
        except (ValueError, TypeError):
            flash('Invalid duration for trip.', 'danger')
            return redirect(url_for('itinerary.plan'))

        if not itinerary_data_raw or len(itinerary_data_raw) > 500000:
            flash('Invalid or oversized itinerary payload.', 'danger')
            return redirect(url_for('itinerary.plan'))

        try:
            parsed_data = json.loads(itinerary_data_raw)
            if not isinstance(parsed_data, (dict, list)):
                raise ValueError()
        except Exception:
            flash('Malformed itinerary data.', 'danger')
            return redirect(url_for('itinerary.plan'))

        saved_trip = SavedTrip(
            user_id=current_user.id,
            city_name=city_name,
            num_days=num_days,
            itinerary_data=json.dumps(parsed_data)
        )
        db.session.add(saved_trip)
        db.session.commit()

        flash(f'Trip to {city_name} saved successfully!', 'success')
        return redirect(url_for('auth.profile'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving trip: {str(e)}', 'danger')
        return redirect(url_for('itinerary.plan'))


@itinerary_bp.route('/city/<city_name>')
def city_details(city_name):
    """Show detailed information about a city and its attractions."""
    city_data = CityService.get_city_with_places(city_name)

    if not city_data:
        flash(f'City "{city_name}" not found.', 'warning')
        return redirect(url_for('main.index'))

    # Get weather
    weather = WeatherService.get_weather(city_name)

    return render_template(
        'itinerary/city_details.html',
        city=city_data,
        weather=weather
    )
