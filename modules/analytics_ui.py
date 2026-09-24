# File: modules/analytics_ui.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from modules.student_manager import load_students
from modules.schedule_manager import load_schedule
from modules.attendance_logger import load_attendance


def compute_student_analytics(student_roll, all_subjects, attendance_data):
    """
    Computes genuine attendance analytics for a specific student from logged records.
    """
    subject_stats = {
        subj: {"Attended": 0, "Missed": 0, "Total": 0, "Attendance %": 0.0}
        for subj in all_subjects
    }
    monthly_data = {}  # { "YYYY-MM": {"Attended": 0, "Total": 0, "Label": "Mon YYYY"} }
    day_missed = {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0}

    for date_str, classes in sorted(attendance_data.items()):
        if not isinstance(classes, dict):
            continue

        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            month_key = dt.strftime("%Y-%m")
            month_label = dt.strftime("%b %Y")
            day_abbr = dt.strftime("%a")
        except ValueError:
            month_key = "Unknown"
            month_label = "Unknown"
            day_abbr = "Unknown"

        if month_key not in monthly_data:
            monthly_data[month_key] = {"Attended": 0, "Total": 0, "Label": month_label}

        for class_key, roll_map in classes.items():
            if not isinstance(roll_map, dict) or student_roll not in roll_map:
                continue

            status = roll_map[student_roll]
            parts = class_key.split("__")
            subject_name = parts[-1] if len(parts) >= 3 else class_key

            if subject_name not in subject_stats:
                subject_stats[subject_name] = {
                    "Attended": 0,
                    "Missed": 0,
                    "Total": 0,
                    "Attendance %": 0.0,
                }

            subject_stats[subject_name]["Total"] += 1
            monthly_data[month_key]["Total"] += 1

            if status == "Present":
                subject_stats[subject_name]["Attended"] += 1
                monthly_data[month_key]["Attended"] += 1
            else:
                subject_stats[subject_name]["Missed"] += 1
                if day_abbr in day_missed:
                    day_missed[day_abbr] += 1

    # Calculate percentages
    for subj, stat in subject_stats.items():
        if stat["Total"] > 0:
            stat["Attendance %"] = round((stat["Attended"] / stat["Total"]) * 100, 1)

    monthly_summary = {}
    for m_key, m_info in sorted(monthly_data.items()):
        if m_info["Total"] > 0:
            monthly_summary[m_info["Label"]] = round(
                (m_info["Attended"] / m_info["Total"]) * 100, 1
            )

    return subject_stats, monthly_summary, day_missed


