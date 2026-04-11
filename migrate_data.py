import json
from flask import Flask
from database import db
from models.attraction import City, Attraction

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def migrate():
    with app.app_context():
        # Ensure our new tables exist
        db.create_all()
        
        # Open and ingest the static JSON file
        try:
            with open("attractions.json", "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading JSON: {e}")
            return
            
        count = 0
        for city_name, info in data.items():
            # Check or create City
            city = City.query.filter_by(name=city_name).first()
            if not city:
                city = City(name=city_name, lat=info["lat"], lon=info["lon"])
                db.session.add(city)
                db.session.commit()
            
            # Create Attractions linked to City
            for attr in info.get("attractions", []):
                existing = Attraction.query.filter_by(name=attr["name"], city_id=city.id).first()
                if not existing:
                    new_attr = Attraction(
                        city_id=city.id,
                        name=attr["name"],
                        type=attr["type"],
                        indoor=attr["indoor"],
                        physical_intensity=attr["physical_intensity"],
                        best_time=attr["best_time"],
                        aqi_sensitive=attr.get("aqi_sensitive", True),
                        weather_sensitive=attr.get("weather_sensitive", True)
                    )
                    db.session.add(new_attr)
                    count += 1
                    
        db.session.commit()
        print(f"Successfully migrated {count} attractions to the new SQL database!")

if __name__ == "__main__":
    migrate()
