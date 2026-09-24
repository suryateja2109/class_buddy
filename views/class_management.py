

import streamlit as st
import pandas as pd
from datetime import time
from helpers import card_start, card_end, display_status_message, build_classes_list
from logic import update_class, delete_class, save_class


def class_management_view(schedule):
    card_start("📘 Class Management & Schedule")

    display_status_message()

    tab_add, tab_manage = st.tabs(["➕ Add New Class", "👀 Manage Schedule"])

    # --- TAB 1: ADD NEW CLASS (CREATE) ---
    with tab_add:
        st.subheader("Add New Class Schedule Entry")

        day_options = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        with st.form("class_add_form", clear_on_submit=True):
            day = st.selectbox("Day*", day_options, key="add_day")
            subject = st.text_input("Subject Name*", key="add_subject")

            c1, c2 = st.columns(2)
            # Default to reasonable class times
            start_time_default = time(9, 0)
            end_time_default = time(10, 0)

            start_time_obj = c1.time_input(
                "Start Time*", value=start_time_default, key="add_start_time"
            )
            end_time_obj = c2.time_input(
                "End Time*", value=end_time_default, key="add_end_time"
            )

            submitted = st.form_submit_button(
                "Save Class", type="primary", use_container_width=True
            )

            if submitted:
                # Basic validation
                if not subject.strip():
                    st.error("⚠ Please enter a subject name.")
                elif start_time_obj >= end_time_obj:
                    st.error("⚠ Start time must be before end time.")
                else:
                    time_range = f"{start_time_obj.strftime('%I:%M %p')} - {end_time_obj.strftime('%I:%M %p')}"

                    # Call the wrapper function for saving
                    save_class(
                        day, subject.strip(), time_range, start_time_obj, end_time_obj
                    )
                    st.rerun()

    # --- TAB 2: MANAGE SCHEDULE (READ/UPDATE/DELETE) ---
    with tab_manage:
        st.subheader("Current Weekly Schedule (Update/Delete)")
        all_classes = build_classes_list(schedule)

        if not all_classes:
            st.info("No classes scheduled yet.")
        else:
            # 1. SCHEDULE TABLE
            df = pd.DataFrame(all_classes)
            df = df[["day", "subject", "time"]]
            df.columns = ["Day", "Subject", "Time Range"]
            st.dataframe(df, hide_index=True, use_container_width=True)

            # 2. CLASS SELECTION
            class_labels = [c["label"] for c in all_classes]
            sel_label = st.selectbox(
                "Select Class for Action",
                class_labels,
                key="select_class_action_manage",
            )

            selected_class = next(
                (c for c in all_classes if c["label"] == sel_label), None
            )

            if selected_class:
                st.markdown("---")

                # --- DELETE LOGIC SECTION ---
                st.markdown("#### Delete Class")
                current_class_id = selected_class["id"]

                if st.session_state.delete_confirm_class == current_class_id:
                    st.warning(
                        f"Are you sure you want to permanently delete class **{selected_class['subject']}** on **{selected_class['day']}**?"
                    )
                    col_conf_yes, col_conf_no = st.columns(2)

                    if col_conf_yes.button(
                        "Yes, Delete Class",
                        key="confirm_class_delete_yes",
                        type="secondary",
                        use_container_width=True,
                    ):
                        delete_class(
                            selected_class["day"],
                            selected_class["subject"],
                            selected_class["time"],
                        )
                        st.session_state.delete_confirm_class = None
                        st.rerun()

                    if col_conf_no.button(
                        "No, Cancel Delete",
                        key="confirm_class_delete_no",
                        use_container_width=True,
                    ):
                        st.session_state.delete_confirm_class = None
                        st.rerun()
                else:
                    if st.button(
                        f"🔴 Delete Class: {selected_class['subject']} on {selected_class['day']}",
                        key="delete_class_btn",
                        use_container_width=True,
                    ):
                        st.session_state.delete_confirm_class = current_class_id
                        st.rerun()

                st.markdown("---")  # Separator between Delete and Update

                # 3. UPDATE CLASS FORM
                st.markdown("#### Update Class Time")
                with st.form(f"class_update_form_{selected_class['id']}"):

                    old_day = selected_class["day"]
                    old_subject = selected_class["subject"]
                    old_time = selected_class["time"]

                    st.text_input("Day", value=old_day, disabled=True)
                    new_subject = st.text_input(
                        "Subject Name*", value=old_subject, key="update_subject_action"
                    )

                    c3, c4 = st.columns(2)

                    new_start_time = c3.time_input(
                        "Start",
                        value=selected_class["start_time_obj"],
                        key="update_start_time_action",
                    )
                    new_end_time = c4.time_input(
                        "End",
                        value=selected_class["end_time_obj"],
                        key="update_end_time_action",
                    )

                    if st.form_submit_button(
                        "Update Class Details", type="primary", use_container_width=True
                    ):
                        new_time_range = f"{new_start_time.strftime('%I:%M %p')} - {new_end_time.strftime('%I:%M %p')}"

                        if not new_subject.strip():
                            st.error("⚠ Subject name cannot be empty.")
                        elif new_start_time >= new_end_time:
                            st.error("⚠ Start time must be before end time.")
                        elif (
                            new_time_range == old_time
                            and new_subject.strip() == old_subject
                        ):
                            st.warning("ⓘ No change in subject name or timing detected.")
                        else:
                            new_data = {
                                "subject": new_subject.strip(),
                                "time": new_time_range,
                            }

                            update_class(old_day, old_subject, old_time, new_data)
                            st.rerun()

    card_end()
