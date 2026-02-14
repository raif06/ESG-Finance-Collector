import streamlit as st
import pandas as pd

st.title("ESG Finance Collector Dashboard")

st.write("Interactive ESG Score Viewer")

# Load ESG data from CSV file
data = pd.read_csv("esg_data.csv")

# Company selector
company = st.selectbox("Select a Company", data["Company"])

# Filter selected company
selected_data = data[data["Company"] == company]

st.subheader(f"ESG Scores for {company}")
st.dataframe(selected_data)

# Chart visualization
st.bar_chart(selected_data.set_index("Company"))
