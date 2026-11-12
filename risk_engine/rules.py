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
    risk_breakdown = {}

    # --- Cybersecurity (40%) ---
    cyber_score = 0

    # Vulnerability count (20 points)
    if row["cve_count"] > 10:
        cyber_score += 20
        drivers.append("High CVE count")
        risk_breakdown["High CVE count"] = 20
    elif row["cve_count"] > 5:
        cyber_score += 12
        drivers.append("Moderate CVE count")
        risk_breakdown["Moderate CVE count"] = 12

    # Vulnerability severity (10 points)
    if row["avg_cve_severity"] > 7:
        cyber_score += 10
        drivers.append("High CVE severity")
        risk_breakdown["High CVE severity"] = 10
    elif row["avg_cve_severity"] > 4:
        cyber_score += 5
        drivers.append("Moderate CVE severity")
        risk_breakdown["Moderate CVE severity"] = 5

    # API exposure (10 points)
    if row["api_access_level"] == "Privileged":
        cyber_score += 10
        drivers.append("Privileged API access")
        risk_breakdown["Privileged API access"] = 10
    elif row["api_access_level"] == "Limited":
        cyber_score += 5
        drivers.append("Limited API access")
        risk_breakdown["Limited API access"] = 5

    risk_score += cyber_score
    assert 0 <= cyber_score <= 40

    # --- Compliance (30%) ---
    compliance_score = 0

    # POPIA (10 points)
    if row["popia_applicable"] == 1 and row["popia_compliant"] == 0:
        compliance_score += 10
        drivers.append("Non-POPIA compliant")
        risk_breakdown["Non-POPIA compliant"] = 10

    # PCI DSS (8 points)
    if row["pci_dss_applicable"] == 1 and row["pci_dss_compliant"] == 0:
        compliance_score += 8
        drivers.append("Non-PCI DSS compliant")
        risk_breakdown["Non-PCI DSS compliant"] = 8

    # ISO 27001 assurance (6 points)
    if row["has_iso27001"] == 0:
        compliance_score += 6
        drivers.append("Missing ISO 27001 assurance")
        risk_breakdown["Missing ISO 27001 assurance"] = 6

    # SOC 2 assurance (6 points)
    if row["soc2_compliant"] == 0:
        compliance_score += 6
        drivers.append("Missing SOC 2 assurance")
        risk_breakdown["Missing SOC 2 assurance"] = 6

    risk_score += compliance_score
    assert 0 <= compliance_score <= 30

    # --- Business Criticality (20%) ---
    business_score = 0

    # Vendor criticality (10 points)
    if row["vendor_criticality"] == "High":
        business_score += 10
        drivers.append("High vendor criticality")
        risk_breakdown["High vendor criticality"] = 10
    elif row["vendor_criticality"] == "Medium":
        business_score += 5
        drivers.append("Medium vendor criticality")
        risk_breakdown["Medium vendor criticality"] = 5

    # Data sensitivity (10 points)
    if row["data_sensitivity"] == "Confidential":
        business_score += 10
        drivers.append("Processes confidential data")
        risk_breakdown["Processes confidential data"] = 10
    elif row["data_sensitivity"] == "Internal":
        business_score += 5
        drivers.append("Processes internal data")
        risk_breakdown["Processes internal data"] = 5

    risk_score += business_score
    assert 0 <= business_score <= 20

    # --- Incident History (10%) ---
    incident_score = 0

    # Number of previous incidents (6 points)
    if row["incident_count"] >= 3:
        incident_score += 6
        drivers.append("High number of past incidents")
        risk_breakdown["High number of past incidents"] = 6
    elif row["incident_count"] >= 1:
        incident_score += 3
        drivers.append("Previous security incidents")
        risk_breakdown["Previous security incidents"] = 3

    # Severity of incidents (4 points)
    if row["incident_severity"] == "High":
        incident_score += 4
        drivers.append("High-severity security incidents")
        risk_breakdown["High-severity security incidents"] = 4
    elif row["incident_severity"] == "Medium":
        incident_score += 2
        drivers.append("Medium-severity security incidents")
        risk_breakdown["Medium-severity security incidents"] = 2

    risk_score += incident_score
    assert 0 <= incident_score <= 10

    assert 0 <= risk_score <= 100
    return (
    risk_score,
    drivers,
    risk_breakdown,
    cyber_score,
    compliance_score,
    business_score,
    incident_score
)
    

# Apply the scoring
(
    df["risk_score"],
    df["risk_drivers"],
    df["risk_breakdown"],
    df["cyber_score"],
    df["compliance_score"],
    df["business_score"],
    df["incident_score"]
) = zip(*df.apply(compute_vendor_risk, axis=1))
breakdown_totals = df["risk_breakdown"].apply(
    lambda breakdown: sum(breakdown.values())
)

print(
    "Breakdown matches risk score:",
    (breakdown_totals == df["risk_score"]).all()
)

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
print("\nRisk Score Statistics:")
print(df["risk_score"].describe())

print("\nRisk Tier Distribution:")
print(df["risk_tier"].value_counts())

print("\nRisk Tier Percentages:")
print(df["risk_tier"].value_counts(normalize=True) * 100)

print("\nHigh Risk Vendors:")
print(
    df[df["risk_tier"] == "High"][
        ["vendor_id", "risk_score", "risk_drivers"]
    ].to_string(index=False)
)