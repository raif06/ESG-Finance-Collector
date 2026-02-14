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

    if "articles" in data and len(data["articles"]) > 0:
        df = pd.DataFrame(data["articles"], columns=[
            "url", "url_mobile", "title", "date", "image", "source", "language", "country"
        ])

        df["date"] = pd.to_datetime(df["date"], format="%Y%m%dT%H%M%SZ")

        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download ESG Data as CSV", csv, "esg_data.csv", "text/csv")

    else:
        st.warning("No ESG articles found for this company.")
