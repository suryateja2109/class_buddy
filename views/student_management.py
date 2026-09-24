import streamlit as st
import pandas as pd
from helpers import (
    card_start,
    card_end,
    display_status_message,
    validate_mobile,
    validate_email,
)
from logic import save_student, update_student, delete_student


def student_management_view(students):
    # --- 1. INITIALIZE SESSION STATE FOR DELETE CONFIRMATION ---
    if "delete_confirm_roll" not in st.session_state:
        st.session_state.delete_confirm_roll = None

    card_start("🧑‍🎓 Student Management")

    display_status_message()

    tab_add, tab_manage = st.tabs(["➕ Add New Student", "👀 Manage Students"])

    # ----------------------------- TAB: ADD STUDENT -----------------------------
    with tab_add:
        st.subheader("Add New Student Record")
        with st.form("student_add_form_final", clear_on_submit=True):
            name = st.text_input("Student Name*", key="input_name_add_final")
            roll_no = st.text_input("Roll Number*", key="input_roll_add_final")
            c3, c4 = st.columns(2)
            mobile = c3.text_input("Mobile Number*", key="input_mobile_add_final")
            email = c4.text_input("Email*", key="input_email_add_final")
            submitted = st.form_submit_button(
                "Save Student", type="primary", use_container_width=True
            )

        if submitted:
            mobile_error = validate_mobile(mobile)
            email_error = validate_email(email)
            if not all([name.strip(), roll_no.strip(), mobile.strip(), email.strip()]):
                st.error("⚠ Please fill all fields.")
            elif mobile_error:
                st.error(mobile_error)
            elif email_error:
                st.error(email_error)
            else:
                save_student(
                    name.strip(), roll_no.strip(), mobile.strip(), email.strip()
                )
                st.rerun()

    # -------------------------- TAB: MANAGE STUDENTS --------------------------
    with tab_manage:
        st.subheader("Existing Students (Update/Delete)")

        if not students:
            st.info("No students found.")
        else:
            df = pd.DataFrame(students)
            df = df[["name", "roll_no", "mobile", "email"]]
            st.dataframe(df, hide_index=True, use_container_width=True)

            st.markdown("---")
            roll_options = [s["roll_no"] for s in students]
            selected_roll = st.selectbox(
                "Select Student for Action",
                roll_options,
                format_func=lambda r: next(
                    (f"{s['name']} (Roll: {s['roll_no']})" for s in students if s["roll_no"] == r),
                    r,
                ),
                key="select_student_roll",
            )

            if selected_roll:
                selected_student = next(
                    (s for s in students if s["roll_no"] == selected_roll), None
                )

                if selected_student:
                    # ----------- UPDATE FORM -----------
                    st.markdown("#### Update Student")
                    with st.form(f"update_form_{selected_roll}"):
                        c1, c2 = st.columns(2)
                        new_name = c1.text_input(
                            "Name", value=selected_student["name"], key="update_name"
                        )
                        new_mobile = c2.text_input(
                            "Mobile",
                            value=selected_student["mobile"],
                            key="update_mobile",
                        )
                        new_email = st.text_input(
                            "Email", value=selected_student["email"], key="update_email"
                        )

                        if st.form_submit_button(
                            "Update Details", type="primary", use_container_width=True
                        ):
                            mobile_update_error = validate_mobile(new_mobile)
                            email_update_error = validate_email(new_email)
                            if not new_name.strip():
                                st.error("⚠ Student name cannot be empty.")
                            elif mobile_update_error:
                                st.error(mobile_update_error)
                            elif email_update_error:
                                st.error(email_update_error)
                            else:
                                update_student(
                                    selected_roll,
                                    {
                                        "name": new_name.strip(),
                                        "mobile": new_mobile.strip(),
                                        "email": new_email.strip().lower(),
                                    },
                                )
                                st.rerun()

                    st.markdown("---")

                    # ----------- DELETE STUDENT LOGIC -----------
                    st.markdown("#### Delete Student")

                    if st.session_state.delete_confirm_roll == selected_roll:
                        st.warning(
                            f"Are you sure you want to permanently delete student **{selected_roll}**?"
                        )
                        col_conf_yes, col_conf_no = st.columns(2)

                        # Confirm Deletion
                        if col_conf_yes.button(
                            "✅ Yes, Delete",
                            key="confirm_delete_yes",
                            use_container_width=True,
                        ):
                            delete_student(selected_roll)
                            st.session_state.delete_confirm_roll = None
                            st.rerun()

                        # Cancel Deletion
                        if col_conf_no.button(
                            "No, Cancel",
                            key="confirm_delete_no",
                            use_container_width=True,
                        ):
                            st.session_state.delete_confirm_roll = None
                            st.rerun()

                    else:
                        # Initial Delete Button
                        if st.button(
                            f"🔴 Delete Student {selected_roll}",
                            key=f"delete_btn_{selected_roll}",
                            use_container_width=True,
                        ):
                            st.session_state.delete_confirm_roll = selected_roll
                            st.rerun()

    card_end()
