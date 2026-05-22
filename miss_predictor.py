import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from collections import defaultdict

# --- Global Model and Data Variables ---
_ATTENDANCE_DATA = {
    "2025-10-06": {
        "Monday__0__Full Stack development -I (FSD)": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Present",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Present",
            "23091a32b8": "Absent", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Monday__1__Introduction to Quantum Technologies and Applications(IQTA)": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Present",
            "23091a32h6": "Absent", "23091a32d6": "Present", "23091a3280": "Absent",
            "23091a32b8": "Present", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Monday__2__Entrepreneurship and New Venture Creation(E&VC)": {
            "23091a32g1": "Present", "23091a32g2": "Present", "23091a32h3": "Present",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Absent",
            "23091a32b8": "Absent", "23091a32g0": "Absent", "23091a32g3": "Absent"
        },
        "Monday__3__Machine Learning (ML)": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Absent",
            "23091a32h6": "Present", "23091a32d6": "Present", "23091a3280": "Present",
            "23091a32b8": "Present", "23091a32g0": "Absent", "23091a32g3": "Absent"
        },
        "Monday__4__Operating Systems(OS)": {
            "23091a32g1": "Present", "23091a32g2": "Present", "23091a32h3": "Present",
            "23091a32h6": "Present", "23091a32d6": "Present", "23091a3280": "Present",
            "23091a32b8": "Present", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Monday__5__physics": {
            "23091a32g1": "Absent", "23091a32g2": "Present", "23091a32h3": "Absent",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Absent",
            "23091a32b8": "Present", "23091a32g0": "Absent", "23091a32g3": "Absent"
        },
        "Monday__6__chemistry": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Absent",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Absent",
            "23091a32b8": "Absent", "23091a32g0": "Present", "23091a32g3": "Absent"
        }
    },
    "2025-10-07": {
        "Tuesday__0__Machine Learning Lab (ML LAB)": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Present",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Present",
            "23091a32b8": "Present", "23091a32g0": "Absent", "23091a32g3": "Absent"
        },
        "Tuesday__1__Operating Systems Lab(OS Lab)": {
            "23091a32g1": "Present", "23091a32g2": "Present", "23091a32h3": "Present",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Present",
            "23091a32b8": "Absent", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Tuesday__2__MOOCS/COUNC/SEM": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Absent",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Present",
            "23091a32b8": "Absent", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Tuesday__3__Introduction to Quantum Technologies and Applications(IQTA)": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Present",
            "23091a32h6": "Absent", "23091a32d6": "Present", "23091a3280": "Absent",
            "23091a32b8": "Present", "23091a32g0": "Absent", "23091a32g3": "Absent"
        }
    },
    "2025-10-08": {
        "Wednesday__0__Software Engineering(SE)": {
            "23091a32g1": "Present", "23091a32g2": "Present", "23091a32h3": "Present",
            "23091a32h6": "Absent", "23091a32d6": "Present", "23091a3280": "Present",
            "23091a32b8": "Absent", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Wednesday__1__Full Stack development -I (FSD)": {
            "23091a32g1": "Present", "23091a32g2": "Present", "23091a32h3": "Absent",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Absent",
            "23091a32b8": "Present", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Wednesday__2__MOOCS/COUNC/SEM": {
            "23091a32g1": "Absent", "23091a32g2": "Present", "23091a32h3": "Absent",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Present",
            "23091a32b8": "Present", "23091a32g0": "Present", "23091a32g3": "Absent"
        }
    },
    "2025-10-02": {
        "Thursday__0__Operating Systems(OS)": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Absent",
            "23091a32h6": "Present", "23091a32d6": "Present", "23091a3280": "Present",
            "23091a32b8": "Present", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Thursday__1__Tinkering Lab": {
            "23091a32g1": "Absent", "23091a32g2": "Present", "23091a32h3": "Absent",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Absent",
            "23091a32b8": "Present", "23091a32g0": "Absent", "23091a32g3": "Absent"
        },
        "Thursday__2__Machine Learning (ML)": {
            "23091a32g1": "Present", "23091a32g2": "Present", "23091a32h3": "Present",
            "23091a32h6": "Absent", "23091a32d6": "Absent", "23091a3280": "Present",
            "23091a32b8": "Present", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Thursday__3__MOOCS/COUNC/SEM": {
            "23091a32g1": "Present", "23091a32g2": "Present", "23091a32h3": "Present",
            "23091a32h6": "Present", "23091a32d6": "Present", "23091a3280": "Present",
            "23091a32b8": "Present", "23091a32g0": "Present", "23091a32g3": "Absent"
        }
    },
    "2025-10-03": {
        "Friday__0__Entrepreneurship and New Venture Creation(E&VC)": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Present",
            "23091a32h6": "Absent", "23091a32d6": "Absent", "23091a3280": "Present",
            "23091a32b8": "Present", "23091a32g0": "Absent", "23091a32g3": "Absent"
        },
        "Friday__1__Machine Learning Lab (ML LAB)": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Absent",
            "23091a32h6": "Absent", "23091a32d6": "Present", "23091a3280": "Absent",
            "23091a32b8": "Absent", "23091a32g0": "Absent", "23091a32g3": "Absent"
        },
        "Friday__2__LIB": {
            "23091a32g1": "Present", "23091a32g2": "Present", "23091a32h3": "Absent",
            "23091a32h6": "Absent", "23091a32d6": "Present", "23091a3280": "Absent",
            "23091a32b8": "Absent", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Friday__3__Software Engineering(SE)": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Absent",
            "23091a32h6": "Absent", "23091a32d6": "Present", "23091a3280": "Absent",
            "23091a32b8": "Absent", "23091a32g0": "Present", "23091a32g3": "Absent"
        }
    },
    "2025-10-04": {
        "Saturday__0__Introduction to Quantum Technologies and Applications(IQTA)": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Absent",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Absent",
            "23091a32b8": "Present", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Saturday__1__CA": {
            "23091a32g1": "Present", "23091a32g2": "Present", "23091a32h3": "Absent",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Present",
            "23091a32b8": "Absent", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Saturday__2__Operating Systems(OS)": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Absent",
            "23091a32h6": "Present", "23091a32d6": "Absent", "23091a3280": "Present",
            "23091a32b8": "Present", "23091a32g0": "Present", "23091a32g3": "Absent"
        },
        "Saturday__3__Machine Learning (ML)": {
            "23091a32g1": "Present", "23091a32g2": "Absent", "23091a32h3": "Present",
            "23091a32h6": "Absent", "23091a32d6": "Absent", "23091a3280": "Present",
            "23091a32b8": "Absent", "23091a32g0": "Present", "23091a32g3": "Absent"
        }
    }
}
_RANDOM_FOREST_MODEL = None
_ONE_HOT_ENCODER = None


