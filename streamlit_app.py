import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="ESG News & Score", layout="wide")
st.title("ESG News Extractor + ESG Score (GDELT)")

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
def normalize_tone(tone: float) -> float:
    # GDELT tone is roughly in [-10, +10]
    if tone is None:
        return 0.5
    return max(0.0, min(1.0, (tone + 10) / 20))

# --- ESG score ---
def compute_esg_score(tone: float, esg_strength: int) -> float:
    tone_norm = normalize_tone(tone)
    esg_norm = (esg_strength or 0) / 3  # 0–1
    return round((0.5 * tone_norm + 0.5 * esg_norm) * 100, 2)

company = st.text_input("Enter company name", "Microsoft")

if st.button("Fetch ESG News"):
    with st.spinner("Fetching ESG news from GDELT..."):
        query = f"{company} AND (sustainability OR environment OR governance OR ethics)"
        url = (
            "https://api.gdeltproject.org/api/v2/doc/doc"
            f"?query={query}&mode=ArtListWithTone&format=json"
        )

        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"GDELT request failed with status code {response.status_code}")
        else:
            data = response.json()

            if "articles" in data and len(data["articles"]) > 0:
                # ArtListWithTone returns: url, url_mobile, title, date, image, source, language, country, tone
                df = pd.DataFrame(
                    data["articles"],
                    columns=[
                        "url",
                        "url_mobile",
                        "title",
                        "date",
                        "image",
                        "source",
                        "language",
                        "country",
                        "tone",
                    ],
                )

                # Clean date
                df["date"] = pd.to_datetime(df["date"], format="%Y%m%dT%H%M%SZ", errors="coerce")

                # ESG strength from title
                df["esg_strength"] = df["title"].apply(classify_esg)

                # ESG score
                df["esg_score"] = df.apply(
                    lambda row: compute_esg_score(row["tone"], row["esg_strength"]),
                    axis=1,
                )

                st.subheader(f"ESG Articles & Scores for {company}")
                st.dataframe(df, use_container_width=True)

                # Simple summary
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
            else:
                st.warning("No ESG articles found for this company.")
