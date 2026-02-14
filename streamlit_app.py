import streamlit as st
import pandas as pd
import requests
import urllib.parse
from io import StringIO

st.set_page_config(page_title="ESG News & Score", layout="wide")
st.title("ESG News Extractor + ESG Score (GDELT - Stable CSV Mode)")

# --- ESG classification ---
def classify_esg(title: str) -> int:
    title = (title or "").lower()
    env = ["climate", "environment", "pollution", "emissions", "sustainability", "carbon", "green"]
    soc = ["diversity", "labour", "labor", "human rights", "community", "safety", "inclusion"]
    gov = ["governance", "ethics", "corruption", "board", "transparency", "compliance"]

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
    try:
        tone = float(tone)
    except:
        return 0.5
    return max(0.0, min(1.0, (tone + 10) / 20))

# --- ESG score ---
def compute_esg_score(tone, esg_strength):
    tone_norm = normalize_tone(tone)
    esg_norm = (esg_strength or 0) / 3
    return round((0.5 * tone_norm + 0.5 * esg_norm) * 100, 2)

company = st.text_input("Enter company name", "Microsoft")

if st.button("Fetch ESG News"):
    with st.spinner("Fetching ESG news from GDELT (CSV mode)..."):
        
        raw_query = f"{company} AND (sustainability OR environment OR governance OR ethics)"
        encoded_query = urllib.parse.quote(raw_query)

        url = (
            "https://api.gdeltproject.org/api/v2/doc/doc"
            f"?query={encoded_query}&mode=ArtListWithTone&format=csv"
        )

        response = requests.get(url)

        if response.status_code != 200:
            st.error("GDELT request failed.")
            st.stop()

        try:
            df = pd.read_csv(StringIO(response.text), header=None)
        except:
            st.error("GDELT returned invalid CSV. Try again later.")
            st.stop()

        if df.empty:
            st.warning("No ESG articles found for this company.")
            st.stop()

        # Assign column names
        df.columns = [
            "url", "url_mobile", "title", "date", "image",
            "source", "language", "country", "tone"
        ]

        # Clean date
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%dT%H%M%SZ", errors="coerce")

        # ESG classification
        df["esg_strength"] = df["title"].apply(classify_esg)

        # ESG score
        df["esg_score"] = df.apply(
            lambda row: compute_esg_score(row["tone"], row["esg_strength"]),
            axis=1,
        )

        st.subheader(f"ESG Articles & Scores for {company}")
        st.dataframe(df, use_container_width=True)

        # Summary
        st.markdown("### ESG Score Summary")
        st.write(
            f"**Average ESG score:** {df['esg_score'].mean():.2f} "
            f"(based on {len(df)} articles)"
        )

        # Download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download ESG Data as CSV",
            csv,
            f"{company}_esg_news.csv",
            "text/csv",
        )
