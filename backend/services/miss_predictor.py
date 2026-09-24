# File: modules/miss_predictor.py

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
try:
    from backend.services.attendance_logger import load_attendance
except (ImportError, ModuleNotFoundError):
    from .attendance_logger import load_attendance

# Global model and encoder caches
_RANDOM_FOREST_MODEL = None
_ONE_HOT_ENCODER = None


def _extract_roll_feature(roll_no):
    """Safely extracts a numeric feature from any roll number format."""
    s = str(roll_no).strip()
    digits = [c for c in s if c.isdigit()]
    if digits:
        return float(int(digits[-1]))
    if s:
        return float(ord(s[-1]) % 10)
    return 0.0


def _prepare_data_and_train_model(data=None):
    """
    Prepares data and trains the Random Forest Classifier dynamically from attendance logs.
    Features: Roll No Numeric Feature, Subject (categorical), Day of Week (categorical).
    """
    global _RANDOM_FOREST_MODEL, _ONE_HOT_ENCODER

    if data is None:
        data = load_attendance()

    if not data or not isinstance(data, dict):
        _RANDOM_FOREST_MODEL = None
        _ONE_HOT_ENCODER = None
        return None

    # Stores [Roll_Feature, Subject_Name, Day_of_Week, Target_Y]
    raw_data = []

    for date_str, classes in data.items():
        if not isinstance(classes, dict):
            continue
        for class_key, attendance in classes.items():
            if not isinstance(attendance, dict):
                continue
            parts = class_key.split("__")
            day_of_week = parts[0]
            full_subject_name = parts[-1]

            for roll_no, status in attendance.items():
                try:
                    roll_feat = _extract_roll_feature(roll_no)
                    # Target: 1 for Absent, 0 for Present
                    target = 1 if status == "Absent" else 0
                    raw_data.append([roll_feat, full_subject_name, day_of_week, target])
                except Exception:
                    continue

    if not raw_data:
        _RANDOM_FOREST_MODEL = None
        _ONE_HOT_ENCODER = None
        return None

    df = np.array(raw_data, dtype=object)
    y = df[:, 3].astype(int)

    # Scikit-learn requires at least 2 distinct classes to train a classifier
    unique_classes = np.unique(y)
    if len(unique_classes) < 2 or len(y) < 4:
        _RANDOM_FOREST_MODEL = None
        _ONE_HOT_ENCODER = None
        return None

    X_num = df[:, 0].reshape(-1, 1).astype(float)
    X_cat = df[:, [1, 2]]

    # 1. One-Hot Encode categorical features
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    X_encoded = encoder.fit_transform(X_cat)

    # 2. Combine all features
    X_combined = np.hstack((X_num, X_encoded))

    # 3. Train Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_combined, y)

    _ONE_HOT_ENCODER = encoder
    _RANDOM_FOREST_MODEL = model
    return model


def predict_risk(roll_no, subject, day_of_week):
    """
    Predicts whether a student will be Present (0) or Absent (1) using a Random Forest model.
    Returns 0 (Present), 1 (Absent), or None if insufficient training data.
    """
    global _RANDOM_FOREST_MODEL, _ONE_HOT_ENCODER

    # Dynamically train or update model if not ready
    if _RANDOM_FOREST_MODEL is None or _ONE_HOT_ENCODER is None:
        _prepare_data_and_train_model()

    if not roll_no or _RANDOM_FOREST_MODEL is None or _ONE_HOT_ENCODER is None:
        return None

    roll_feat = _extract_roll_feature(roll_no)
    X_num_pred = np.array([[roll_feat]])
    X_cat_pred = np.array([[subject, day_of_week]])

    try:
        X_encoded_pred = _ONE_HOT_ENCODER.transform(X_cat_pred)
    except Exception:
        return None

    X_combined_pred = np.hstack((X_num_pred, X_encoded_pred))

    if X_combined_pred.shape[1] != _RANDOM_FOREST_MODEL.n_features_in_:
        return None

    prediction = _RANDOM_FOREST_MODEL.predict(X_combined_pred)[0]
    return int(prediction)