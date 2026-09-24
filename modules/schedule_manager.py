# File: modules/schedule_manager.py

import json
import os
from datetime import datetime, time

SCHEDULE_FILE = "data/schedule.json"


def load_schedule():
    # ... (unchanged load_schedule and save_schedule functions) ...
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_schedule(schedule_dict):
    os.makedirs(os.path.dirname(SCHEDULE_FILE), exist_ok=True)
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule_dict, f, indent=4)


# --- NEW: Helper function to check for time overlaps ---
def check_overlap(schedule_list, new_start_time, new_end_time):
    new_start_dt = datetime.combine(datetime.min.date(), new_start_time)
    new_end_dt = datetime.combine(datetime.min.date(), new_end_time)

    for class_item in schedule_list:
        try:
            time_range = class_item.get("time")
            start_str, end_str = time_range.split(" - ")

            existing_start = datetime.strptime(start_str, "%I:%M %p").time()
            existing_end = datetime.strptime(end_str, "%I:%M %p").time()

            existing_start_dt = datetime.combine(datetime.min.date(), existing_start)
            existing_end_dt = datetime.combine(datetime.min.date(), existing_end)

            # Check for overlap: [StartA < EndB] AND [EndA > StartB]
            if (new_start_dt < existing_end_dt) and (new_end_dt > existing_start_dt):
                return True  # Overlap found
        except Exception:
            # Ignore classes with corrupted time data
            continue
    return False


# --- NEW: CREATE OPERATION ---
def add_class(day, subject, time_range, start_time_obj, end_time_obj):
    schedule = load_schedule()

    day_schedule = schedule.get(day, [])

    # 1. Check for time overlap
    if check_overlap(day_schedule, start_time_obj, end_time_obj):
        return False, "Error: Class time overlaps with an existing class."

    # 2. Check for duplicate subject at the exact time
    if any(
        c.get("subject") == subject and c.get("time") == time_range
        for c in day_schedule
    ):
        return False, "Error: A class with this subject and time already exists."

    new_class = {"subject": subject, "time": time_range}

    # Add new class to the list for that day
    day_schedule.append(new_class)
    schedule[day] = day_schedule

    save_schedule(schedule)
    return True, None


def update_class(old_day, old_subject, old_time, new_data):
    # ... (existing update_class logic remains, needs refinement for overlap checking) ...
    schedule = load_schedule()

    if old_day in schedule:
        for i, class_item in enumerate(schedule[old_day]):
            if (
                class_item.get("subject") == old_subject
                and class_item.get("time") == old_time
            ):

                # Extract new time objects for overlap check
                try:
                    start_str, end_str = new_data["time"].split(" - ")
                    new_start_obj = datetime.strptime(start_str, "%I:%M %p").time()
                    new_end_obj = datetime.strptime(end_str, "%I:%M %p").time()
                except Exception:
                    return False  # Invalid time format

                # Temporarily remove the current class for overlap check against others
                temp_schedule_list = schedule[old_day][:i] + schedule[old_day][i + 1 :]

                # Check for overlap against all OTHER classes on that day
                if check_overlap(temp_schedule_list, new_start_obj, new_end_obj):
                    return False  # Overlap found with a different class

                # Apply update
                schedule[old_day][i].update(new_data)
                save_schedule(schedule)
                return True
    return False


def delete_class(day, subject, time_range):
    # ... (unchanged delete_class function) ...
    schedule = load_schedule()

    if day in schedule:
        initial_count = len(schedule[day])

        schedule[day][:] = [
            c
            for c in schedule[day]
            if not (c.get("subject") == subject and c.get("time") == time_range)
        ]

        if not schedule[day]:
            del schedule[day]

        if len(schedule.get(day, [])) < initial_count or day not in schedule:
            save_schedule(schedule)
            return True
    return False
