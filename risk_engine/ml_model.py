from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    fbeta_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

df = pd.read_csv(
    Path(__file__).parent.parent / "data" / "processed" / "vendors_scored.csv"
)

categorical_cols = [
    "industry",
    "region",
    "data_sensitivity",
    "api_access_level",
    "vendor_criticality",
    "popia_compliant",
    "pci_dss_compliant",
    "incident_severity",
]

for col in ["popia_compliant", "pci_dss_compliant"]:
    df[col] = df[col].astype("string").fillna("Not Applicable")
df["incident_severity"] = df["incident_severity"].astype("string").fillna("None")

features = categorical_cols + [
    "has_iso27001",
    "soc2_compliant",
    "popia_applicable",
    "pci_dss_applicable",
    "incident_count",
    "cve_count",
    "avg_cve_severity",
]
X = df[features]
y = df["risk_tier"]

X_development, X_test, y_development, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train, X_validation, y_train, y_validation = train_test_split(
    X_development,
    y_development,
    test_size=0.25,
    random_state=43,
    stratify=y_development,
)

preprocessor = ColumnTransformer(
    [("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_cols)],
    remainder="passthrough",
)
model = Pipeline(
    [
        ("preprocessor", preprocessor),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=500,
                max_depth=12,
                min_samples_leaf=3,
                min_samples_split=5,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)
model.fit(X_train, y_train)

high_index = list(model.classes_).index("High")
validation_high_probability = model.predict_proba(X_validation)[:, high_index]
precision, recall, thresholds = precision_recall_curve(
    y_validation == "High", validation_high_probability
)
f2_scores = (
    5 * precision[:-1] * recall[:-1]
    / (4 * precision[:-1] + recall[:-1] + np.finfo(float).eps)
)
high_threshold = float(thresholds[int(np.argmax(f2_scores))])

validation_high_prediction = validation_high_probability >= high_threshold
print("\nValidation High-risk threshold (selected by F2):", round(high_threshold, 3))
print(
    "Validation High-risk precision / recall / F2:",
    round(precision_score(y_validation == "High", validation_high_prediction), 3),
    round(recall_score(y_validation == "High", validation_high_prediction), 3),
    round(fbeta_score(y_validation == "High", validation_high_prediction, beta=2), 3),
)

test_high_probability = model.predict_proba(X_test)[:, high_index]
default_prediction = model.predict(X_test)
threshold_prediction = default_prediction.astype(object)
threshold_prediction[test_high_probability >= high_threshold] = "High"

for name, prediction in [
    ("Default multiclass prediction", default_prediction),
    ("High-recall threshold prediction", threshold_prediction),
]:
    high_actual = y_test == "High"
    high_predicted = prediction == "High"
    print(f"\n===== {name} =====")
    print(
        "High-risk precision / recall / F2:",
        round(precision_score(high_actual, high_predicted, zero_division=0), 3),
        round(recall_score(high_actual, high_predicted, zero_division=0), 3),
        round(fbeta_score(high_actual, high_predicted, beta=2, zero_division=0), 3),
    )
    print("Confusion matrix (rows/columns: High, Low, Medium):")
    print(confusion_matrix(y_test, prediction, labels=["High", "Low", "Medium"]))
    print(
        classification_report(
            y_test,
            prediction,
            labels=["High", "Low", "Medium"],
            target_names=["High", "Low", "Medium"],
            zero_division=0,
        )
    )