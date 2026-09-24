# File: modules/student_manager.py

import json
import os

# Define the file path for persistence
STUDENT_FILE = "data/students.json"


def load_students():
    """
    Loads student data from the JSON file.
    Returns an empty list if the file is missing or corrupted.
    """
    # Ensure the 'data' directory exists
    os.makedirs(os.path.dirname(STUDENT_FILE), exist_ok=True)

    if os.path.exists(STUDENT_FILE):
        with open(STUDENT_FILE, "r") as f:
            try:
                # Attempt to load the file contents
                data = json.load(f)
                # Ensure the loaded data is a list (the expected format)
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                # Handle cases where the file is empty or contains invalid JSON
                return []

    # If the file doesn't exist, return an empty list
    return []


def save_students(students_list):
    """Saves the current list of students back to the JSON file."""
    # Ensure the directory exists before writing
    os.makedirs(os.path.dirname(STUDENT_FILE), exist_ok=True)
    with open(STUDENT_FILE, "w") as f:
        json.dump(students_list, f, indent=4)


def add_student(name, roll_no, mobile, email):
    """Adds a new student if the roll number doesn't already exist."""
    students = load_students()
    roll_clean = roll_no.strip()

    # Check for roll number duplication case-insensitively
    if any(s.get("roll_no", "").strip().lower() == roll_clean.lower() for s in students):
        return False

    new_student = {
        "name": name.strip(),
        "roll_no": roll_clean,
        "mobile": mobile.strip(),
        "email": email.strip().lower(),
    }
    students.append(new_student)
    save_students(students)
    return True


def update_student(roll_no, new_data):
    """Updates the details for an existing student by roll number."""
    students = load_students()
    roll_target = roll_no.strip().lower()
    for i, s in enumerate(students):
        if s.get("roll_no", "").strip().lower() == roll_target:
            clean_data = {k: v.strip() if isinstance(v, str) else v for k, v in new_data.items()}
            if "email" in clean_data and isinstance(clean_data["email"], str):
                clean_data["email"] = clean_data["email"].lower()
            students[i].update(clean_data)
            save_students(students)
            return True
    return False


def delete_student(roll_no):
    """Deletes a student record by roll number."""
    students = load_students()
    roll_target = roll_no.strip().lower()
    initial_count = len(students)
    students[:] = [s for s in students if s.get("roll_no", "").strip().lower() != roll_target]

    if len(students) < initial_count:
        save_students(students)
        return True
    return False
