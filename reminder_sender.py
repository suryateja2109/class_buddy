# File: modules/reminder_sender.py

# Note: The actual sending mock is in email_service.py. 
# This module acts as a bridge/utility layer.

from .email_service import send_manual_reminder
from .student_manager import load_students

def send_manual_reminder_util(roll_no, subject, message):
    """Fetches student data and sends a manual reminder via the email service."""
    students = load_students()
    student = next((s for s in students if s["roll_no"] == roll_no), None)
    
    if student:
        return send_manual_reminder(student["name"], student["email"], subject, message)
    
    print(f"[MOCK EMAIL] Failed to send manual reminder: Student {roll_no} not found.")
    return False