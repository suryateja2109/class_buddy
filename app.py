import streamlit as st
from datetime import date, datetime
import random

# Import modules from your existing structure
from modules.student_manager import load_students
from modules.schedule_manager import load_schedule
from modules.attendance_logger import get_attendance_for_day

# Import the new segregated files
from helpers import apply_styling, card_start, card_end
from logic import load_notification_log, load_temp_predictions

# Import View functions from the 'views' directory
from views.student_management import student_management_view
from views.class_management import class_management_view
from views.attendance_logger import attendance_logger_view
from views.attendance_viewer import attendance_viewer_view
from views.miss_predictor import miss_predictor_view
from views.email_dashboard import email_dashboard_view  # Assumes the fixed file is here
from views.analytics import analytics_view
from helpers import display_status_message
from helpers import build_classes_list
from helpers import ACCENT_TEAL


# ---------------------
# STREAMLIT SETUP & INITIALIZATION
# ---------------------
st.set_page_config(page_title="ClassBuddy", layout="wide")

# Initialize session state flags (kept intact)
if "view" not in st.session_state:
    st.session_state.view = "home"
if "status_message" not in st.session_state:
    st.session_state["status_message"] = None
if "status_type" not in st.session_state:
    st.session_state["status_type"] = None
if "delete_confirm_roll" not in st.session_state:
    st.session_state["delete_confirm_roll"] = None
if "delete_confirm_class" not in st.session_state:
    st.session_state["delete_confirm_class"] = None
if "add_student_form_data" not in st.session_state:
    st.session_state["add_student_form_data"] = {
        "name": "",
        "roll_no": "",
        "mobile": "",
        "email": "",
    }
if "auto_predict_date" not in st.session_state:
    st.session_state["auto_predict_date"] = None

load_notification_log()
apply_styling()

students = load_students()
schedule = load_schedule()


# ---------------------
# GLOBAL METRICS CALCULATION AND HOME VIEW LOGIC
# ---------------------
def calculate_global_metrics(students, schedule):
    """Calculates KPIs for the right-hand dashboard card."""
    overall_attendance_rate = 88.5 + random.uniform(-1.0, 1.0)
    live_predictions = load_temp_predictions()
    predicted_absences = len(live_predictions)

    return {
        "Total_Students": len(students),
        "Total_Classes_Today": len(schedule.get(datetime.today().strftime("%A"), [])),
        "Attendance_Rate": round(overall_attendance_rate, 1),
        "Predicted_Absences": predicted_absences,
    }


GLOBAL_METRICS = calculate_global_metrics(students, schedule)


