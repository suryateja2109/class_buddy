# ClassBuddy 🎓

ClassBuddy is an intelligent class and attendance management platform built with Streamlit and Python. It provides automated predictive absence detection, email notification alerts, class timetable management, and detailed attendance analytics.

---

## 📁 Project Architecture

The codebase is organized into a clean separation of concerns between `frontend` and `backend`:

```text
class_buddy/
├── frontend/
│   ├── app.py                      # Main Streamlit web application
│   ├── helpers.py                  # UI styling, card components & validators
│   ├── __init__.py
│   └── views/                      # Streamlit view modules
│       ├── __init__.py
│       ├── analytics.py            # Analytics dashboard view
│       ├── analytics_ui.py         # Attendance charts & metric computations
│       ├── attendance_logger.py    # Daily class attendance logging view
│       ├── attendance_viewer.py    # Historical attendance viewer
│       ├── class_management.py     # Class timetable creation & management
│       ├── email_dashboard.py      # Alerts, temporary logs & manual reminders
│       ├── miss_predictor.py       # Absence risk predictor view
│       └── student_management.py   # Student registration & roster management
│
├── backend/
│   ├── __init__.py
│   ├── config.py                   # Central paths and environment loading
│   ├── background_scheduler.py     # Background worker for automated absence alerts
│   ├── logic.py                    # Notification history, prediction cache & business logic
│   ├── services/                   # Core business logic & persistence services
│   │   ├── __init__.py
│   │   ├── attendance_logger.py    # Attendance CRUD operations
│   │   ├── email_service.py        # SMTP email alerts & HTML templates
│   │   ├── miss_predictor.py       # ML Random Forest absence prediction model
│   │   ├── reminder_sender.py      # Manual notification dispatcher
│   │   ├── schedule_manager.py     # Class timetable CRUD & collision detection
│   │   └── student_manager.py      # Student roster CRUD operations
│   ├── modules/                    # Backward-compatibility alias layer
│   └── data/                       # Persistent JSON data store
│       ├── attendance.json
│       ├── notification_log.json
│       ├── schedule.json
│       ├── students.json
│       └── temp_predictions.json
│
├── .env                            # Local configuration (never committed to git)
├── .env.example                    # Configuration template
├── .gitignore                      # Git exclusion rules
├── requirements.txt                # Python package dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and provide your email credentials:
```bash
cp .env.example .env
```
Inside `.env`:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@rgmcet.edu.in
SENDER_PASSWORD=your_google_app_password
```

---

## 🖥️ Running the Application

### Launch the Frontend (Streamlit Dashboard)
```bash
streamlit run frontend/app.py
```

### Launch the Background Scheduler (Automated Alerts)
In a separate terminal window:
```bash
python backend/background_scheduler.py
```