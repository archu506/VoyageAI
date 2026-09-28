"""
Itinerary planning routes blueprint.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.forms import ItineraryForm
from app.services import ItineraryService, WeatherService, CityService
from app.models import City

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

        return render_template(
            'itinerary/result.html',
            city_name=city_name,
            itinerary=crowd_results,
            weather=weather,
            num_days=days
        )
    
    return render_template('itinerary/plan.html', form=form)


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
