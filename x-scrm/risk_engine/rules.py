"""
Rule-based vendor risk scoring logic.
Phase 1 baseline for explainable risk assessment.
"""
import pandas as pd
from pathlib import Path

# Load synthetic vendor data
data_path = Path(__file__).parent.parent / "data" / "raw" / "vendors.csv"
df = pd.read_csv(data_path)

print("First 5 rows of the vendor dataset:")
print(df.head())

def compute_vendor_risk(row):
    """"
    Compute risk score (0-100) and risk drivers for a vendor.
    Returns: (risk_score, risk_drivers)
    """
    risk_score = 0
    drivers = []

    # --- Cybersecurity (40%) ---
    cyber_score = 0
    if row["cve_count"] > 10:
        cyber_score += 25
        drivers.append("High CVE count")
    elif row["cve_count"] > 5:
        cyber_score += 15

    if row["avg_cve_severity"] > 7:
        cyber_score += 15
        drivers.append("High CVE severity")
    elif row["avg_cve_severity"] > 4:
        cyber_score += 10

    if row["has_iso27001"] == 0 or row["soc2_compliant"] == 0:
        cyber_score += 10
        drivers.append("Missing ISO/SOC2 certification")

    risk_score += cyber_score

    # --- Compliance (30%) ---
    compliance_score = 0
    if row["popia_compliant"] == 0:
        compliance_score += 20
        drivers.append("Non-POPIA compliant")
    risk_score += compliance_score

    # --- Business Criticality (20%) ---
    business_score = 0
    if row["vendor_criticality"] == "High" and row["api_access_level"] == "Privileged":
        business_score += 20
        drivers.append("High criticality + privileged access")
    elif row["vendor_criticality"] == "High":
        business_score += 10
    risk_score += business_score

    # --- Incident History (10%) ---
    incident_score = 0
    if row["incident_count"] >= 2:
        incident_score += 10
        drivers.append("Multiple past incidents")
    risk_score += incident_score

    # Ensure score <= 100
    risk_score = min(risk_score, 100)

    return risk_score, drivers

# Apply the scoring
df["risk_score"], df["risk_drivers"] = zip(*df.apply(compute_vendor_risk, axis = 1))

# Define risk tier based on score
def risk_tier(score):
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"

df["risk_tier"] = df["risk_score"].apply(risk_tier)

# Save results
output_path = Path(__file__).parent.parent / "data" / "processed" / "vendors_scored.csv"
df.to_csv(output_path, index = False)

print("Rule-based risk scoring completed. Results saved to vendors_scored.csv")