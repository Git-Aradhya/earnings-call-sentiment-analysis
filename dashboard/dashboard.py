import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="Earnings Call Sentiment Dashboard",
    layout="wide"
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

df = pd.read_csv("final_dataset.csv")

df["earnings_date"] = pd.to_datetime(df["earnings_date"])

# -------------------------------------------------
# TITLE
# -------------------------------------------------

st.title("Earnings Call Sentiment vs. Stock Reaction")

st.markdown("""
This dashboard explores whether the language used during corporate earnings calls
(sentiment, hedging, forward-looking statements and readability)
is associated with short-term stock price reactions.

**Dataset:** 187 earnings calls from 11 U.S. companies.
""")

st.divider()

# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------

st.subheader("Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Earnings Calls",
    len(df)
)

col2.metric(
    "Companies",
    df["ticker"].nunique()
)

col3.metric(
    "Average Sentiment",
    round(df["sentiment_score"].mean(), 3)
)

col4.metric(
    "Average 1-Day Reaction",
    f"{df['reaction_1day'].mean():.2f}%"
)

st.divider()

# -------------------------------------------------
# COMPANY SELECTOR
# -------------------------------------------------

st.header("Company Deep Dive")

selected_ticker = st.selectbox(
    "Select Company",
    sorted(df["ticker"].unique())
)

company_df = (
    df[df["ticker"] == selected_ticker]
    .sort_values("earnings_date")
)

# -------------------------------------------------
# COMPANY METRICS
# -------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Calls",
    len(company_df)
)

col2.metric(
    "Avg Sentiment",
    round(company_df["sentiment_score"].mean(), 3)
)

col3.metric(
    "Avg 1-Day Reaction",
    f"{company_df['reaction_1day'].mean():.2f}%"
)

col4.metric(
    "Avg Earnings Surprise",
    f"{company_df['surprise_pct'].mean():.2f}%"
)

st.divider()

# -------------------------------------------------
# LANGUAGE FEATURES
# -------------------------------------------------

st.subheader("Language Features Over Time")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=company_df["earnings_date"],
    y=company_df["sentiment_score"],
    mode="lines+markers",
    name="Sentiment"
))

fig.add_trace(go.Scatter(
    x=company_df["earnings_date"],
    y=company_df["hedging_pct"],
    mode="lines+markers",
    name="Hedging"
))

fig.add_trace(go.Scatter(
    x=company_df["earnings_date"],
    y=company_df["forward_looking_pct"],
    mode="lines+markers",
    name="Forward Looking"
))

fig.update_layout(
    height=450,
    xaxis_title="Earnings Date",
    yaxis_title="Score"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# STOCK REACTION
# -------------------------------------------------

st.subheader("Stock Reaction Over Time")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=company_df["earnings_date"],
    y=company_df["reaction_1day"],
    mode="lines+markers",
    name="1-Day Reaction"
))

fig.add_trace(go.Scatter(
    x=company_df["earnings_date"],
    y=company_df["reaction_3day"],
    mode="lines+markers",
    name="3-Day Reaction"
))

fig.update_layout(
    height=450,
    xaxis_title="Earnings Date",
    yaxis_title="Return (%)"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# SCATTER
# -------------------------------------------------

st.subheader("Sentiment vs 1-Day Stock Reaction")

fig = px.scatter(
    company_df,
    x="sentiment_score",
    y="reaction_1day",
    hover_data=["earnings_date"],
    trendline="ols",
    title=""
)

fig.update_layout(
    height=500,
    xaxis_title="Sentiment Score",
    yaxis_title="1-Day Stock Reaction (%)"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# CORRELATION HEATMAP
# -------------------------------------------------

st.header("Overall Dataset Insights")

corr_columns = [
    "reaction_1day",
    "reaction_3day",
    "market_reaction_1day",
    "market_reaction_3day",
    "surprise_pct",
    "sentiment_score",
    "hedging_pct",
    "forward_looking_pct",
    "readability_score"
]

corr = df[corr_columns].corr()

fig = px.imshow(
    corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    aspect="auto",
    title="Correlation Heatmap"
)

fig.update_layout(height=650)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# REGRESSION SUMMARY
# -------------------------------------------------

st.header("Regression Findings")

st.success("""
**Key Findings**

• Earnings surprise showed the strongest positive relationship with stock reaction.

• Market return was also an important control variable.

• Sentiment score was not statistically significant after controlling for earnings surprise and market return.

• Hedging and readability had limited explanatory power.

These findings suggest that short-term stock reactions are driven primarily by fundamental information rather than language alone.
""")

# -------------------------------------------------
# DATASET
# -------------------------------------------------

st.header("Dataset Preview")

st.dataframe(
    df[
        [
            "ticker",
            "earnings_date",
            "reaction_1day",
            "reaction_3day",
            "surprise_pct",
            "hedging_pct",
            "forward_looking_pct",
            "readability_score",
            "sentiment_score"
        ]
    ],
    use_container_width=True
)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.divider()

st.caption(
    "Built using Python, Streamlit, Pandas, Plotly, FinBERT and Statsmodels."
)
