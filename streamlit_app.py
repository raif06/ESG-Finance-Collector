import streamlit as st
import requests
import pandas as pd

st.title("ESG News Extractor + ESG Score (GDELT)")

# --- ESG classification ---
def classify_esg(title):
    title = title.lower()
    env = ["climate", "environment", "pollution", "emissions", "sustainability"]
    soc = ["diversity", "labor", "human rights", "community", "safety"]
    gov = ["governance", "ethics", "corruption", "board", "transparency"]

    score = 0
    if any(word in title for word in env):
        score += 1
    if any(word in title for word in soc):
        score += 1
    if any(word in title for word in gov):
        score += 1

    return score

# --- Tone normalization ---
def normalize_tone(tone):
    return (tone + 10) / 20

# --- ESG score ---
def compute_esg_score(tone, esg_strength):
    tone_norm = normalize_tone(tone)
    return round((0.5 * tone_norm + 0.5 * (esg_strength / 3)) * 100, 2)

company = st.text_input("Enter company name", "Microsoft")

if st.button("Fetch ESG News"):
    query = f"{company} AND (sustainability OR environment OR governance OR ethics)"
    url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={query}&mode=ArtList&format=json"

    response = requests.get(url)
    data = response.json()

    if "articles" in data and len(data["articles"]) > 0:
        df = pd.DataFrame(data["articles"], columns=[
            "url", "url_mobile", "title", "date", "image", "source", "language", "country", "tone"
        ])

        df["date"] = pd.to_datetime(df["date"], format="%Y%m%dT%H%M%SZ")

        # Add ESG classification
        df["esg_strength"] = df["title"].apply(classify_esg)

        # Add ESG score
        df["esg_score"] = df.apply(lambda row: compute_esg_score(row["tone"], row["esg_strength"]), axis=1)

        st.subheader(f"ESG Articles + ESG Score for {company}")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download ESG Data as CSV", csv, "esg_data.csv", "text/csv")

    else:
        st.warning("No ESG articles found for this company.")
