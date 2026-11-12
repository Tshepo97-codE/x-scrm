import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import ast
from pathlib import Path

st.set_page_config(page_title="X-SCRM DASHBOARD", layout="wide")

st.title("X-SCRM -- Vendor Risk Dashboard")
st.subheader("Third-Party Cyber Risk Assessment")

# Load scored data
try:
    data_path = Path(__file__).parent.parent / "data" / "processed" / "vendors_scored.csv"
    df = pd.read_csv(data_path)
except FileNotFoundError:
    st.error(f"Data file not found at {data_path}. Please run the risk scoring script first.")
    st.stop()

df["risk_breakdown"] = df["risk_breakdown"].apply(ast.literal_eval)

# Sidebar filters (applied before any display)
st.sidebar.header("Filter Options")
risk_filter = st.sidebar.multiselect(
    "Select Risk Tier",
    options=sorted(df["risk_tier"].unique()),
    default=sorted(df["risk_tier"].unique())
)

filtered_df = df[df["risk_tier"].isin(risk_filter)]

# Display key metrics at the top
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Vendors", len(filtered_df))
col2.metric("High Risk Vendors", len(filtered_df[filtered_df["risk_tier"] == "High"]))
col3.metric("Average Risk Score", round(filtered_df["risk_score"].mean(), 1))
col4.metric("Critical Vendors", len(filtered_df[filtered_df["vendor_criticality"] == "High"]))

# Filtered vendor table with styling
st.write("### Vendor Risk Overview")
display_df = filtered_df[[
    "vendor_name",
    "industry",
    "risk_score",
    "risk_tier",
    "risk_drivers"
]]
styled_df = display_df.style.map(
    lambda val: "background-color: #ffcccc; color: black" if val == "High" 
    else ("background-color: #ffe6cc; color: black" if val == "Medium" 
    else ("background-color: #ccffcc; color: black" if val == "Low" else "")),
    subset=["risk_tier"]
)
st.dataframe(styled_df)

# Risk distribution chart
st.write("### Risk Tier Distribution")
if len(filtered_df) > 0:
    risk_counts = filtered_df["risk_tier"].value_counts()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = {"High": "#ff6b6b", "Medium": "#ffa500", "Low": "#51cf66"}
    colors = [colors.get(tier, "gray") for tier in risk_counts.index]
    
    ax.bar(risk_counts.index, risk_counts.values, color=colors)
    ax.set_xlabel("Risk Tier")
    ax.set_ylabel("Number of Vendors")
    ax.set_title("Vendor Risk Distribution")
    ax.grid(axis="y", alpha=0.3)
    
    st.pyplot(fig)
else:
    st.info("No vendors match the selected filters.")

# Drill-down view
st.write("### Vendor Detail View")
if len(filtered_df) > 0:
    selected_vendor = st.selectbox(
        "Select Vendor",
        filtered_df["vendor_name"]
    )
    
    vendor_data = filtered_df[filtered_df["vendor_name"] == selected_vendor].iloc[0]

    st.subheader("Risk Component Scores")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Cybersecurity", f"{vendor_data['cyber_score']}/40")
        st.metric("Business Criticality", f"{vendor_data['business_score']}/20")

    with col2:
        st.metric("Compliance", f"{vendor_data['compliance_score']}/30")
        st.metric("Incident History", f"{vendor_data['incident_score']}/10")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Risk Score", vendor_data["risk_score"])
    col2.metric("Risk Tier", vendor_data["risk_tier"])
    col3.metric("Criticality", vendor_data["vendor_criticality"])
    
    st.write("**Risk Drivers:**")
    st.write(vendor_data["risk_drivers"])
    st.write("**Risk Breakdown:**")
    st.json(vendor_data["risk_breakdown"])
else:
    st.info("No vendors available to view details.")