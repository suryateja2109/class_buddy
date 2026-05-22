# File: modules/attendance_logger.py

import json
import os

ATTENDANCE_FILE = "data/attendance.json"


def load_attendance():
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "r") as f:
            try:
                # Structure: { "YYYY-MM-DD": { "class_id": { "roll_no": "Status" } } }
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_attendance(attendance_dict):
    os.makedirs(os.path.dirname(ATTENDANCE_FILE), exist_ok=True)
    with open(ATTENDANCE_FILE, "w") as f:
        json.dump(attendance_dict, f, indent=4)


def mark_attendance(class_id, roll_no, status, date_str):
    attendance = load_attendance()

    if date_str not in attendance:
        attendance[date_str] = {}

    if class_id not in attendance[date_str]:
        attendance[date_str][class_id] = {}

    attendance[date_str][class_id][roll_no] = status
    save_attendance(attendance)
    return True


def get_attendance_for_day(date_str):
    attendance = load_attendance()
    return attendance.get(date_str, {})
