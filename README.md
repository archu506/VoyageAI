# Smart Tourism Planner - Production-Ready Flask Application

A modern, scalable Flask web application for intelligent travel planning with community-driven reviews and real-time weather integration.

## 🎯 Project Overview

Smart Tourism is a full-stack web application that helps travelers plan their perfect trips with:
- **AI-Powered Itineraries** - Generate optimized travel plans for any destination
- **Community Reviews** - Read and write honest reviews with star ratings
- **Real-Time Weather** - Check current conditions for your destination
- **User Authentication** - Create accounts and save your trips
- **Advanced Search** - Find destinations and attractions easily
- **Responsive Design** - Works seamlessly on desktop and mobile

## 🏗️ Architecture & Design Decisions

### Backend Architecture
- **Flask Application Factory Pattern** - Enables better testing and configuration management
- **SQLAlchemy ORM** - Type-safe database queries with automatic relationship management
- **Flask Blueprints** - Organized routes by domain (authentication, itinerary, reviews)
- **Service Layer** - Business logic separated from HTTP handlers
- **Form Validation** - Flask-WTF with built-in CSRF protection

### Database Design
```
Models:
├── User (Authentication)
│   ├── id (Primary Key)
│   ├── username (Unique)
│   ├── email (Unique)
│   ├── password_hash
│   └── reviews (Relationship)
│
├── City (Destinations)
│   ├── id (Primary Key)
│   ├── name (Unique, Indexed)
│   ├── description
│   ├── country
│   └── places (Relationship)
│
├── Place (Attractions)
│   ├── id (Primary Key)
│   ├── city_id (Foreign Key)
│   ├── name (Indexed)
│   ├── place_type (Indexed)
│   ├── description
│   └── reviews (Relationship)
│
└── Review (User Feedback)
    ├── id (Primary Key)
    ├── user_id (Foreign Key)
    ├── place_id (Foreign Key)
    ├── rating (1-5)
    ├── comment
    ├── created_at (Indexed)
    └── Unique Constraint: (user_id, place_id)
```

**Key Design Features:**
- Foreign key constraints with CASCADE delete
- Unique constraint preventing duplicate reviews by same user
- Indexes on frequently queried columns for performance
- Timestamps for created_at and updated_at tracking

### Frontend
- **Bootstrap 5** - Modern, responsive CSS framework
- **Server-Side Rendering** - Jinja2 templates for SEO-friendly pages
- **Form Validation** - Client and server-side validation
- **Interactive UI** - Star ratings, pagination, filtering

## 📁 Project Structure

```
smart_tourism/
├── app/
│   ├── __init__.py              # App factory & initialization
│   ├── models/
│   │   └── __init__.py          # SQLAlchemy models (User, City, Place, Review)
│   ├── forms/
│   │   └── __init__.py          # WTForms for validation
│   ├── services/
│   │   └── __init__.py          # Business logic (Weather, Itinerary, Reviews, Cities)
│   ├── routes/
│   │   ├── __init__.py          # Main blueprint (home, search, errors)
│   │   ├── auth.py              # Authentication routes
│   │   ├── itinerary.py         # Trip planning routes
│   │   └── reviews.py           # Review management routes
│   ├── templates/
│   │   ├── base.html            # Base template with navigation
│   │   ├── main/
│   │   │   ├── index.html       # Home page
│   │   │   ├── search.html      # Search results
│   │   │   ├── about.html       # About page
│   │   │   └── featured.html    # Featured destinations
│   │   ├── auth/
│   │   │   ├── login.html       # Login page
│   │   │   ├── register.html    # Registration page
│   │   │   └── profile.html     # User profile & reviews
│   │   ├── itinerary/
│   │   │   ├── plan.html        # Plan form
│   │   │   ├── result.html      # Itinerary display
│   │   │   └── city_details.html # City info
│   │   ├── reviews/
│   │   │   ├── place_reviews.html    # Reviews list
│   │   │   ├── add_review.html       # Add review form
│   │   │   └── edit_review.html      # Edit review form
│   │   ├── errors/
│   │   │   ├── 403.html         # Forbidden
│   │   │   ├── 404.html         # Not found
│   │   │   └── 500.html         # Server error
│   │   └── static/
│   │       ├── css/             # Custom styles
│   │       └── js/              # Custom scripts
│   └── data/
│       └── attractions.json     # Initial attractions data
├── config.py                    # Configuration (Dev, Test, Prod)
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── Dockerfile                   # Docker configuration
├── docker-compose.yml          # Docker Compose setup
└── README.md                    # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Git
- OpenWeatherMap API key (get free one at https://openweathermap.org/api)

### Installation

1. **Clone Repository**
```bash
git clone <repository-url>
cd smart_tourism
```

2. **Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup Environment Variables**
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your values
# - Set SECRET_KEY to a random string
# - Add your WEATHER_API_KEY from OpenWeatherMap
```

5. **Initialize Database**
```bash
python run.py
# This will create the database and load initial data from attractions.json
```

6. **Run Application**
```bash
python run.py
```