def calculate_and_display_analytics():
    """
    Provides interactive visualizations of real attendance trends.
    """
    students = load_students()
    schedule = load_schedule()
    attendance_data = load_attendance()

    if not students:
        st.info("ℹ️ No student data found. Please add students first in Student Management.")
        return

    subjects_from_schedule = {
        c["subject"]
        for d in schedule.values()
        for c in d
        if isinstance(c, dict) and "subject" in c
    }
    subjects_from_attendance = set()
    if isinstance(attendance_data, dict):
        for classes in attendance_data.values():
            if isinstance(classes, dict):
                for class_key in classes.keys():
                    parts = class_key.split("__")
                    subjects_from_attendance.add(
                        parts[-1] if len(parts) >= 3 else class_key
                    )
    all_subjects = sorted(list(subjects_from_schedule | subjects_from_attendance))

    if not all_subjects:
        st.info(
            "ℹ️ No classes or subjects found. Please add classes in Class Schedule first."
        )
        return

    # Student Selector
    student_options = {f"{s['name']} (Roll: {s['roll_no']})": s for s in students}
    selected_option = st.selectbox(
        "Select Student for Progress Dashboard",
        options=list(student_options.keys()),
        key="analytics_student_select",
    )
    selected_student = student_options[selected_option]
    student_roll = selected_student["roll_no"]

    # Compute real analytics
    subject_stats, monthly_summary, day_missed = compute_student_analytics(
        student_roll, all_subjects, attendance_data
    )

    df_subjects = pd.DataFrame.from_dict(subject_stats, orient="index")
    df_subjects.index.name = "Subject"
    df_subjects = df_subjects.reset_index()

    total_classes = df_subjects["Total"].sum()
    total_attended = df_subjects["Attended"].sum()
    total_missed = df_subjects["Missed"].sum()

    st.markdown(f"## {selected_student['name']}'s Progress Dashboard")
    st.markdown(f"**Roll Number:** `{student_roll}` | **Email:** `{selected_student.get('email', 'N/A')}`")
    st.markdown("---")

    if total_classes == 0:
        st.info(
            f"ℹ️ No attendance records have been logged yet for **{selected_student['name']}**. "
            "Go to **Mark Attendance** to record daily attendance, and comprehensive analytics charts will appear here automatically."
        )
        return

    overall_percent = round((total_attended / total_classes) * 100, 1)

    # --- 1. Summary Reports & Metrics ---
    st.subheader("📚 Summary Reports")
    col_monthly, col_weekly = st.columns(2)

    with col_monthly:
        st.markdown("##### Monthly Attendance Trend")
        if monthly_summary:
            df_monthly = pd.DataFrame(
                list(monthly_summary.items()), columns=["Month", "Attendance %"]
            )
            st.line_chart(df_monthly.set_index("Month")["Attendance %"])
        else:
            st.caption("No monthly data recorded yet.")

    with col_weekly:
        st.markdown("##### Overall Progress Metrics")
        st.metric(
            label="Overall Attendance Percentage",
            value=f"{overall_percent}%",
            delta=f"{'+' if overall_percent >= 75 else '-'}{abs(round(overall_percent - 75, 1))}% vs target (75%)",
        )
        st.metric(label="Total Classes Attended", value=int(total_attended))
        st.metric(label="Total Classes Missed", value=int(total_missed))

    st.markdown("---")

    # --- 2. Subject-wise Attendance Rates ---
    st.subheader("📊 Subject-wise Attendance Rates")
    active_subjects = df_subjects[df_subjects["Total"] > 0]["Subject"].tolist()
    filter_options = active_subjects if active_subjects else all_subjects

    subject_filter = st.multiselect(
        "Filter Subjects for Bar Chart",
        options=filter_options,
        default=filter_options,
        key="analytics_subject_filter",
    )

    df_filtered_subjects = df_subjects[df_subjects["Subject"].isin(subject_filter)]

    if not df_filtered_subjects.empty:
        st.bar_chart(df_filtered_subjects.set_index("Subject")["Attendance %"])
        st.dataframe(
            df_filtered_subjects.sort_values(by="Attendance %", ascending=False),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.warning("No subjects selected or data available for this view.")

    st.markdown("---")

    # --- 3. Attended vs Missed Breakdown ---
    st.subheader("🥧 Attendance Breakdown")
    pie_col_1, pie_col_2 = st.columns(2)

    with pie_col_1:
        st.markdown("##### Attended vs Missed Ratio")
        df_overall_pie = pd.DataFrame(
            {
                "Category": ["Attended", "Missed"],
                "Count": [int(total_attended), int(total_missed)],
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
        st.markdown("##### Most Missed Subjects")
        df_missed = df_subjects[df_subjects["Missed"] > 0].sort_values(
            by="Missed", ascending=False
        ).head(5)
        if not df_missed.empty:
            st.bar_chart(df_missed.set_index("Subject")["Missed"])
        else:
            st.success("🎉 Perfect attendance! No classes missed so far.")

    st.markdown("---")

    # --- 4. Missed Classes by Day of Week ---
    st.subheader("🔥 Missed Classes by Day")
    df_days = pd.DataFrame(
        list(day_missed.items()), columns=["Day", "Missed Count"]
    )
    st.bar_chart(df_days.set_index("Day")["Missed Count"])