# --- Training and Prediction Functions ---

def _prepare_data_and_train_model(data):
    """
    Prepares data and trains the Random Forest Classifier.
    Features: Last Roll No Digit (numeric), Subject (categorical), Day of Week (categorical).
    """
    global _ONE_HOT_ENCODER
    
    # Stores [Last_Digit, Subject_Name, Day_of_Week, Target_Y]
    raw_data = [] 
    
    for date in data:
        for class_key, attendance in data[date].items():
            parts = class_key.split("__")
            day_of_week = parts[0]
            full_subject_name = parts[-1] 

            for roll_no, status in attendance.items():
                try:
                    last_digit = int(roll_no[-1])
                    # Target: 1 for Absent, 0 for Present
                    target = 1 if status == "Absent" else 0
                    
                    raw_data.append([last_digit, full_subject_name, day_of_week, target])
                except ValueError:
                    continue 

    if not raw_data:
        return None

    df = np.array(raw_data, dtype=object)
    X_num = df[:, 0].reshape(-1, 1).astype(float)      # Last Digit
    X_cat = df[:, [1, 2]]                              # Subject Name and Day of Week
    y = df[:, 3].astype(int)                           # Target

    # 1. One-Hot Encode the Subject and Day features
    _ONE_HOT_ENCODER = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    X_encoded = _ONE_HOT_ENCODER.fit_transform(X_cat)
    
    # 2. Combine all Features
    X_combined = np.hstack((X_num, X_encoded))

    # 3. Train Model: Use Random Forest Classifier
    # n_estimators=100 (number of trees), class_weight='balanced' handles imbalance.
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_combined, y)
    return model

# Train the model upon script execution
_RANDOM_FOREST_MODEL = _prepare_data_and_train_model(_ATTENDANCE_DATA)


def predict_risk(roll_no, subject, day_of_week):
    """
    Predicts whether a student will be Present (0) or Absent (1) using a Random Forest model.
    """
    global _RANDOM_FOREST_MODEL, _ONE_HOT_ENCODER

    # Check Model Readiness and Roll Number validity
    if not roll_no or not _RANDOM_FOREST_MODEL or not _ONE_HOT_ENCODER:
        return None 

    try:
        last_digit = int(roll_no[-1])
    except ValueError:
        return None 

    # Prepare features for prediction
    X_num_pred = np.array([[last_digit]]) 
    X_cat_pred = np.array([[subject, day_of_week]])

    # Transform Subject and Day using the fitted Encoder
    try:
        X_encoded_pred = _ONE_HOT_ENCODER.transform(X_cat_pred)
    except ValueError:
        return None 

    # Combine and Predict
    X_combined_pred = np.hstack((X_num_pred, X_encoded_pred))
    
    # Check if the feature vector size matches the model's expectation
    if X_combined_pred.shape[1] != _RANDOM_FOREST_MODEL.n_features_in_:
        return None

    # Predict the class (0 or 1)
    prediction = _RANDOM_FOREST_MODEL.predict(X_combined_pred)[0]
    
    return int(prediction)