Visit `http://localhost:5000` in your browser.

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:5000
```

## 📚 Features & Usage

### 1. User Registration & Authentication
- Create account with username, email, and password
- Password hashing with Werkzeug security
- Session-based authentication with Flask-Login
- Profile page showing all user reviews

### 2. Trip Planning
- Search for supported destinations
- Generate optimized itineraries by number of days
- Automatic distribution of attractions across days
- Real-time weather for destination

### 3. Destination Browsing
- Browse all available cities
- View detailed city information
- See all attractions in each city
- Filter and search cities

### 4. Review System
- Write detailed reviews with 1-5 star ratings
- View all reviews for any attraction
- Edit or delete your own reviews
- Filter reviews by minimum rating
- Sort reviews by recency or rating
- Prevent duplicate reviews by same user
- Display average ratings and review counts

### 5. Search & Discovery
- Full-text search for cities
- Results pagination
- Quick access to view and plan trips

## 🔐 Security Features

- **CSRF Protection** - Flask-WTF CSRF tokens on all forms
- **Password Security** - Hashed with pbkdf2:sha256
- **SQL Injection Prevention** - SQLAlchemy parameterized queries
- **XSS Protection** - Jinja2 auto-escaping
- **Authentication Required** - Protected routes with @login_required
- **Authorization Checks** - Users can only edit/delete own reviews
- **Environment Secrets** - Sensitive data via .env file

## 🗄️ Database Queries

### Get Average Rating for a Place
```python
place = Place.query.get(place_id)
avg_rating = place.get_average_rating()  # Returns float 1-5
```

### Get All Reviews for a Place with Filtering
```python
from app.services import ReviewService

reviews_page = ReviewService.get_reviews_by_place(
    place_id=1,
    page=1,
    per_page=5,
    min_rating=4.0,
    sort_by='highest'
)
```

### Search Cities
```python
from app.services import CityService

results = CityService.search_cities(
    query='jaipur',
    page=1,
    per_page=10
)
```

## 🧪 Testing

```bash
# Run with testing configuration
export FLASK_ENV=testing
python run.py

# The app uses in-memory SQLite database for testing
```

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/logout` - Logout user
- `GET /auth/profile` - View user profile (protected)

### Itineraries
- `GET /itinerary/plan` - Plan form
- `POST /itinerary/plan` - Generate itinerary
- `GET /itinerary/city/<city_name>` - City details

### Reviews
- `GET /reviews/place/<place_id>` - View reviews
- `GET /reviews/place/<place_id>/add` - Add review form (protected)
- `POST /reviews/place/<place_id>/add` - Submit review (protected)
- `GET /reviews/<review_id>/edit` - Edit form (protected)
- `POST /reviews/<review_id>/edit` - Update review (protected)
- `POST /reviews/<review_id>/delete` - Delete review (protected)
- `GET /reviews/api/place/<place_id>/stats` - Review stats (JSON)

### Main
- `GET /` - Home page
- `GET /search` - Search page
- `POST /search` - Search results
- `GET /about` - About page

## 🛠️ Configuration

### Development vs Production

**Development** (FLASK_ENV=development)
- Debug mode enabled
- SQLAlchemy echo enabled
- Session cookies not secure

**Production** (FLASK_ENV=production)
- Debug mode disabled
- HTTPS required for session cookies
- Environment variables must be set
- Requires valid SECRET_KEY and WEATHER_API_KEY

See `config.py` for all configuration options.

## 📈 Performance Optimizations

- **Database Indexes** - On frequently queried columns
- **Lazy Loading** - Relationships use appropriate loading strategies
- **Query Optimization** - Join eager loading where needed
- **Pagination** - Limits result sets
- **Caching** - Could add Redis in production
- **CDN** - Bootstrap and Font Awesome from CDN

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database (loses all data)
rm instance/smart_tourism.db
python run.py
```

### Weather API Not Working
- Verify `WEATHER_API_KEY` in `.env`
- Check OpenWeatherMap API rate limits
- Look at application logs for errors

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 🚀 Deployment

### On Heroku
```bash
# Create Procfile
echo "web: gunicorn run:app" > Procfile

# Install Gunicorn
pip install gunicorn
pip freeze > requirements.txt

# Push to Heroku
git push heroku main
```

### On AWS/DigitalOcean
1. Use Docker container for deployment
2. Set environment variables in production
3. Use PostgreSQL instead of SQLite
4. Configure web server (nginx) with gunicorn
5. Set up SSL/HTTPS with Let's Encrypt

## 📝 Adding New Features

### Add a New Route
1. Create method in appropriate blueprint file
2. Add corresponding template in templates folder
3. Register blueprint in app factory if new blueprint

### Add a New Database Model
1. Define class in `app/models/__init__.py`
2. Add relationships to related models
3. Create migration or initialize with `db.create_all()`

### Add Form Validation
1. Create form class in `app/forms/__init__.py`
2. Use form in route with `form.validate_on_submit()`

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For issues, questions, or suggestions:
- Email: info@smarttourism.com
- Phone: +1 (555) 123-4567

## 🎓 Learning Resources

### Flask
- [Flask Official Documentation](https://flask.palletsprojects.com/)
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

### SQLAlchemy
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/index.html)

### Security
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)

---

**Built with ♥️ using Flask, SQLAlchemy, and Bootstrap**
