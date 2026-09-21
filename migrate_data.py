import os
import json
from dotenv import load_dotenv
from flask import Flask
from database import db
from models.attraction import City, Attraction

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
database_url = os.getenv("DATABASE_URL")

if database_url:
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )
    database_uri = database_url
else:
    # Local development fallback
    instance_path = os.path.join(BASE_DIR, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    db_path = os.path.join(instance_path, 'travel.db')
    database_uri = f'sqlite:///{db_path}'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def migrate():
    with app.app_context():
        # Register all models before create_all
        from models.review import Review                    # noqa: F401
        from models.trip import SavedTrip                   # noqa: F401
        from models.user import User, PasswordResetToken    # noqa: F401
        db.create_all()

        try:
            with open(os.path.join(BASE_DIR, "attractions.json"), "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading attractions.json: {e}")
            return

        count = 0
        for city_name, info in data.items():
            city = City.query.filter_by(name=city_name).first()
            if not city:
                city = City(name=city_name, lat=info["lat"], lon=info["lon"])
                db.session.add(city)
                db.session.flush()  # get city.id before commit

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
        print(f"Migration complete: {count} attractions seeded into {database_uri}")
        
        # Print summary
        cities = City.query.all()
        print(f"Cities in DB: {[c.name for c in cities]}")

if __name__ == "__main__":
    migrate()
