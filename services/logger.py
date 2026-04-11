import logging
import os
from datetime import datetime

def setup_logger(name="adaptive_travel"):
    """Configure logging to file and console."""
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler("logs/app.log")
    fh.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s - %(name)s - %(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

# Global logger instance
logger = setup_logger()

def log_adaptation(city, weather, aqi, crowd, energy, selected_count):
    """Log adaptation event."""
    logger.info(
        f"Adaptation: city={city}, weather={weather['condition']}, "
        f"aqi={aqi['level']}, crowd={crowd}%, energy={energy}, "
        f"attractions_selected={selected_count}"
    )

def log_fallback(reason):
    """Log fallback activation."""
    logger.warning(f"Fallback activated: {reason}")
