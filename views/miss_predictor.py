import streamlit as st
from datetime import date
from helpers import card_start, card_end
from modules import miss_predictor
from modules.student_manager import load_students
from modules.schedule_manager import load_schedule


def miss_predictor_view(students_list, schedule_data):
    card_start("🤖 Miss Predictor (Manual Test)")

    student_info = {s["roll_no"]: s for s in students_list}

    if not students_list or not schedule_data:
        st.info("⚠ Please add students and classes first.")
    else:
        roll = st.selectbox("Select Student", [s["roll_no"] for s in students_list])
        subj = st.selectbox(
            "Select Subject",
            list({c["subject"] for d in schedule_data.values() for c in d}),
        )

        selected_date = st.date_input("Select Date", value=date.today())
        day_of_week = selected_date.strftime("%A")

        if st.button("Predict Miss Risk"):
            # Only predict the risk
            result = miss_predictor.predict_risk(roll, subj, day_of_week)

            if result is None:
                st.error(
                    "⚠ Not enough data to predict. Ensure some attendance logs exist for this student/subject."
                )
            else:
                risk_label = "Absent" if result == 1 else "Present"
                st.metric(
                    "Predicted Status",
                    f"{risk_label} (on {day_of_week})",
                )
                if result == 1:
                    st.warning(
                        "🚨 Prediction is **ABSENT**. The automated scheduler will handle alerts based on class time."
                    )

    if st.button("⬅ Back to Home", key="back_from_predictor"):
        st.session_state.view = "home"
        st.rerun()

    card_end()