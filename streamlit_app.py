import streamlit as st
import pandas as pd

st.title("ESG Finance Collector Dashboard")

st.write("Interactive ESG Score Viewer")

# Example ESG dataset
data = pd.DataFrame({
    "Company": ["Apple", "Microsoft", "Tesla", "Amazon", "Google"],
    "Environmental": [80, 85, 70, 75, 83],
    "Social": [84, 90, 72, 78, 88],
    "Governance": [82, 88, 79, 81, 86]
})

# Company selector
company = st.selectbox("Select a Company", data["Company"])

# Filter selected company
selected_data = data[data["Company"] == company]

st.subheader(f"ESG Scores for {company}")
st.dataframe(selected_data)

# Chart
st.bar_chart(selected_data.set_index("Company"))
