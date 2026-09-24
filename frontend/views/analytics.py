# File: views/analytics.py

try:
    from frontend.helpers import card_start, card_end
    from frontend.views.analytics_ui import calculate_and_display_analytics
except (ImportError, ModuleNotFoundError):
    from helpers import card_start, card_end
    try:
        from .analytics_ui import calculate_and_display_analytics
    except ImportError:
        from views.analytics_ui import calculate_and_display_analytics


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
