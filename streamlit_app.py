import streamlit as st
import pandas as pd
import yfinance as yf

# =====================================
# PAGE SETUP
# =====================================
st.set_page_config(page_title="ESG Finance Collector", layout="wide")

st.title("🌍 ESG Finance Collector Dashboard")
st.write("Live ESG Analytics from Public Financial Data")

# =====================================
# FETCH LIVE ESG DATA
# =====================================

st.subheader("Fetching Live ESG Data from Public Source")

# Companies to analyze (you can add more later)
tickers = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL"
}

esg_list = []

for company, ticker in tickers.items():
    try:
        stock = yf.Ticker(ticker)
        esg = stock.sustainability

        # Some companies may not have ESG data
        if esg is not None:
            esg_list.append({
                "Company": company,
                "Environmental": float(esg.loc["environmentScore"][0]),
                "Social": float(esg.loc["socialScore"][0]),
                "Governance": float(esg.loc["governanceScore"][0])
            })

    except Exception:
        continue

data = pd.DataFrame(esg_list)

# Safety check
if data.empty:
    st.error("ESG data could not be fetched right now. Try refreshing later.")
    st.stop()

# =====================================
# ESG CALCULATIONS
# =====================================

# Overall ESG Score
data["Overall ESG"] = data[
    ["Environmental", "Social", "Governance"]
].mean(axis=1)

# Ranking
data["Rank"] = data["Overall ESG"].rank(ascending=False)

# ESG Grade System
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

# =====================================
# TOP ESG COMPANY HIGHLIGHT
# =====================================

top_company = data.sort_values("Overall ESG", ascending=False).iloc[0]

st.success(
    f"🏆 Top ESG Company: {top_company['Company']} "
    f"({top_company['ESG Grade']})"
)

# =====================================
# VISUAL ANALYTICS
# =====================================

st.divider()

# Overall ESG comparison
st.subheader("Overall ESG Comparison")
st.bar_chart(data.set_index("Company")["Overall ESG"])

st.divider()

# ESG Ranking Table
st.subheader("ESG Ranking")
st.dataframe(
    data.sort_values("Rank")[["Company", "Overall ESG", "ESG Grade", "Rank"]],
    use_container_width=True
)

st.divider()

# ESG Pillar comparison
st.subheader("ESG Pillar Comparison")
st.bar_chart(
    data.set_index("Company")[["Environmental", "Social", "Governance"]]
)

st.divider()

# Individual company analysis
company = st.selectbox(
    "Select a Company for Detailed View",
    data["Company"]
)

selected_data = data[data["Company"] == company]

st.subheader(f"Detailed ESG Scores — {company}")
st.dataframe(selected_data, use_container_width=True)

st.bar_chart(selected_data.set_index("Company"))