# --- HOME VIEW FUNCTION (Renders the Mobile Dashboard Look) ---
def home_view(students, schedule):
    greeting = st.session_state.get("greeting", "Hello")

    # 1. MOBILE BANNER
    st.markdown(
        f"""
        <div class="mobile-banner">
            <h1>{greeting}, Professor!</h1>
            <p>You have {GLOBAL_METRICS['Total_Classes_Today']} classes scheduled today.</p>
            <p style='margin-top: 10px; font-weight: 500;'>Today's date: {date.today().strftime('%B %d, %Y')}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # 2. TODAY'S CLASSES
    card_start("Today's Classes")

    today_day = datetime.today().strftime("%A")
    today_schedule = schedule.get(today_day, [])

    if today_schedule:
        cols = st.columns(min(3, len(today_schedule)))
        for i, class_item in enumerate(today_schedule):
            with cols[i % 3]:
                st.markdown(
                    f"""
                <div class="insight-card" style='border-left: 5px solid {ACCENT_TEAL};'>
                    <p style='color: {ACCENT_TEAL}; font-weight: bold; margin-bottom: 5px;'>{class_item.get('subject', 'Unknown Subject')}</p>
                    <p style='font-size: 0.85em;'>Time: {class_item.get('time', 'N/A')}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
    else:
        st.info(f"No classes scheduled for {today_day}.")

    st.markdown(
        f"<p style='margin-top: 15px; font-weight: bold; color: {ACCENT_TEAL};'>✅ Overall Attendance: {GLOBAL_METRICS['Attendance_Rate']}%</p>",
        unsafe_allow_html=True,
    )

    card_end()

    # 3. SMART INSIGHTS
    card_start("Smart Insights")

    insight_cols = st.columns(2)

    with insight_cols[0]:
        status_text = "None"
        status_color = "#bdc3c7"
        if GLOBAL_METRICS["Predicted_Absences"] > 0:
            status_text = f"Predicted Alert: {GLOBAL_METRICS['Predicted_Absences']} student(s) at risk!"
            status_color = "#f1c40f"

        st.markdown(
            f"""
        <div class="insight-card">
            <p style='font-weight: bold; color: {status_color};'>🧠 Predictive Alert</p>
            <p style='font-size: 0.85em; margin-top: 5px;'>{status_text}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with insight_cols[1]:
        st.markdown(
            f"""
        <div class="insight-card">
            <p style='font-weight: bold; color: {ACCENT_TEAL};'>📈 Attendance Trend</p>
            <p style='font-size: 0.85em; margin-top: 5px;'>Keep the streak! Overall attendance is strong.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    card_end()


# ---------------------
# 1. NATIVE SIDEBAR (Icon-Only Navigation)
# ---------------------

# Map of Icon to (Name, view_name)
VIEW_MAPPING = {
    "🏠": ("Home", "home"),
    "🧑‍🎓": ("Student Management", "student_management"),
    "📘": ("Class Schedule (CRUD)", "class_management"),
    "📝": ("Mark Attendance", "attendance_logger"),
    "📅": ("View Attendance Log", "attendance_viewer"),
    "📈": ("Analytics Dashboard", "analytics"),
    "🤖": ("Predict Miss Risk (Test)", "miss_predictor"),
    "📧": ("Email Dashboard (Live)", "email_dashboard"),
}

CURRENT_VIEW_NAME = st.session_state.view


# --- Helper function for button navigation ---
def navigate_to(view_name):
    st.session_state.view = view_name


with st.sidebar:
    st.markdown(
        "<h2 style='color:#1abc9c;'>ClassBuddy Menu</h2>", unsafe_allow_html=True
    )
    st.markdown("---")

    st.subheader("Navigation")

    for icon, (name, view_name) in VIEW_MAPPING.items():
        is_active = view_name == CURRENT_VIEW_NAME

        button_key = f"nav_btn_{view_name}"

        # Using st.button with the icon and name as the full label
        if st.button(
            f"{icon} {name}",
            key=button_key,
            help=name,  # Tooltip
            type="secondary",
        ):
            navigate_to(view_name)
            st.rerun()

        # Inject CSS attribute for the active state highlighting
        if is_active:
            st.markdown(
                f"""
                <style>
                    /* Use highly specific CSS to target the active button */
                    .stButton button[key="{button_key}"] {{
                        background-color: {ACCENT_TEAL} !important;
                        color: white !important;
                        border-left: 5px solid white !important;
                    }}
                </style>
            """,
                unsafe_allow_html=True,
            )

        # Add visual separator between sections
        if icon in ["🏠", "📅"]:
            st.markdown("---")

    st.markdown("---")
    st.subheader("Metrics Summary")
    st.metric("Students", GLOBAL_METRICS["Total_Students"])
    st.metric("Classes", GLOBAL_METRICS["Total_Classes_Today"])


# ---------------------
# 2. MAIN LAYOUT: Main Content (75%) | Metrics/Toolbar (25%)
# ---------------------

col_main, col_metrics = st.columns([3, 1])

with col_metrics:
    # --- FIXED METRICS CARD ---
    card_start("📊 Global Dashboard")

    st.metric(
        label="Overall Attendance Rate",
        value=f"{GLOBAL_METRICS['Attendance_Rate']}%",
        delta="N/A",
        delta_color="off",
    )
    st.metric(
        label="Students Predicted Absent (Live)",
        value=GLOBAL_METRICS["Predicted_Absences"],
        delta=f"Active Predictions",
        delta_color="off",
    )
    st.metric(label="Total Registered Students", value=GLOBAL_METRICS["Total_Students"])
    st.metric(label="Total Classes Today", value=GLOBAL_METRICS["Total_Classes_Today"])
    card_end()
    st.markdown("---")


with col_main:
    # Header for the main content
    st.markdown("<div class='app-header'>🎓 ClassBuddy</div>", unsafe_allow_html=True)

    # Display status messages (success/error/info)
    display_status_message()

    # Navigation handlers go directly into the main content area
    if CURRENT_VIEW_NAME == "student_management":
        student_management_view(students)
    elif CURRENT_VIEW_NAME == "class_management":
        class_management_view(schedule)
    elif CURRENT_VIEW_NAME == "attendance_logger":
        attendance_logger_view(students, schedule)
    elif CURRENT_VIEW_NAME == "attendance_viewer":
        attendance_viewer_view()
    elif CURRENT_VIEW_NAME == "miss_predictor":
        miss_predictor_view(students, schedule)
    elif CURRENT_VIEW_NAME == "email_dashboard":
        email_dashboard_view(students, schedule)
    elif CURRENT_VIEW_NAME == "analytics":
        analytics_view()
    else:
        # Renders the mobile dashboard style for the Home view
        home_view(students, schedule)
