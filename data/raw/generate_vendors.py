import pandas as pd
import numpy as np
import random

# Reproducibility
random.seed(42)
np.random.seed(42)

NUM_VENDORS = 10000

industries = ["SaaS", "Cloud", "Payments", "Consulting", "FinTech"]
regions = ["Local", "International"]
incident_severities = ["Low", "Medium", "High"]
data_sensitivities = ["Public", "Internal", "Confidential"]
api_access_levels = ["No Access", "Limited", "Privileged"]
criticality_levels = ["Low", "Medium", "High"]

vendors = []

for i in range(NUM_VENDORS):
        # Compliance applicability
    industry = random.choice(industries)

    # Does the vendor process personal information?
    popia_applicable = random.choices(
        [1, 0],
        weights=[75, 25]
    )[0]

    # Does the vendor handle payment card information?
    pci_dss_applicable = int(
        industry == "Payments"
        or (industry == "FinTech" and random.random() < 0.35)
    )

    incident_count = np.random.poisson(lam=1)
    vendor = {
        "vendor_id": f"V{i+1:03}",
        "vendor_name": f"Vendor_{i+1}",
        "industry": industry,
        "region": random.choice(regions),
        "cve_count": np.random.poisson(lam=5),
        "avg_cve_severity": round(np.random.uniform(0, 10), 2),
        "has_iso27001": random.choice([0, 1]),
        "soc2_compliant": random.choice([0, 1]),
        "popia_applicable": popia_applicable,
        "popia_compliant": random.choice([0, 1]) if popia_applicable else np.nan,
        "pci_dss_applicable": pci_dss_applicable,
        "pci_dss_compliant": random.choice([0, 1]) if pci_dss_applicable else np.nan,
        "incident_count": incident_count,
        "incident_severity": random.choice(incident_severities) if incident_count > 0 else "None",
        "data_sensitivity": random.choice(data_sensitivities),
        "api_access_level": random.choice(api_access_levels),
        "vendor_criticality": random.choice(criticality_levels),
    }
    vendors.append(vendor)

df = pd.DataFrame(vendors)

df.to_csv("vendors.csv", index=False)

print("Synthetic vendor dataset generated: vendors.csv")
