import streamlit as st
import requests
import pandas as pd
import urllib.parse
from textblob import TextBlob

st.set_page_config(page_title="ESG News & Score", layout="wide")
st.title("ESG News Extractor + ESG Score (Stable GDELT Search API)")

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

# --- Sentiment using TextBlob ---
def sentiment_score(text):
    try:
        return (TextBlob(text).sentiment.polarity + 1) / 2  # convert -1..1 → 0..1
    except:
        return 0.5

# --- ESG score ---
def compute_esg_score(sentiment, esg_strength):
    esg_norm = (esg_strength or 0) / 3
    return round((0.5 * sentiment + 0.5 * esg_norm) * 100, 2)

company = st.text_input("Enter company name", "Microsoft")

if st.button("Fetch ESG News"):
    with st.spinner("Fetching ESG news from GDELT (stable mode)..."):
        
        raw_query = f"{company} sustainability OR {company} environment OR {company} governance OR {company} ethics"
        encoded_query = urllib.parse.quote(raw_query)

        url = f"https://api.gdeltproject.org/api/v2/doc/search?query={encoded_query}&format=json"

        response = requests.get(url)

        try:
            data = response.json()
        except:
            st.error("GDELT returned invalid data. Try again later.")
            st.stop()

        if "articles" not in data or len(data["articles"]) == 0:
            st.warning("No ESG articles found for this company.")
            st.stop()

        df = pd.DataFrame(data["articles"])

        # Clean date
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # ESG classification
        df["esg_strength"] = df["title"].apply(classify_esg)

        # Sentiment
        df["sentiment"] = df["title"].apply(sentiment_score)

        # ESG score
        df["esg_score"] = df.apply(
            lambda row: compute_esg_score(row["sentiment"], row["esg_strength"]),
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
