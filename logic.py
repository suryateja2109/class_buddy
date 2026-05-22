# File: logic.py (FINAL LOGIC FILE - With Tab Context & Cleanup)

import streamlit as st
import json
import os
from datetime import datetime, date, time, timedelta

# Import modules from your existing 'modules' directory
from modules.student_manager import (
    add_student,
    update_student as real_update_student,
    delete_student as real_delete_student,
)
from modules.schedule_manager import (
    add_class,
    update_class as real_update_class,
    delete_class as real_delete_class,
)
from modules.email_service import send_absence_alert
from modules import miss_predictor
from modules.attendance_logger import get_attendance_for_day, mark_attendance

# --- NEW IMPORT ---
from modules.reminder_sender import send_manual_reminder_util


# --- PERSISTENT LOG FILES ---
NOTIFICATION_LOG_FILE = "data/notification_log.json"
TEMP_PREDICTIONS_FILE = "data/temp_predictions.json"


def load_notification_log():
    """Loads the permanent notification log (History)."""
    if os.path.exists(NOTIFICATION_LOG_FILE):
        with open(NOTIFICATION_LOG_FILE, "r") as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []
    os.makedirs(os.path.dirname(NOTIFICATION_LOG_FILE), exist_ok=True)
    with open(NOTIFICATION_LOG_FILE, "w") as f:
        json.dump([], f)
    return []


# --- CRITICAL CHANGE: Added Cleanup Function ---
def clean_old_notifications():
    """Removes notifications that are older than 40 minutes."""
    log = load_notification_log()
    current_time = datetime.now()

    CLEANUP_WINDOW = timedelta(minutes=40)

    def is_recent(entry):
        try:
            log_time = datetime.strptime(entry.get("timestamp"), "%Y-%m-%d %H:%M:%S")
            return (current_time - log_time) < CLEANUP_WINDOW
        except:
            return True

    new_log = [entry for entry in log if is_recent(entry)]

    if len(new_log) < len(log):
        with open(NOTIFICATION_LOG_FILE, "w") as f:
            json.dump(new_log, f, indent=4)
        print(f"🧹 Cleaned {len(log) - len(new_log)} old notification entries.")
        return True
    return False


def log_notification(roll_no, name, subject, day):
    """
    Logs an event to the permanent persistent file with only core details.
    """

    log = load_notification_log()
    log.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "roll_no": roll_no,
            "name": name,
            "subject": subject,
            "day": day,
        }
    )
    with open(NOTIFICATION_LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)


def load_temp_predictions():
    """Loads the transient prediction log (Live Dashboard)."""
    if os.path.exists(TEMP_PREDICTIONS_FILE):
        with open(TEMP_PREDICTIONS_FILE, "r") as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []
    os.makedirs(os.path.dirname(TEMP_PREDICTIONS_FILE), exist_ok=True)
    return []


def save_temp_predictions(log_list):
    """Saves the temporary prediction log to a persistent file."""
    os.makedirs(os.path.dirname(TEMP_PREDICTIONS_FILE), exist_ok=True)
    with open(TEMP_PREDICTIONS_FILE, "w") as f:
        json.dump(log_list, f, indent=4)


def clear_temp_predictions():
    """Clears the entire temporary log file. (Used by scheduler)"""
    save_temp_predictions([])


# ---------------------
## CRUD WRAPPER FUNCTIONS (CRITICAL FIX: Setting view and active_tab)
# ---------------------


def save_student(name, roll_no, mobile, email):
    # CRITICAL FIX: Set view and tab to go back to after rerunning
    st.session_state.view = "student_management"
    st.session_state.active_tab = "tab_add"  # New students go back to the Add tab

    if add_student(name, roll_no, mobile, email):
        st.session_state["status_message"] = f"✅ Student '{name}' added successfully."
        st.session_state["status_type"] = "success"
        return True
    else:
        st.session_state["status_message"] = (
            f"❌ Error: Could not save student {roll_no}. Roll number might already exist."
        )
        st.session_state["status_type"] = "error"
        return False


def update_student(roll_no, new_data):
    # CRITICAL FIX: Set view and tab to go back to after rerunning
    st.session_state.view = "student_management"
    st.session_state.active_tab = "tab_manage"  # Updates go back to the Manage tab

    if real_update_student(roll_no, new_data):
        st.session_state["status_message"] = (
            f"✅ Student {roll_no} updated successfully."
        )
        st.session_state["status_type"] = "success"
        return True
    else:
        st.session_state["status_message"] = (
            f"❌ Error: Could not find/update student {roll_no}."
        )
        st.session_state["status_type"] = "error"
        return False


def delete_student(roll_no):
    # CRITICAL FIX: Set view and tab to go back to after rerunning
    st.session_state.view = "student_management"
    st.session_state.active_tab = "tab_manage"  # Deletes go back to the Manage tab

    if real_delete_student(roll_no):
        st.session_state["status_message"] = (
            f"🗑️ Student {roll_no} deleted successfully."
        )
        st.session_state["status_type"] = "success"
        return True
    else:
        st.session_state["status_message"] = (
            f"❌ Error: Could not find/delete student {roll_no}."
        )
        st.session_state["status_type"] = "error"
        return False


def save_class(day, subject, time_range, start_time_obj, end_time_obj):
    # CRITICAL FIX: Set view and tab to go back to after rerunning
    st.session_state.view = "class_management"
    st.session_state.active_tab = "tab_add"  # New classes go back to Add tab

    success, error_msg = add_class(
        day, subject, time_range, start_time_obj, end_time_obj
    )

    if success:
        st.session_state["status_message"] = (
            f"✅ Class '{subject}' on {day} added successfully."
        )
        st.session_state["status_type"] = "success"
        return True
    else:
        st.session_state["status_message"] = (
            f"❌ Error: {error_msg or 'Could not save class due to overlap or duplication.'}"
        )
        st.session_state["status_type"] = "error"
        return False


def update_class(old_day, old_subject, old_time, new_data):
    # CRITICAL FIX: Set view and tab to go back to after rerunning
    st.session_state.view = "class_management"
    st.session_state.active_tab = "tab_manage"  # Updates go back to Manage tab

    if real_update_class(old_day, old_subject, old_time, new_data):
        st.session_state["status_message"] = f"✅ Class updated successfully."
        st.session_state["status_type"] = "success"
        return True
    else:
        st.session_state["status_message"] = f"❌ Error: Could not find/update class."
        st.session_state["status_type"] = "error"
        return False


def delete_class(day, subject, time_range):
    # CRITICAL FIX: Set view and tab to go back to after rerunning
    st.session_state.view = "class_management"
    st.session_state.active_tab = "tab_manage"  # Deletes go back to Manage tab

    if real_delete_class(day, subject, time_range):
        st.session_state["status_message"] = (
            f"🗑️ Class '{subject}' on {day} deleted successfully."
        )
        st.session_state["status_type"] = "success"
        return True
    else:
        st.session_state["status_message"] = (
            f"❌ Error: Could not find/delete class '{subject}' on {day}."
        )
        st.session_state["status_type"] = "error"
        return False


def send_reminder(roll_no, subject, message):
    """
    Wrapper to send a manual reminder email using the reminder_sender module.
    Handles setting Streamlit status messages.
    """
    if send_manual_reminder_util(roll_no, subject, message):
        st.session_state["status_message"] = (
            f"📧 Reminder sent successfully to {roll_no}."
        )
        st.session_state["status_type"] = "success"
        return True
    else:
        st.session_state["status_message"] = (
            f"❌ Error: Could not send reminder to {roll_no} (check student details/service)."
        )
        st.session_state["status_type"] = "error"
        return False
