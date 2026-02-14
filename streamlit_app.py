import streamlit as st
import pandas as pd

st.title("ESG Finance Collector Dashboard")

st.write("Example ESG visualization")

# Sample ESG data (temporary demo)
data = pd.DataFrame({
    "Company": ["Apple", "Microsoft", "Tesla", "Amazon"],
    "ESG Score": [82, 88, 74, 79]
})

st.bar_chart(data.set_index("Company"))
