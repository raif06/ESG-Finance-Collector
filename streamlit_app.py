import streamlit as st
import pandas as pd

st.title("ESG Finance Collector Dashboard")
st.write("Interactive ESG Analytics")

# ---- File Upload Option ----
uploaded_file = st.file_uploader(
    "Upload ESG Dataset (CSV)", type=["csv"]
)

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
else:
    data = pd.read_csv("esg_data.csv")

# ✅ Clean column names
data.columns = data.columns.str.strip()

# ✅ Validate dataset
required_cols = ["Company", "Environmental", "Social", "Governance"]

if not all(col in data.columns for col in required_cols):
    st.error("Dataset must contain columns: Company, Environmental, Social, Governance")
    st.stop()

# ---- Calculate Overall ESG Score ----
data["Overall ESG"] = data[
    ["Environmental", "Social", "Governance"]
].mean(axis=1)

# --- Overall ESG comparison ---
st.subheader("Overall ESG Comparison")
st.bar_chart(data.set_index("Company")["Overall ESG"])

st.divider()

# --- ESG pillar comparison ---
st.subheader("ESG Pillar Comparison")
st.bar_chart(
    data.set_index("Company")[["Environmental","Social","Governance"]]
)

st.divider()

# --- Individual company analysis ---
company = st.selectbox(
    "Select a Company for Detailed View",
    data["Company"]
)

selected_data = data[data["Company"] == company]

st.subheader(f"Detailed ESG Scores for {company}")
st.dataframe(selected_data)

st.bar_chart(selected_data.set_index("Company"))
