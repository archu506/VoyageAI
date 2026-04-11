from database import db
from datetime import datetime
import json

class SavedTrip(db.Model):
    __tablename__ = 'saved_trips'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255))
    city = db.Column(db.String(100))
    attractions = db.Column(db.Text)
    mood = db.Column(db.String(100))
    itinerary_html = db.Column(db.Text)
    summary = db.Column(db.Text)
    created_at = db.Column(db.String(100), default=lambda: datetime.now().isoformat())
    saved_date = db.Column(db.String(100), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'))

    def to_dict(self):
        summary_dict = {}
        try:
            summary_dict = json.loads(self.summary) if self.summary else {}
        except:
            pass
            
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'mood': self.mood,
            'itinerary': self.itinerary_html,
            'saved_at': self.created_at,
            'saved_date': self.saved_date,
            'summary': summary_dict
        }
