import json
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from database import get_reviews_by_city, add_review
from services.weather_service import get_weather
from services.aqi_service import get_aqi
from services.weather_monitor import should_reoptimize
from services.adaptation_engine import adapt_itinerary
from services.mood_predictor import predict_mood, get_recommendation
from services.logger import logger

planner_bp = Blueprint('planner', __name__)

from models.attraction import City, Attraction

@planner_bp.route("/plan", methods=["POST"])
@login_required
def plan():
    try:
        city = request.form["city"].strip().title()
        days = int(request.form.get("days", 1))
        crowd_level = int(request.form.get("crowd_level", 50))
        user_energy = int(request.form.get("energy", 100))
        
        logger.info(f"Plan request: {city}, {days} days, crowd={crowd_level}%, energy={user_energy}%")
        
        city_obj = City.query.filter_by(name=city).first()
        if not city_obj:
            logger.warning(f"City not found: {city}")
            return render_template(
                "result.html",
                error="City not found in database",
                city=city,
                reviews={}
            )
        
        attractions_records = Attraction.query.filter_by(city_id=city_obj.id).all()
        attractions = [a.to_dict() for a in attractions_records]
        
        weather = get_weather(city)
        aqi = get_aqi(city_obj.lat, city_obj.lon, city)
        
        logger.info(f"Conditions: {weather['condition']}, AQI {aqi['level']}, {crowd_level}% crowds")
        
        reoptimize, reason = should_reoptimize(weather, aqi)
        if reoptimize:
            logger.info(f"Re-optimization triggered: {reason}")
            flash(f"Weather update: {reason}", "info")
        
        # User defined thresholds overrides
        heat_tol = 38.0
        rain_tol = 0.6
        aqi_tol = 150
        
        if current_user.is_authenticated:
            if current_user.heat_tolerance is not None: heat_tol = current_user.heat_tolerance
            if current_user.rain_tolerance is not None: rain_tol = current_user.rain_tolerance
            if current_user.aqi_tolerance is not None: aqi_tol = current_user.aqi_tolerance
            
        adaptation = adapt_itinerary(attractions, weather, aqi, crowd_level, user_energy,
                                     heat_tolerance=heat_tol, rain_tolerance=rain_tol, aqi_tolerance=aqi_tol)
        
        attraction_types = [a.get("type", "") for a in attractions[:5]]
        mood, mood_score, mood_factors = predict_mood(weather, aqi, crowd_level, user_energy, attraction_types)
        mood_recommendation = get_recommendation(mood, mood_score)
        
        reviews = get_reviews_by_city(city)
        
        logger.info(f"Adaptation complete: {len(adaptation['selected'])} attractions selected, mood={mood}")
        
        if current_user.is_authenticated:
            selected_names = [a["name"] for a in adaptation["selected"]]
            current_user.save_trip(city, selected_names, mood)
        
        return render_template(
            "result.html",
            city=city,
            weather=weather,
            aqi=aqi,
            adaptation=adaptation,
            reviews=reviews,
            days=days,
            mood=mood,
            mood_score=mood_score,
            mood_recommendation=mood_recommendation
        )
    except Exception as e:
        logger.error(f"Plan error: {str(e)}", exc_info=True)
        return render_template(
            "result.html",
            error=f"Error: {str(e)}",
            city="",
            reviews={}
        )

@planner_bp.route("/add_review", methods=["POST"])
def submit_review():
    city = request.form["city"].strip().title()
    place = request.form["place"].strip().title()
    user_name = request.form["user_name"]
    rating = request.form["rating"]
    comment = request.form["comment"]
    print("Saving review:", city, place, user_name, rating, comment)
    add_review(city, place, user_name, rating, comment)
    return redirect(url_for("planner.reload_plan", city=city))

@planner_bp.route("/reload_plan/<city>")
def reload_plan(city):
    try:
        city = city.title()
        logger.info(f"Reloading plan for: {city}")
        
        city_obj = City.query.filter_by(name=city).first()
        if not city_obj:
            return redirect(url_for("home"))
        
        attractions_records = Attraction.query.filter_by(city_id=city_obj.id).all()
        attractions = [a.to_dict() for a in attractions_records]
        
        weather = get_weather(city)
        aqi = get_aqi(city_obj.lat, city_obj.lon, city)
        
        heat_tol = 38.0
        rain_tol = 0.6
        aqi_tol = 150
        
        if current_user.is_authenticated:
            if current_user.heat_tolerance is not None: heat_tol = current_user.heat_tolerance
            if current_user.rain_tolerance is not None: rain_tol = current_user.rain_tolerance
            if current_user.aqi_tolerance is not None: aqi_tol = current_user.aqi_tolerance
            
        adaptation = adapt_itinerary(attractions, weather, aqi, 50, 100,
                                     heat_tolerance=heat_tol, rain_tolerance=rain_tol, aqi_tolerance=aqi_tol)
        reviews = get_reviews_by_city(city)
        
        logger.info(f"Reload complete: {len(adaptation['selected'])} attractions")
        
        return render_template(
            "result.html",
            city=city,
            weather=weather,
            aqi=aqi,
            adaptation=adaptation,
            reviews=reviews,
            days=1
        )
    except Exception as e:
        logger.error(f"Reload error: {str(e)}", exc_info=True)
        return render_template(
            "result.html",
            error=f"Error reloading plan: {str(e)}",
            city=city,
            reviews={}
        )
