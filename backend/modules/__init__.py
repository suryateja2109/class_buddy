# File: backend/modules/__init__.py
"""Compatibility package aliasing services to legacy modules."""
from backend.services import (
    attendance_logger,
    email_service,
    miss_predictor,
    reminder_sender,
    schedule_manager,
    student_manager,
)
