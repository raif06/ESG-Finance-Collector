import streamlit as st
import requests
import pandas as pd
import urllib.parse
from bs4 import BeautifulSoup

st.set_page_config(page_title="ESG News & Score", layout="wide")
st.title("ESG News Extractor + ESG Score (Google News – No API Key Needed)")

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

# --- Simple sentiment ---
def sentiment_score(title: str) -> float:
    title = (title or "").lower()
    positive_words = ["improve", "growth", "positive", "sustainable", "award", "recognition"]
    negative_words = ["risk", "lawsuit", "pollution", "controversy", "violation", "fraud"]

    score = 0.5
    if any(w in title for w in positive_words):
        score += 0.25
    if any(w in title for w in negative_words):
        score -= 0.25

    return max(0.0, min(1.0, score))

# --- ESG score ---
def compute_esg_score(sentiment, esg_strength):
    esg_norm = (esg_strength or 0) / 3
    return round((0.5 * sentiment + 0.5 * esg_norm) * 100, 2)

company = st.text_input("Enter company name", "Microsoft")

if st.button("Fetch ESG News"):
    with st.spinner("Fetching ESG news from Google News..."):

        query = f"{company} sustainability"
        rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"

        response = requests.get(rss_url)
        soup = BeautifulSoup(response.content, "xml")

        items = soup.find_all("item")

        if not items:
            st.warning("No ESG articles found for this company.")
            st.stop()

        titles = [item.title.text for item in items]
        links = [item.link.text for item in items]
        dates = [item.pubDate.text for item in items]

        df = pd.DataFrame({
            "title": titles,
            "url": links,
            "date": dates
        })

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["esg_strength"] = df["title"].apply(classify_esg)
        df["sentiment"] = df["title"].apply(sentiment_score)
        df["esg_score"] = df.apply(
            lambda row: compute_esg_score(row["sentiment"], row["esg_strength"]),
            axis=1,
        )

        st.subheader(f"ESG Articles & Scores for {company}")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download ESG Data as CSV",
            csv,
            f"{company}_esg_news.csv",
            "text/csv",
        )
