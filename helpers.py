# File: helpers.py (Final Robust Styling)

import streamlit as st
import re
from datetime import datetime, time


# --- GLOBAL CONSTANTS ---
ACCENT_TEAL = "#1abc9c"
# ------------------------


def apply_styling():
    """
    Applies professional styling, focusing on native button appearance
    and enforcing high contrast.
    """

    accent_color = ACCENT_TEAL
    sidebar_bg_dark = "#111418"
    main_content_bg = "#22272e"
    ACCENT_GREEN = "#6ae0b0"

    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    st.session_state["greeting"] = greeting

    css = f"""
        <style>
        /* Base Styles */
        html, body, [class*="st-"] {{
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            color: #ecf0f1; 
        }}
        
        /* 1. NATIVE SIDEBAR CONTAINER */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg_dark}; 
            border-right: 4px solid {accent_color}; 
        }}
        
        /* 2. CUSTOM NAVIGATION BUTTONS (Simplified Styling) */
        
        .stButton button {{
            width: 100%;
            height: 50px;
            padding: 0 15px;
            font-size: 16px;
            font-weight: 500;
            color: #bdc3c7; 
            background-color: transparent;
            border: none;
            border-radius: 6px;
            text-align: left;
            transition: all 0.2s;
            border-left: 5px solid transparent; 
        }}

        /* Hover effect */
        .stButton button:hover {{
            background-color: rgba(27, 188, 156, 0.1); 
            color: {accent_color};
            border-left: 5px solid {accent_color}; 
        }}

        /* Active State Styling (Relying on Streamlit's internal primary button CSS for active view) */
        /* Since we cannot rely on data-active, the style relies on Streamlit's primary coloring or we skip the aggressive active styling */
        
        /* 3. MAIN CONTENT STYLING */
        .app-header {{ 
            display: none; /* Hide HTML header, relying on view titles */
        }}
        
        .main-content-wrapper {{
            background-color: {main_content_bg};
            padding: 30px 40px;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.7);
            margin-bottom: 20px;
        }}
        
        /* Card and Section Styling */
        .card {{ 
            padding: 20px 0; 
            border-radius: 0; 
            background: transparent; 
            box-shadow: none; 
            margin-bottom: 20px; 
            border-top: 1px solid rgba(255, 255, 255, 0.08); 
        }}
        
        .mobile-banner {{
            background: linear-gradient(135deg, {accent_color}, {ACCENT_GREEN});
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            color: white;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }}

        .toolbar-col {{ display: none; }} 

        </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def card_start(title):
    accent_color = ACCENT_TEAL
    sidebar_bg_dark = "#1c1f24"

    if title == "📊 Global Dashboard":
        st.markdown(
            f"<div class='card right-metrics-card' style='background: {sidebar_bg_dark}; border-left: 5px solid {accent_color}; border-radius: 8px; padding: 15px;'><h3>{title}</h3>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"<div class='card'><h3>{title}</h3>", unsafe_allow_html=True)


def card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def display_status_message():
    # ... (function logic remains unchanged) ...
    if st.session_state.get("status_message"):
        if st.session_state["status_type"] == "success":
            st.success(st.session_state["status_message"])
        elif st.session_state["status_type"] == "error":
            st.error(st.session_state["status_message"])
        st.session_state["status_message"] = None
        st.session_state["status_type"] = None


# ... (rest of helper functions remain unchanged) ...
def build_classes_list(schedule_dict):
    classes = []
    for day in schedule_dict:
        clist = schedule_dict.get(day, [])
        for i, c in enumerate(clist):
            subj = c.get("subject") if isinstance(c, dict) else str(c)
            time_range = c.get("time") if isinstance(c, dict) else ""

            start_time_obj = time(9, 0)
            end_time_obj = time(10, 0)
            try:
                time_parts = time_range.split(" - ")
                if len(time_parts) == 2:
                    start_time_obj = datetime.strptime(time_parts[0], "%I:%M %p").time()
                    end_time_obj = datetime.strptime(time_parts[1], "%I:%M %p").time()
            except:
                pass

            classes.append(
                {
                    "id": f"{day}__{i}__{subj}",
                    "label": f"{subj} — {day} ({time_range})",
                    "day": day,
                    "subject": subj,
                    "time": time_range,
                    "start_time_obj": start_time_obj,
                    "end_time_obj": end_time_obj,
                }
            )
    return classes


def validate_mobile(mobile):
    cleaned = re.sub(r"[\s\-\(\)\+]", "", mobile.strip())
    if cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]
    if not re.match(r"^[6-9]\d{9}$", cleaned):
        return (
            "⚠ Please enter a valid 10-digit mobile number starting with 6, 7, 8, or 9."
        )
    return None


def validate_email(email):
    email_clean = email.strip()
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_pattern, email_clean):
        return "⚠ Please enter a valid email address (e.g., student@rgmcet.edu.in or user@gmail.com)."
    return None

