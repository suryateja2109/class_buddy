# File: modules/analytics_ui.py

import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import date, timedelta

# FIX: Use absolute imports for sibling modules in the 'modules' directory
from modules.student_manager import load_students
from modules.schedule_manager import load_schedule
from modules.attendance_logger import load_attendance


# Helper to generate mock attendance data for visualization
def generate_mock_analytics_data(subjects):
    """Generates mock data suitable for visualizations."""

    # 1. Subject-wise Attendance Data
    subject_data = {}
    for subj in subjects:
        # Simulate attendance percentage between 70% and 100%
        att_percent = random.randint(70, 100)
        total_classes = random.randint(15, 30)

        subject_data[subj] = {
            "Attendance %": att_percent,
            "Attended": int(total_classes * (att_percent / 100)),
            "Missed": total_classes - int(total_classes * (att_percent / 100)),
            "Total": total_classes,
        }

    # 2. Monthly Summary (Last 4 months)
    today = date.today()
    monthly_summary = {}
    for i in range(4):
        # Calculate month by going backwards
        month_name = (today.replace(day=1) - timedelta(days=i * 30)).strftime("%b %Y")
        monthly_summary[month_name] = random.randint(80, 95)  # Mock attendance %

    return subject_data, monthly_summary


# --- MODIFIED FUNCTION SIGNATURE ---
def calculate_and_display_analytics():
    """
    Provides interactive visualizations of attendance trends (The Progress Dashboard).
    """

    students = load_students()
    schedule = load_schedule()

    # --- Initial Error Handling & Student Filter ---
    if not students:
        st.info("No student data found. Please add a student first.")
        return

    all_subjects = list({c["subject"] for d in schedule.values() for c in d})
    if not all_subjects:
        st.info(
            "No classes found in the schedule. Please add classes to view analytics."
        )
        return

    # 1. STUDENT FILTER
    student_options = {f"{s['name']} (Roll: {s['roll_no']})": s for s in students}
    selected_option = st.selectbox(
        "Select Student for Progress Dashboard",
        options=list(student_options.keys()),
        key="analytics_student_select",
    )

    # Get the data for the selected student
    selected_student = student_options[selected_option]

    # --- Data Preparation ---
    # Note: Mock data generation is currently not dependent on the *selected* student,
    # but in a real app, load_attendance() would be filtered by roll_no.
    subject_data_dict, monthly_summary = generate_mock_analytics_data(all_subjects)

    df_subjects = pd.DataFrame.from_dict(subject_data_dict, orient="index")
    df_subjects.index.name = "Subject"
    df_subjects = df_subjects.reset_index()

    st.markdown(f"## {selected_student['name']}'s Progress Dashboard")
    st.markdown("---")

    # --- 1. Weekly and Monthly Summary Reports ---
    st.subheader("📚 Summary Reports")

    col_monthly, col_weekly = st.columns(2)

    with col_monthly:
        st.markdown("##### Monthly Attendance Trend")
        df_monthly = pd.DataFrame(
            monthly_summary.items(), columns=["Month", "Attendance %"]
        )
        # Prepare for sorting
        df_monthly["Date_Sort"] = pd.to_datetime(df_monthly["Month"], format="%b %Y")
        df_monthly = df_monthly.sort_values(by="Date_Sort")

        st.line_chart(df_monthly.set_index("Month")["Attendance %"])

    with col_weekly:
        st.markdown("##### Overall Progress Metrics")

        # Calculate overall metrics (based on mock data)
        overall_attended = df_subjects["Attended"].sum()
        overall_missed = df_subjects["Missed"].sum()
        overall_total = df_subjects["Total"].sum()
        overall_percent = (
            round((overall_attended / overall_total) * 100, 1)
            if overall_total > 0
            else 0
        )

        st.metric(
            label="Overall Attendance Percentage",
            value=f"{overall_percent}%",
            delta=(
                f"+{random.randint(0, 2)}.0%"
                if overall_percent > 75
                else f"-{random.randint(0, 3)}.0%"
            ),
        )
        st.metric(label="Total Classes Attended", value=overall_attended)
        st.metric(label="Total Classes Missed", value=overall_missed)

    st.markdown("---")

    # --- 2. Bar Graphs of Subject-wise Attendance (WITH Subject Filter) ---
    st.subheader("📊 Subject-wise Attendance Rates")

    # 2a. SUBJECT FILTER
    subject_filter = st.multiselect(
        "Filter Subjects for Bar Chart",
        options=all_subjects,
        default=all_subjects,
        key="analytics_subject_filter",
    )

    df_filtered_subjects = df_subjects[df_subjects["Subject"].isin(subject_filter)]

    if not df_filtered_subjects.empty:
        st.bar_chart(df_filtered_subjects.set_index("Subject")["Attendance %"])
        st.dataframe(
            df_filtered_subjects.sort_values(by="Attendance %"),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.warning("No subjects selected or data available for this view.")

    st.markdown("---")

    # --- 3. Pie Charts for Attended vs. Missed Classes ---
    st.subheader("🥧 Missed vs. Attended Breakdown")

    pie_col_1, pie_col_2 = st.columns(2)

    with pie_col_1:
        st.markdown("##### Overall Breakdown")
        df_overall_pie = pd.DataFrame(
            {
                "Category": ["Attended", "Missed"],
                "Count": [overall_attended, overall_missed],
            }
        )
        st.vega_lite_chart(
            df_overall_pie,
            {
                "mark": {"type": "arc", "innerRadius": 50},
                "encoding": {
                    "theta": {"field": "Count", "type": "quantitative"},
                    "color": {
                        "field": "Category",
                        "scale": {"range": ["#1abc9c", "#e74c3c"]},
                    },
                },
                "width": 300,
                "height": 300,
            },
        )

    with pie_col_2:
        st.markdown("##### Breakdown by Missed Subject (Top 3)")
        df_missed = df_subjects.sort_values(by="Missed", ascending=False).head(3)
        st.bar_chart(df_missed.set_index("Subject")["Missed"])

    st.markdown("---")

    # --- 4. Heat Maps showing most missed days or times ---
    st.subheader("🔥 Missed Classes Heatmap (By Timeslot)")

    # Create mock day/time data matrix (5 days x 5 slots)
    mock_matrix = np.random.randint(0, 6, size=(5, 5))
    df_heatmap = pd.DataFrame(
        mock_matrix,
        index=["Mon", "Tue", "Wed", "Thu", "Fri"],
        columns=["8am-9am", "9am-10am", "10am-11am", "11am-12pm", "1pm-2pm"],
    )

    st.write("Mock Count of Classes Missed per Day/Timeslot:")
    st.dataframe(df_heatmap)
