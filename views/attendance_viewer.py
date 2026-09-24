
import streamlit as st
import pandas as pd
from datetime import date
from helpers import card_start, card_end, build_classes_list
from modules.student_manager import load_students
from modules.schedule_manager import load_schedule
from modules.attendance_logger import get_attendance_for_day

def attendance_viewer_view():
    card_start("📅 View Attendance")

    all_students = load_students()
    if not all_students:
        st.info("ℹ️ No students found. Please add students first in Student Management.")
        if st.button("⬅ Back to Home", key="back_from_view_att"):
            st.session_state.view = "home"
            st.rerun()
        card_end()
        return

    student_options = {"All Students": None}
    student_options.update(
        {f"{s['name']} (Roll: {s['roll_no']})": s["roll_no"] for s in all_students}
    )
    students_map = {s.get("roll_no"): s.get("name") for s in all_students}

    col_date, col_student = st.columns([1, 2])
    with col_date:
        sel_date = st.date_input("Select Date", value=date.today())
    with col_student:
        sel_name = st.selectbox(
            "Filter by Student", list(student_options.keys()), index=0
        )

    selected_roll_no = student_options[sel_name]

    day_str = sel_date.strftime("%Y-%m-%d")
    attendance_day = get_attendance_for_day(day_str)

    classes_list = build_classes_list(load_schedule())
    id_to_label = {c["id"]: c["label"] for c in classes_list}

    if not attendance_day:
        st.info(f"No attendance records found for **{day_str}**.")
    else:
        found_records = False
        display_data = []

        for class_id, recs in attendance_day.items():
            if class_id in id_to_label:
                class_name = id_to_label[class_id].split(" — ")[0]
            else:
                parts = class_id.split("__")
                class_name = parts[-1] if len(parts) >= 3 else class_id

            for roll, status in recs.items():
                if selected_roll_no is None or roll == selected_roll_no:
                    name = students_map.get(roll, "Unknown")
                    display_data.append({
                        "Date": day_str,
                        "Class": class_name,
                        "Roll No": roll,
                        "Student Name": name,
                        "Status": status
                    })
                    found_records = True

        if display_data:
            df = pd.DataFrame(display_data)
            st.dataframe(df, hide_index=True, use_container_width=True)
        elif not found_records:
            st.info(
                f"No attendance records found for **{sel_name}** on **{day_str}**."
            )

    if st.button("⬅ Back to Home", key="back_from_view_att"):
        st.session_state.view = "home"
        st.rerun()

    card_end()