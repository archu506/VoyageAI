#!/usr/bin/env python
"""Initialize the database with seed data for testing."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, City, Attraction, Review

def init_db():
    """Initialize database with seed data."""
    app = create_app('development')
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print('✓ Database tables created')
        
        # Clear existing data
        db.session.query(Review).delete()
        db.session.query(Attraction).delete()
        db.session.query(City).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        # Create test cities
        cities = [
            City(name='Paris', country='France', latitude=48.8566, longitude=2.3522),
            City(name='Tokyo', country='Japan', latitude=35.6762, longitude=139.6503),
            City(name='New York', country='USA', latitude=40.7128, longitude=-74.0060),
            City(name='Barcelona', country='Spain', latitude=41.3851, longitude=2.1734),
            City(name='Amsterdam', country='Netherlands', latitude=52.3676, longitude=4.9041),
        ]
        for city in cities:
            db.session.add(city)
        db.session.commit()
        print('✓ Created 5 test cities')
        
        # Create test attractions
        attractions = [
            Attraction(name='Eiffel Tower', description='Iconic iron lattice tower in Paris', category='Landmark', city_id=cities[0].id),
            Attraction(name='Louvre Museum', description='Famous art museum with the Mona Lisa', category='Museum', city_id=cities[0].id),
            Attraction(name='Arc de Triomphe', description='Monument and iconic symbol', category='Landmark', city_id=cities[0].id),
            
            Attraction(name='Sensoji Temple', description='Ancient Buddhist temple', category='Temple', city_id=cities[1].id),
            Attraction(name='Tokyo Tower', description='Communications and observation tower', category='Landmark', city_id=cities[1].id),
            
            Attraction(name='Statue of Liberty', description='Colossal neoclassical sculpture', category='Landmark', city_id=cities[2].id),
            Attraction(name='Central Park', description='Urban park with beautiful scenery', category='Park', city_id=cities[2].id),
            
            Attraction(name='Sagrada Familia', description='Basilica under construction since 1883', category='Temple', city_id=cities[3].id),
            
            Attraction(name='Anne Frank House', description='Museum dedicated to Holocaust victim', category='Museum', city_id=cities[4].id),
        ]
        for attr in attractions:
            db.session.add(attr)
        db.session.commit()
        print('✓ Created 9 test attractions')
        
        # Create test users
        users = [
            User(username='alice', email='alice@example.com', password='password123'),
            User(username='bob', email='bob@example.com', password='password123'),
            User(username='testuser', email='test@example.com', password='testpass123'),
        ]
        for user in users:
            db.session.add(user)
        db.session.commit()
        print('✓ Created 3 test users')
        
        # Create test reviews
        reviews_data = [
            (users[0], attractions[0], 'Incredible Experience!', 5.0, 'The Eiffel Tower is absolutely stunning! Worth every effort to climb to the top.'),
            (users[0], attractions[1], 'Masterpiece Collection', 4.5, 'The Louvre has an amazing collection of art from different periods.'),
            (users[1], attractions[3], 'Peaceful Atmosphere', 4.0, 'Sensoji Temple is a serene and beautiful place to visit.'),
            (users[1], attractions[5], 'Iconic and Must-See', 4.5, 'The Statue of Liberty is an iconic monument that all visitors should see.'),
            (users[2], attractions[6], 'Nature in the City', 4.0, 'Central Park is a wonderful escape from the bustling city.'),
        ]
        for user, attraction, title, rating, comment in reviews_data:
            review = Review(
                title=title,
                rating=rating,
                comment=comment,
                user_id=user.id,
                attraction_id=attraction.id
            )
            db.session.add(review)
        db.session.commit()
        print('✓ Created 5 test reviews')
        
        print(f'\n✓✓✓ Database initialized successfully ✓✓✓')
        print(f'Database: {os.path.abspath("travelplanner.db")}')
        print(f'Users: 3 (alice, bob, testuser)')
        print(f'Cities: 5')
        print(f'Attractions: 9')
        print(f'Reviews: 5')

if __name__ == '__main__':
    init_db()
