import streamlit as st
import pandas as pd

st.title("ESG Finance Collector Dashboard")

st.write("Interactive ESG Analytics")

# Load ESG data
data = pd.read_csv("esg_data.csv")

# --- Company comparison section ---
st.subheader("ESG Comparison Across Companies")
st.bar_chart(data.set_index("Company"))

st.divider()

# --- Individual company analysis ---
company = st.selectbox("Select a Company for Detailed View", data["Company"])

selected_data = data[data["Company"] == company]

st.subheader(f"Detailed ESG Scores for {company}")
st.dataframe(selected_data)

st.bar_chart(selected_data.set_index("Company"))
