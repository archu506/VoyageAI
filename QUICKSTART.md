# Quick Start Guide

Get your Smart Tourism application running in 5 minutes!

## ⚡ Express Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add:
# - SECRET_KEY=your-secret-here (can be any random string)
# - WEATHER_API_KEY=your-api-key-from-openweathermap
```

**Get a Free Weather API Key:**
1. Visit https://openweathermap.org/api
2. Sign up for free
3. Get API key from dashboard
4. Paste it in your .env file

### Step 3: Run the Application
```bash
python run.py
```

The application will:
- Create the database automatically
- Load initial attractions data
- Start on http://localhost:5000

### Step 4: Test It!
1. Open http://localhost:5000 in your browser
2. Click **Register** to create an account
3. Login with your credentials
4. Click **Plan Trip** and select:
   - City: `Jaipur` (or `Goa`)
   - Days: `3`
5. Click **View Reviews** on any attraction
6. Click **Write Review** to add a review
7. Visit your profile to see your reviews

---

## 🐳 Docker Quick Start

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your WEATHER_API_KEY

# Run with Docker Compose
docker-compose up --build

# Access at http://localhost:5000
```

---

## 📋 Available Test Data

The system comes pre-loaded with attractions from:
- **Jaipur**: Amber Fort, Hawa Mahal, City Palace, Jantar Mantar, Nahargarh Fort, Chokhi Dhani
- **Goa**: Baga Beach, Calangute Beach, Fort Aguada, Dudhsagar Falls, Basilica of Bom Jesus

Try planning trips to these cities!

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```bash
# Install dependencies
pip install -r requirements.txt
```

### "WEATHER_API_KEY not found"
- Make sure you added it to your `.env` file
- Check for typos
- Get a free key from https://openweathermap.org/api

### Database Errors
```bash
# Reset database (loses all data)
rm instance/smart_tourism.db

# Restart application
python run.py
```

### Port Already in Use
Flask defaults to port 5000. To use a different port:
```bash
python run.py --port 5001
```

---

## 📚 Project Structure (Key Files)

```
app/
├── __init__.py        ← App initialization
├── models/            ← Database models (User, City, Place, Review)
├── forms/             ← Form validation
├── services/          ← Business logic
├── routes/            ← URL routes
│   ├── auth.py        ← Login/Register
│   ├── itinerary.py   ← Trip planning
│   └── reviews.py     ← Review management
└── templates/         ← HTML pages (Bootstrap powered)

config.py             ← Configuration (dev/prod)
run.py                ← Start here
requirements.txt      ← Dependencies
.env                  ← Your secrets (create from .env.example)
README.md             ← Full documentation
MIGRATION_GUIDE.md    ← Detailed upgrade explanation
```

---

## 🎯 Common Tasks

### Add a New City/Attraction
Edit `data/attractions.json` and restart the app.

### Change Database
Edit `DATABASE_URL` in `config.py` or `.env`:
```
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/smart_tourism

# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost/smart_tourism
```

### Enable Production Mode
```bash
# In .env
FLASK_ENV=production
DEBUG=False
```

### View Database
```bash
# Install sqlite3 viewer (optional)
sqlite3 instance/smart_tourism.db

# Query examples
sqlite> SELECT * FROM users;
sqlite> SELECT * FROM reviews;
```

---

## 🚀 Next Steps

After running successfully:

1. **Explore Features**
   - Create multiple accounts
   - Write reviews
   - Filter and search

2. **Read Documentation**
   - `README.md` - Full project overview
   - `MIGRATION_GUIDE.md` - Architecture decisions
   - `config.py` - Configuration options

3. **Understand the Code**
   - Study the blueprint structure (routes/)
   - Review the service layer (services/)
   - Check the database models (models/)

4. **Add Your Own Features**
   - Add email notifications
   - Add user profiles pictures
   - Add wishlist functionality
   - Add trip saving
   - Add sharing capabilities

---

## 📞 Need Help?

- Check the README.md for comprehensive guide
- Review MIGRATION_GUIDE.md for architecture explanation
- Check logs in the console for error messages
- Make sure your .env file has all required variables

---

## ✅ Verification Checklist

- [ ] Python 3.9+ installed (`python --version`)
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list` should show Flask, SQLAlchemy, etc.)
- [ ] `.env` file created with WEATHER_API_KEY
- [ ] Application started (`python run.py` shows "Running on http://localhost:5000")
- [ ] Can access https://localhost:5000 in browser
- [ ] Can register and login
- [ ] Can generate itinerary
- [ ] Can write a review
- [ ] Can see your profile

When all are checked ✅, you're ready to go! 🎉

---

**Happy traveling! 🌍✈️**
