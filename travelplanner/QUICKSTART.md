# Quick Start Guide

Get the Travel Planner application up and running in 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- OpenWeatherMap API key (free at https://openweathermap.org/api)

## Installation & Setup

### Step 1: Clone and Navigate
```bash
cd smart_tourism/travelplanner
```

### Step 2: Create Environment File
```bash
cp .env.example .env
```

### Step 3: Edit Configuration
Open `.env` and update:
```
WEATHER_API_KEY=your_actual_api_key_here
SECRET_KEY=your-secret-key-here
DB_PASSWORD=securepassword
```

### Step 4: Start Services
```bash
docker-compose up -d
```

This starts:
- PostgreSQL database on port 5432
- Flask web app on port 5000
- PgAdmin on port 5050

### Step 5: Access the Application

- **Web App**: http://localhost:5000
- **Login Credentials**:
  - Username: `demo`
  - Password: `demo1234`
- **PgAdmin**: http://localhost:5050
  - Email: `admin@example.com`
  - Password: `admin`

## Common Commands

### View Logs
```bash
# Web application logs
docker-compose logs -f web

# Database logs
docker-compose logs -f postgres
```

### Database Operations
```bash
# Seed additional data
docker-compose exec web flask seed-db

# Access database directly
docker-compose exec postgres psql -U traveluser -d travelplanner

# Create fresh database
docker-compose exec web flask drop-db
docker-compose exec web flask init-db
docker-compose exec web flask seed-db
```

### Application Management
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: Deletes database data)
docker-compose down -v

# Restart services
docker-compose restart

# View running containers
docker-compose ps
```

## Development Workflow

### Making Code Changes

1. Edit files in the application directory
2. With `docker-compose up` running, changes auto-reload thanks to `--reload` flag
3. Refresh browser to see changes
4. Check logs: `docker-compose logs -f web | grep error`

### Database Schema Changes

1. Update model in `app/models/__init__.py`
2. Create migration: `docker-compose exec web flask db migrate -m "description"`
3. Apply migration: `docker-compose exec web flask db upgrade`
4. Restart web service: `docker-compose restart web`

### Accessing Bash Shell
```bash
# Access web container
docker-compose exec web /bin/bash

# Inside container:
# - Run pytest: pytest tests/
# - Check dependencies: pip list
# - View logs: tail -f logs/app.log
```

## Troubleshooting

### Services Won't Start
```bash
# Check if ports are already in use
docker-compose down
docker-compose up -d
```

### Database Connection Error
```bash
# Check database is ready
docker-compose exec postgres pg_isready

# Check logs
docker-compose logs postgres | tail -20

# Rebuild from scratch
docker-compose down -v
docker-compose up -d
```

### Can't Login with Demo Account
```bash
# Reseed the database
docker-compose exec web flask drop-db
docker-compose exec web flask init-db
docker-compose exec web flask seed-db
```

### Port 5000 Already in Use
```bash
# Option 1: Stop other processes
# Linux/Mac: lsof -i :5000 | tail -1 | awk '{print $2}' | xargs kill
# Windows: netstat -ano | findstr :5000 | findstr LISTENING

# Option 2: Use different port
# Edit docker-compose.yml and change "5000:5000" to "5001:5000"
```

## Local Development (Without Docker)

If you prefer local development without Docker:

### 1. Install PostgreSQL
- Download from https://www.postgresql.org/download/
- Create user: `traveluser` with password `password`
- Create database: `travelplanner`

### 2. Setup Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your local database URL
DATABASE_URL=postgresql://traveluser:password@localhost:5432/travelplanner
```

### 4. Initialize Database
```bash
flask init-db
flask seed-db
```

### 5. Run Development Server
```bash
python run.py
```

Access at http://localhost:5000

## Next Steps

- [ ] Explore the Demo Account and create reviews
- [ ] Browse attractions by city
- [ ] Test the weather API integration
- [ ] Review application logs
- [ ] Read [README.md](README.md) for detailed documentation
- [ ] Check [API Documentation](README.md#api-documentation)

## Support

Having issues? Check:
1. [Troubleshooting Section](#troubleshooting)
2. Application logs: `docker-compose logs -f web`
3. Database logs: `docker-compose logs -f postgres`
4. Full [README.md](README.md) documentation

---

**Having fun?** Try:
- Creating a new user account
- Adding reviews to attractions
- Searching for specific cities or attractions
- Checking real weather data for different cities
