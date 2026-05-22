# File: views/analytics.py

import streamlit as st
from helpers import card_start, card_end

# Correct import path for the function defined in the modules folder
from modules.analytics_ui import calculate_and_display_analytics


def analytics_view():
    """
    Renders the Analytics dashboard using the function from the modules folder.
    """
    card_start("📈 Attendance Analytics & Reporting")

    # Call the main analysis and display function
    calculate_and_display_analytics()

    if st.button("⬅ Back to Home", key="back_from_analytics"):
        st.session_state.view = "home"
        st.rerun()

    card_end()
