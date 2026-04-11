# Travel Planner Application

A production-grade full-stack travel planning web application built with Flask, SQLAlchemy, and PostgreSQL. Features comprehensive attraction browsing, user reviews, weather integration, and a secure authentication system.

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Prerequisites](#prerequisites)
5. [Quick Start](#quick-start)
6. [Development Setup](#development-setup)
7. [Database Management](#database-management)
8. [API Documentation](#api-documentation)
9. [Deployment](#deployment)
10. [Security](#security)
11. [Troubleshooting](#troubleshooting)

## Features

### Core Functionality
- **User Authentication**: Secure registration and login with password hashing (PBKDF2-SHA256)
- **Attraction Browsing**: Browse attractions by city with detailed information
- **Reviews System**: Post, edit, and delete reviews with 1-5 star ratings
- **Search Functionality**: Full-text search for cities and attractions
- **Weather Integration**: Real-time weather data from OpenWeatherMap API
- **User Profiles**: View personal review history and manage preferences

### Security Features
- CSRF protection on all forms
- SQL injection prevention via SQLAlchemy ORM
- Password hashing with industry-standard algorithms
- Input validation and sanitization
- Secure session management with HTTP-only cookies
- Environment-based configuration with secret management

### Enterprise Features
- Production-ready logging with rotating file handlers
- Health check endpoints for monitoring
- Pagination for large datasets
- RESTful API endpoints for JSON responses
- Docker containerization for easy deployment
- Database migrations with Flask-Migrate
- Comprehensive error handling

## Architecture

### Layered Architecture
```
┌─────────────────────────────────┐
│       Templates (Jinja2)        │
├─────────────────────────────────┤
│     Routes (Blueprints)         │
├─────────────────────────────────┤
│    Services (Business Logic)    │
├─────────────────────────────────┤
│  Models (SQLAlchemy ORM)        │
├─────────────────────────────────┤
│    Database (PostgreSQL)        │
└─────────────────────────────────┘
```

### Directory Structure
```
travelplanner/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models/              # SQLAlchemy models
│   ├── forms/               # WTForms validation forms
│   ├── services/            # Business logic layer
│   ├── routes/              # Flask blueprints
│   ├── templates/           # Jinja2 templates
│   ├── static/              # CSS, JavaScript, images
│   ├── config.py            # Configuration management
│   └── extensions.py        # Flask extension initialization
├── migrations/              # Database migration files
├── tests/                   # Test suite
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Container definition
├── wsgi.py                  # WSGI entry point
└── run.py                   # Development server
```

## Tech Stack

### Backend
- **Python 3.12**: Latest stable Python release
- **Flask 3.0**: Lightweight web framework
- **SQLAlchemy 2.0**: ORM for database operations
- **PostgreSQL 16**: Production-grade relational database
- **Gunicorn**: Production WSGI server

### Frontend
- **Jinja2**: Template engine
- **Bootstrap 5**: CSS framework
- **jQuery**: JavaScript library
- **Fetch API**: Client-side HTTP requests

### DevOps
- **Docker**: Container platform
- **Docker Compose**: Multi-container orchestration
- **Flask-Migrate**: Database schema management

### Security
- **Flask-WTF**: CSRF protection
- **Werkzeug**: Password hashing
- **Flask-Login**: Session management
- **SQLAlchemy**: SQL injection prevention

## Prerequisites

### System Requirements
- Python 3.12 or higher
- PostgreSQL 14 or higher
- Docker and Docker Compose (for containerized deployment)
- 2GB RAM minimum
- 500MB disk space minimum

### External APIs
- OpenWeatherMap API key (free at https://openweathermap.org/api)

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   cd smart_tourism/travelplanner
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (WEATHER_API_KEY, SECRET_KEY, etc.)
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize database** (runs automatically, but can be manual)
   ```bash
   docker-compose exec web flask db upgrade
   docker-compose exec web flask seed-db
   ```

5. **Access the application**
   - Application: http://localhost:5000
   - PgAdmin: http://localhost:5050 (Email: admin@example.com)
   - Health Check: http://localhost:5000/health

### Local Development (Without Docker)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your database URL and API key
   ```

4. **Initialize database**
   ```bash
   flask db upgrade
   flask seed-db
   ```

5. **Run development server**
   ```bash
   python run.py
   ```

   Application will be available at: http://localhost:5000

## Development Setup

### Setting Up PostgreSQL Locally

1. **Install PostgreSQL**
   - Windows: Download from https://www.postgresql.org/download/windows/
   - Mac: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql`

2. **Create database and user**
   ```sql
   CREATE USER traveluser WITH PASSWORD 'securepassword';
   CREATE DATABASE travelplanner OWNER traveluser;
   GRANT ALL PRIVILEGES ON DATABASE travelplanner TO traveluser;
   ```

3. **Update .env**
   ```
   DATABASE_URL=postgresql://traveluser:securepassword@localhost:5432/travelplanner
   ```

### Getting Weather API Key

1. Visit https://openweathermap.org/api
2. Sign up for a free account
3. Copy your API key
4. Add to .env: `WEATHER_API_KEY=your_api_key_here`

### Flask CLI Commands

```bash
# Initialize database schema
flask init-db

# Populate with sample data
flask seed-db

# Drop all tables (WARNING: Data loss!)
flask drop-db

# Run database migrations
flask db upgrade

# Create new migration after model changes
flask db migrate -m "Description of changes"
```

### Running Tests

```bash
# Run entire test suite
python -m pytest

# Run specific test file
python -m pytest tests/test_models.py

# Run with coverage
python -m pytest --cov=app tests/
```

## Database Management

### Schema Overview

**User**: Stores authentication and profile data
```
id (int) - Primary key
username (string, unique) - Login identifier
email (string, unique) - Contact email
password_hash (string) - Bcrypt hashed password
created_at (datetime)
updated_at (datetime)
```

**City**: Travel destinations
```
id (int) - Primary key
name (string, unique) - City name
country (string) - Country name
description (text) - City description
latitude (float) - Geographic coordinate
longitude (float) - Geographic coordinate
image_url (string) - Featured image
created_at (datetime)
```

**Attraction**: Points of interest within cities
```
id (int) - Primary key
city_id (int) - Foreign key to City
name (string) - Attraction name
description (text) - Detailed description
category (string) - heritage/adventure/cultural
image_url (string) - Featured image
created_at (datetime)
```

**Review**: User reviews and ratings
```
id (int) - Primary key
user_id (int) - Foreign key to User
attraction_id (int) - Foreign key to Attraction
rating (float) - 1.0-5.0 star rating
title (string) - Review headline
comment (text) - Review content
created_at (datetime)
updated_at (datetime)
UNIQUE(user_id, attraction_id) - One review per user per attraction
```

### Migrations

```bash
# Generate migration from model changes
flask db migrate -m "Add new column"

# Apply pending migrations
flask db upgrade

# Rollback last migration
flask db downgrade
```

## API Documentation

### Authentication Endpoints

**POST /auth/register**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "confirm_password": "securepass123"
}
```

**POST /auth/login**
```json
{
  "username": "johndoe",
  "password": "securepass123",
  "remember_me": true
}
```

**GET /auth/logout**
Requires authentication

### Attraction Endpoints

**GET /api/attractions**
Returns all attractions (with optional filters)

Query Parameters:
- `city_id` (int) - Filter by city
- `category` (string) - Filter by category
- `page` (int) - Pagination

**GET /attractions/<id>**
Get detailed attraction information

### Review Endpoints

**GET /api/reviews/attraction/<attraction_id>**
Get reviews for an attraction

Parameters:
- `page` (int) - Page number
- `sort_by` (string) - recent/highest/lowest

**POST /reviews/add/<attraction_id>**
Create new review (requires authentication)

```json
{
  "rating": 4.5,
  "title": "Great place!",
  "comment": "Amazing attractions..."
}
```

**POST /reviews/<id>/edit**
Edit existing review (requires authentication)

**POST /reviews/<id>/delete**
Delete review (requires authentication)

### Health & Stats Endpoints

**GET /health**
```json
{
  "status": "healthy",
  "service": "travel-planner",
  "database": "connected"
}
```

**GET /api/stats**
```json
{
  "total_cities": 42,
  "total_attractions": 158,
  "total_reviews": 1024
}
```

## Deployment

### Production Checklist

- [ ] Generate secure SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] Set `FLASK_ENV=production`
- [ ] Configure PostgreSQL production database
- [ ] Set `SESSION_COOKIE_SECURE=true` (requires HTTPS)
- [ ] Enable `SESSION_COOKIE_HTTPONLY=true`
- [ ] Set strong database password
- [ ] Configure weather API key
- [ ] Set up HTTPS with reverse proxy (Nginx)
- [ ] Configure logging to persistent volume
- [ ] Set up automated backups for PostgreSQL
- [ ] Review security headers in app configuration

### Docker Deployment

1. **Build image**
   ```bash
   docker build -t travelplanner:latest .
   ```

2. **Run container**
   ```bash
   docker run -d \
     -e DATABASE_URL=postgresql://user:pass@db:5432/travelplanner \
     -e SECRET_KEY=your-secret-key \
     -e WEATHER_API_KEY=your-api-key \
     -p 5000:5000 \
     travelplanner:latest
   ```

### Production Gunicorn Configuration

```bash
gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 4 \
  --worker-class sync \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  wsgi:app
```

### Nginx Reverse Proxy

```nginx
upstream gunicorn {
    server localhost:5000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security

### Implemented Security Measures

1. **Authentication**: Sessions with Flask-Login, password hashing with PBKDF2-SHA256
2. **Authorization**: Login required decorators on protected routes
3. **CSRF Protection**: All forms protected with tokens
4. **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
5. **XSS Prevention**: Jinja2 auto-escaping of template variables
6. **Input Validation**: Server-side validation on all forms and APIs
7. **Password Requirements**: Minimum 8 characters, case-sensitive
8. **Session Security**: HTTP-only cookies, secure flag in production
9. **Secret Management**: Environment variables for sensitive data
10. **Logging**: Audit trail with created_at/updated_at timestamps

### Best Practices

- Never commit `.env` files with real credentials
- Use strong, randomly generated SECRET_KEY in production
- Always use HTTPS in production (set `SESSION_COOKIE_SECURE=true`)
- Regularly update dependencies: `pip list --outdated`
- Monitor application logs for suspicious activity
- Implement rate limiting for API endpoints (future enhancement)
- Use database backups and test recovery procedures

## Troubleshooting

### Database Connection Issues

**Error**: `FATAL: database does not exist`
```bash
# Create database
flask init-db
flask seed-db
```

**Error**: `could not translate host name to address`
```bash
# Check DATABASE_URL in .env
# Ensure PostgreSQL service is running
# For Docker: docker-compose ps
```

### Port Already in Use

**Error**: `Address already in use`
```bash
# Change port in .env
FLASK_PORT=5001

# Or kill process using port 5000
# Linux/Mac: lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill
# Windows: netstat -ano | findstr :5000
```

### Missing Weather Data

**Error**: `Could not fetch weather`
- Verify WEATHER_API_KEY is set in .env
- Check API key is active at https://openweathermap.org
- Ensure network connectivity
- Review logs: tail -f logs/app.log

### Import Errors

**Error**: `ModuleNotFoundError`
```bash
# Verify dependencies are installed
pip install -r requirements.txt

# Check Python version (should be 3.12+)
python --version

# Verify virtual environment is activated
which python  # Linux/Mac
where python  # Windows
```

### Database Migration Issues

**Error**: `Alembic version table not found`
```bash
# Initialize migrations
flask db upgrade
```

**Error**: `Target database is not up to date`
```bash
# Apply all pending migrations
flask db upgrade

# Check migration status
flask db history
```

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes with type hints and docstrings
3. Run tests: `pytest`
4. Ensure code style: Follow PEP 8
5. Commit with clear messages
6. Submit pull request

## License

This project is proprietary and confidential. Unauthorized copying or distribution is prohibited.

## Support

For issues, questions, or contributions:
- Check existing GitHub issues
- Review documentation in `/docs`
- Contact development team

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Python**: 3.12  
**Flask**: 3.0+  
**Database**: PostgreSQL 14+
