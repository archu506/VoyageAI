@echo off
REM ATIG Setup and Run Script

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║         ATIG - Adaptive Tourism Intelligence Grid            ║
echo ║                Setup and Launch Script                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -q Flask pandas numpy networkx scikit-learn scipy --upgrade

echo.
echo Creating sample data...
if not exist "data\footfall_history.json" (
    echo Data file missing - creating minimal dataset...
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    Starting ATIG Server                      ║
echo ║                                                              ║
echo ║        🌍 Open browser: http://localhost:5000               ║
echo ║        📊 Dashboard: http://localhost:5000/dashboard        ║
echo ║        📍 Planner: http://localhost:5000/plan               ║
echo ║                                                              ║
echo ║        Press Ctrl+C to stop the server                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

python run.py

pause
