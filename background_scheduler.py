# File: background_scheduler.py (FINAL - Constant Resend Logic)

import time
import schedule
from datetime import datetime, date, timedelta
import os

# Import necessary core modules (Scheduler needs access to data)
from modules.student_manager import load_students
from modules.schedule_manager import load_schedule
from modules.email_service import send_absence_alert
from modules import miss_predictor

# Import the persistent logging functions, including the checker function
# NOTE: has_alert_been_logged is REMOVED from the import list.
from logic import (
    log_notification,
    load_temp_predictions,
    save_temp_predictions,
    clear_temp_predictions,
    clean_old_notifications,
)


def run_prediction_and_alert():
    """
    Runs prediction, attempts email send, and logs the attempt.
    """

    # --- Run cleanup on every scheduler cycle ---
    clean_old_notifications()
    # ---------------------------------------------------

    # Ensure data files exist before loading
    if not os.path.exists("data/students.json") or not os.path.exists(
        "data/schedule.json"
    ):
        print("Data files not found. Skipping prediction run.")
        clear_temp_predictions()
        return 0

    students_list = load_students()
    schedule_data = load_schedule()

    now = datetime.now()
    current_time = now.time()
    today_day = now.strftime("%A")

    today_classes = schedule_data.get(today_day, [])

    # If no classes are scheduled, clear the temp log and exit
    if not today_classes:
        print("No classes today. Clearing temp log.")
        clear_temp_predictions()
        return 0

    alerts_sent_count = 0
    temp_log_entries = []  # List to hold the new, time-relevant predictions

    # We use a single window for prediction, logging, and sending (35 minutes)
    PREDICTION_AND_SEND_WINDOW = timedelta(minutes=35)

    for class_item in today_classes:
        subj = class_item.get("subject", "Unknown Subject")
        time_range = class_item.get("time", "12:00 AM - 12:00 AM")

        try:
            start_time_str = time_range.split(" - ")[0]
            dt_now = datetime.combine(date.min, current_time)
            dt_class_start = datetime.combine(
                date.min, datetime.strptime(start_time_str, "%I:%M %p").time()
            )

            if dt_class_start <= dt_now:
                continue

            time_until_class = dt_class_start - dt_now

            # --- 1. PREDICTION CHECK (Max 35 minutes) ---
            if time_until_class <= PREDICTION_AND_SEND_WINDOW:

                # Set alert time to be the prediction window itself
                is_alert_time = True

                # Iterate over students to run prediction
                for student in students_list:
                    roll_no = student["roll_no"]
                    name = student["name"]

                    prediction_result = miss_predictor.predict_risk(
                        roll_no, subj, today_day
                    )

                    if prediction_result == 1:
                        # Student is predicted ABSENT.

                        # --- CRITICAL: Attempt Email Send Immediately ---
                        email = student["email"]
                        email_success = send_absence_alert(name, email, subj, today_day)

                        # Determine status for temporary log
                        status = "ALERT SENT" if email_success else "ALERT FAILED"

                        # --- Log the event to PERMANENT History ---
                        # This logs the event every time a send is attempted.
                        log_notification(
                            roll_no,
                            name,
                            subj,
                            today_day,
                        )

                        if email_success:
                            alerts_sent_count += 1
                            print(
                                f"-> Alert sent to {name} for {subj}. Status: {status}"
                            )
                        # --- END CRITICAL MERGED LOGIC ---

                        # --- Log to TEMPORARY file (Live Dashboard) ---
                        temp_log_entries.append(
                            {
                                "time_until": str(time_until_class).split(".")[0],
                                "class_time": start_time_str,
                                "roll_no": roll_no,
                                "name": name,
                                "subject": subj,
                                "status": status,
                                "is_alert_window": is_alert_time,
                            }
                        )

        except Exception as e:
            print(f"Error processing class {subj}: {e}")

    # 3. Overwrite the temporary log on every run (Transient logging)
    save_temp_predictions(temp_log_entries)

    if temp_log_entries:
        print(
            f"✅ Saved {len(temp_log_entries)} live prediction entries to temporary log."
        )

    return alerts_sent_count


# ---------------------
# SCHEDULER EXECUTION
# ---------------------

schedule.every(1).minute.do(run_prediction_and_alert)
print("Background scheduler started. Checking for alerts every minute...")

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler stopped by user.")
        clear_temp_predictions()
        break
    except Exception as e:
        print(f"An error occurred in the scheduler loop: {e}")
        time.sleep(60)
