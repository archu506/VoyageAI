import logging
import os
import json
from datetime import datetime


# -------------------------------
# JSON Formatter (Production logs)
# -------------------------------
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Add structured data if present
        if hasattr(record, "extra_data"):
            log_entry["extra"] = record.extra_data

        return json.dumps(log_entry)


# -------------------------------
# Logger Setup
# -------------------------------
def setup_logger(name="adaptive_travel"):
    logger = logging.getLogger(name)

    # Prevent duplicate handlers (VERY IMPORTANT in Vercel / Flask)
    if logger.handlers:
        return logger

    # Log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Console handler (Vercel captures this automatically)
    handler = logging.StreamHandler()
    handler.setLevel(logger.level)

    # Choose format based on environment
    if os.getenv("ENV", "production") == "production":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "[%(asctime)s - %(name)s - %(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Global logger instance
logger = setup_logger()


# -------------------------------
# Application Logs
# -------------------------------
def log_adaptation(city, weather, aqi, crowd, energy, selected_count):
    logger.info(
        "Adaptation event",
        extra={
            "extra_data": {
                "city": city,
                "weather": weather.get("condition"),
                "aqi": aqi.get("level"),
                "crowd": crowd,
                "energy": energy,
                "attractions_selected": selected_count
            }
        }
    )


def log_fallback(reason):
    logger.warning(
        "Fallback activated",
        extra={
            "extra_data": {
                "reason": reason
            }
        }
    )