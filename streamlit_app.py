import streamlit as st
import pandas as pd
import yfinance as yf

st.title("ESG Finance Collector Dashboard")
st.write("Interactive ESG Analytics")

# ===============================
# Step 1: Define cached ESG fetch
# ===============================
@st.cache_data(show_spinner=True)
def fetch_esg_data(tickers):
    data = pd.DataFrame(columns=["Company", "Environmental", "Social", "Governance"])
    
    for t in tickers:
        company = yf.Ticker(t)
        info = company.info
        try:
            data = pd.concat([data, pd.DataFrame([{
                "Company": info.get("shortName", t),
                "Environmental": info.get("environmentScore", 0),
                "Social": info.get("socialScore", 0),
                "Governance": info.get("governanceScore", 0)
            }])], ignore_index=True)
        except KeyError:
            st.warning(f"ESG data not available for {t}")
    
    data.fillna(0, inplace=True)
    return data

# ===============================
# Step 2: Optional Refresh Button
# ===============================
if st.button("🔄 Refresh ESG Data"):
    st.cache_data.clear()
    st.success("Cache cleared! Reloading data...")

# ===============================
# Step 3: Fetch data
# ===============================
tickers = ["AAPL", "MSFT", "TSLA", "AMZN", "GOOG"]  # Add more tickers here
data = fetch_esg_data(tickers)

# ===============================
# Step 4: Clean and validate
# ===============================
data.columns = data.columns.str.strip()
required_cols = ["Company", "Environmental", "Social", "Governance"]

if not all(col in data.columns for col in required_cols):
    st.error("Dataset must contain columns: Company, Environmental, Social, Governance")
    st.stop()

# ===============================
# Step 5: Calculate ESG Scores, Rank, Grade
# ===============================
data["Overall ESG"] = data[["Environmental", "Social", "Governance"]].mean(axis=1)
data["Rank"] = data["Overall ESG"].rank(ascending=False)

def esg_grade(score):
    if score >= 85:
        return "AAA"
    elif score >= 75:
        return "AA"
    elif score >= 65:
        return "A"
    else:
        return "BBB"

data["ESG Grade"] = data["Overall ESG"].apply(esg_grade)

# ---- Top ESG Company Highlight ----
top_company = data.sort_values("Overall ESG", ascending=False).iloc[0]
st.success(
    f"🏆 Top ESG Company: {top_company['Company']} ({top_company['ESG Grade']})"
)

# ===============================
# VISUAL ANALYTICS
# ===============================

# --- Overall ESG Comparison ---
st.subheader("Overall ESG Comparison")
st.bar_chart(data.set_index("Company")["Overall ESG"])

st.divider()

# --- ESG Ranking Table ---
st.subheader("ESG Ranking")
st.dataframe(
    data.sort_values("Rank")[["Company", "Overall ESG", "ESG Grade", "Rank"]]
)

st.divider()

# --- ESG Pillar Comparison ---
st.subheader("ESG Pillar Comparison")
st.bar_chart(
    data.set_index("Company")[["Environmental", "Social", "Governance"]]
)

st.divider()

# --- Individual Company Analysis ---
company = st.selectbox(
    "Select a Company for Detailed View",
    data["Company"]
)

selected_data = data[data["Company"] == company]

st.subheader(f"Detailed ESG Scores for {company}")
st.dataframe(selected_data)
st.bar_chart(selected_data.set_index("Company"))
