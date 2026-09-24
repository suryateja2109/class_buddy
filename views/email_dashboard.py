# File: views/email_dashboard.py (Notification Log Commented Out)

import streamlit as st
import pandas as pd

# Import only necessary helper and logic functions
from helpers import card_start, card_end
from logic import (
    load_notification_log,
    load_temp_predictions,
    clear_temp_predictions,
    send_reminder,
)
from modules.schedule_manager import load_schedule
from modules.student_manager import load_students


def email_dashboard_view(students, schedule):
    card_start("📧 Email Notification Dashboard")

    # --- 1. Define Tabs ---
    # We define the tabs but only use tab_temp and tab_manual
    tab_temp, tab_log, tab_manual = st.tabs(
        [
            "Temporary Notification",  # Live Predictions
            "Notification Log",  # Permanent History
            "Manual Send",
        ]
    )

    # --- 2. Tab: Predicted Absences (Live) / Temporary Notification ---
    with tab_temp:
        st.subheader("Time-Sensitive Absence Predictions")
        st.warning(
            "⚠️ **LIVE PREDICTIONS:** This log shows students predicted to miss an **upcoming** class (within the next 35 minutes). Entries will clear automatically as class time passes."
        )

        temp_log_data = load_temp_predictions()

        if temp_log_data:
            df_temp = pd.DataFrame(temp_log_data)

            # Prepare data and columns
            df_temp = df_temp[
                ["name", "roll_no", "subject", "class_time", "time_until", "status"]
            ]
            df_temp.columns = [
                "Name",
                "Roll No",
                "Subject",
                "Class Time",
                "Time Until",
                "Status",
            ]

            # Style the dataframe based on Status (FIXED)
            def highlight_status(row):
                # Define the style you want to apply to the whole row
                if row["Status"] == "ALERT SENT":
                    row_style = (
                        "background-color: #1abc9c; color: white; font-weight: bold;"
                    )
                elif row["Status"] == "ALERT FAILED":
                    row_style = (
                        "background-color: #e74c3c; color: white; font-weight: bold;"
                    )
                elif row["Status"].startswith("WAITING"):
                    row_style = (
                        "background-color: #f1c40f; color: black; font-weight: bold;"
                    )
                else:
                    row_style = ""

                # CRITICAL FIX: Return a list of style strings for ALL columns in the row
                return [row_style] * len(row)

            st.dataframe(
                df_temp.style.apply(highlight_status, axis=1),
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info(
                "No students are currently predicted to be absent for upcoming classes."
            )

    # --- 3. Tab: Notification Log (Permanent History) ---
    with tab_log:
        st.subheader("Automated & Manual Email History (Core Log)")
        st.info(
            "This is the permanent record of all alert triggers, saving only core student/class details."
        )

        log_data = load_notification_log()

        if log_data:
            df = pd.DataFrame(log_data)
            df = df.set_index("timestamp")

            # Check for legacy status fields for warning purposes
            if any(
                col in df.columns for col in ["prediction", "email_status", "status"]
            ):
                st.warning(
                    "Legacy status fields detected in log. Showing only core fields for new entries."
                )

            # --- CRITICAL CHANGE: Always select only the core fields ---

            # Select only the fields that are guaranteed to be saved by the new logic
            df = df[["roll_no", "name", "subject", "day"]]

            df.columns = [
                "Roll No",
                "Name",
                "Subject",
                "Day",
            ]

            st.dataframe(df, use_container_width=True)
        else:
            st.info("No email notifications have been logged yet.")

    # --- 4. Tab: Manual Send ---
    with tab_manual:
        st.subheader("Send Manual Reminder/Alert")

        students_list = load_students()
        schedule_data = load_schedule()

        all_subjects = list(
            {c["subject"] for d in schedule_data.values() for c in d if isinstance(c, dict) and "subject" in c}
        )

        if not students_list or not all_subjects:
            st.warning(
                "Cannot send reminder: Please ensure both students and classes are configured."
            )

        else:
            student_options = {
                f"{s['name']} (Roll: {s['roll_no']})": s["roll_no"]
                for s in students_list
            }
            roll_options = list(student_options.keys())

            with st.form("manual_reminder_form"):
                col_roll, col_subj = st.columns(2)
                target_option = col_roll.selectbox(
                    "Select Student", roll_options, key="manual_roll_option"
                )
                target_roll = student_options.get(target_option)
                target_subj = col_subj.selectbox(
                    "Select Subject", all_subjects, key="manual_subj"
                )

                message = st.text_area(
                    "Custom Message/Reason", height=100, key="manual_message"
                )

                if st.form_submit_button("Send Reminder Now", type="primary"):
                    if not target_roll or not message:
                        st.error("Please select a student and enter a message.")
                    else:
                        send_reminder(target_roll, target_subj, message)
                        st.rerun()

    if st.button("⬅ Back to Home", key="back_from_email_dash"):
        st.session_state.view = "home"
        st.rerun()

    card_end()
