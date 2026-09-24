# File: backend/config.py
from pathlib import Path
import os
from dotenv import load_dotenv

# Base paths
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from root .env if present
env_file = ROOT_DIR / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

# Data file paths
STUDENT_FILE = str(DATA_DIR / "students.json")
SCHEDULE_FILE = str(DATA_DIR / "schedule.json")
ATTENDANCE_FILE = str(DATA_DIR / "attendance.json")
NOTIFICATION_LOG_FILE = str(DATA_DIR / "notification_log.json")
TEMP_PREDICTIONS_FILE = str(DATA_DIR / "temp_predictions.json")
