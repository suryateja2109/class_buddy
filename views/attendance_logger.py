import streamlit as st
import pandas as pd
from datetime import date
from helpers import card_start, card_end, build_classes_list
from modules.attendance_logger import get_attendance_for_day, save_class_attendance


def attendance_logger_view(students, schedule_data):
    card_start("📝 Attendance Logger")

    if not students:
        st.info("ℹ️ No students found. Please add students first in Student Management.")
        card_end()
        return

    classes = build_classes_list(schedule_data)
    if not classes:
        st.info("ℹ️ No classes scheduled yet. Add a class in Class Schedule first.")
        card_end()
        return

    col_date_select, col_class_select = st.columns([1, 2])

    with col_date_select:
        if "log_date_select_value" not in st.session_state:
            st.session_state["log_date_select_value"] = date.today()

        selected_log_date = st.date_input(
            "Select Date",
            value=st.session_state["log_date_select_value"],
            key="log_date_select",
        )
        st.session_state["log_date_select_value"] = selected_log_date

    target_day_name = selected_log_date.strftime("%A")
    available_classes = [c for c in classes if c["day"] == target_day_name]

    if not available_classes:
        st.info(
            f"ℹ️ No classes scheduled for {selected_log_date.strftime('%A, %B %d, %Y')}."
        )
        card_end()
        return

    class_labels = [c["label"] for c in available_classes]

    if (
        "sel_label_value" not in st.session_state
        or st.session_state["sel_label_value"] not in class_labels
    ):
        st.session_state["sel_label_value"] = class_labels[0]

    with col_class_select:
        try:
            current_index = class_labels.index(st.session_state["sel_label_value"])
        except ValueError:
            current_index = 0

        sel_label = st.selectbox(
            "Select Class", class_labels, index=current_index, key="sel_label"
        )
        st.session_state["sel_label_value"] = sel_label

    sel_index = class_labels.index(sel_label)
    selected_class = available_classes[sel_index]

    class_id = selected_class["id"]
    today_str = selected_log_date.strftime("%Y-%m-%d")

    existing_att_for_day = get_attendance_for_day(today_str)
    existing_for_class = (
        existing_att_for_day.get(class_id, {}) if existing_att_for_day else {}
    )
    attendance_done = bool(existing_for_class)

    students_map = {s.get("roll_no"): s.get("name") for s in students}

    edit_mode_key = f"edit_mode__{class_id}__{today_str}"
    is_editing = st.session_state.get(edit_mode_key, False)
    is_locked = attendance_done and not is_editing

    if attendance_done and not is_editing:
        col_info, col_unlock = st.columns([3, 1])
        with col_info:
            st.success(f"✅ Attendance is already logged for this class on {today_str}.")
        with col_unlock:
            if st.button("✏️ Edit Attendance", key=f"unlock_btn_{class_id}_{today_str}", use_container_width=True):
                st.session_state[edit_mode_key] = True
                st.rerun()

    form_title = (
        f"✏️ Update Attendance for **{sel_label}** ({today_str})"
        if is_editing
        else f"Mark Attendance for **{sel_label}** ({today_str})"
    )

    with st.form("attendance_form"):
        st.write(form_title)

        for i, s in enumerate(students):
            unique_key = (
                f"att__{class_id}__{s['roll_no']}__{s['name'].replace(' ', '_')}__{i}"
            )

            default_status = existing_for_class.get(s["roll_no"], "Present")
            options = ["Present", "Absent"]
            default_index = 0 if default_status == "Present" else 1

            st.radio(
                label=f"{s['name']} (Roll: {s['roll_no']})",
                options=options,
                index=default_index,
                key=unique_key,
                horizontal=True,
                disabled=is_locked,
            )

        col_save, col_cancel = st.columns(2)
        submit_label = "🔄 Update Attendance" if is_editing else "💾 Save Attendance"
        save_att = col_save.form_submit_button(
            submit_label,
            disabled=is_locked,
            type="primary",
            use_container_width=True,
        )

        cancel_att = col_cancel.form_submit_button(
            "Back to Home", use_container_width=True
        )

        if save_att:
            status_map = {}
            for i, s in enumerate(students):
                unique_key = f"att__{class_id}__{s['roll_no']}__{s['name'].replace(' ', '_')}__{i}"
                status_map[s["roll_no"]] = st.session_state.get(unique_key, "Present")

            save_class_attendance(class_id, status_map, today_str)
            st.session_state[edit_mode_key] = False
            st.success(f"✅ Attendance successfully saved for {today_str}!")
            st.rerun()

        if cancel_att:
            st.session_state[edit_mode_key] = False
            st.session_state.view = "home"
            st.rerun()

    # Summary table
    attendance_today = get_attendance_for_day(today_str)
    current_class_attendance = attendance_today.get(class_id, {})

    if current_class_attendance:
        st.markdown(f"### Current Log for {sel_label} on {today_str}")

        data = []
        present_count = 0
        for roll, status in current_class_attendance.items():
            name = students_map.get(roll, "Unknown Student")
            data.append({"Roll No": roll, "Student Name": name, "Status": status})
            if status == "Present":
                present_count += 1

        total_marked = len(current_class_attendance)
        pct = round((present_count / total_marked) * 100, 1) if total_marked > 0 else 0.0

        m1, m2, m3 = st.columns(3)
        m1.metric("Present", present_count)
        m2.metric("Absent", total_marked - present_count)
        m3.metric("Attendance %", f"{pct}%")

        df_att = pd.DataFrame(data)
        st.dataframe(df_att, hide_index=True, use_container_width=True)
    else:
        st.info(f"No attendance recorded yet for this class on {today_str}.")

    card_end()
