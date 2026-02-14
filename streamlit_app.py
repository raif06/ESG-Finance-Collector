import streamlit as st
import requests
import pandas as pd

st.title("ESG News Extractor (GDELT)")

company = st.text_input("Enter company name", "Microsoft")

if st.button("Fetch ESG News"):
    query = f"{company} AND (sustainability OR environment OR governance OR ethics)"
    url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={query}&mode=ArtList&format=json"

    response = requests.get(url)
    data = response.json()

    if "articles" in data:
        df = pd.DataFrame(data["articles"])
        st.write(df)
    else:
        st.warning("No ESG articles found for this company.")
