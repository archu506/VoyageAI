from database import db

class City(db.Model):
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    
    # Relationships
    attractions = db.relationship('Attraction', backref='city_ref', lazy=True, cascade='all, delete-orphan')

class Attraction(db.Model):
    __tablename__ = 'attractions'
    
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    indoor = db.Column(db.Float, default=0.0)
    physical_intensity = db.Column(db.Integer, default=5)
    best_time = db.Column(db.String(50))
    aqi_sensitive = db.Column(db.Boolean, default=True)
    weather_sensitive = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "indoor": self.indoor,
            "physical_intensity": self.physical_intensity,
            "best_time": self.best_time,
            "aqi_sensitive": self.aqi_sensitive,
            "weather_sensitive": self.weather_sensitive
        }
