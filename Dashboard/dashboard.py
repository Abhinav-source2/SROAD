import os
import pandas as pd
import streamlit as st
import plotly.express as px
from pyathena import connect
from pyathena.pandas.util import as_pandas
from dotenv import load_dotenv
import requests  # 👈 NEW: for calling AI agent

# ==========================================================
# 🔧 LOAD ENVIRONMENT VARIABLES
# ==========================================================
load_dotenv()

AWS_ACCESS_KEY = os.getenv("REDACTED")
AWS_SECRET_KEY = os.getenv("AWS_REDACTED")

# NEW REGION
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")

ATHENA_DATABASE = os.getenv("ATHENA_DATABASE", "sroad_analytics")

# NEW BUCKET + ATHENA RESULTS
ATHENA_OUTPUT = os.getenv(
    "ATHENA_OUTPUT_LOCATION",
    "s3://sroad-data-2/sroad-athena-results-2/"
)

DASHBOARD_TITLE = os.getenv("DASHBOARD_TITLE", "SROAD Analytics Dashboard")

# 👇 NEW: AI Agent endpoint
AI_AGENT_URL = os.getenv("AI_AGENT_URL", "http://localhost:8001/ask")

# ==========================================================
# 🚀 STREAMLIT CONFIGURATION
# ==========================================================
st.set_page_config(
    page_title=DASHBOARD_TITLE,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 SROAD – Real-Time Analytics Dashboard")
st.caption("**Live Analytics:** Kafka → S3 → AWS Athena → Streamlit")

# ==========================================================
# 🔗 ATHENA CONNECTION
# ==========================================================
@st.cache_resource
def athena_connection():
    return connect(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        s3_staging_dir=ATHENA_OUTPUT,
        region_name=AWS_REGION,
        work_group="primary"
    )

conn = athena_connection()

# ==========================================================
# 🧭 QUERY EXECUTION HELPER
# ==========================================================
def run_query(sql):
    """Execute SQL on Athena and return as Pandas DataFrame."""
    try:
        df = as_pandas(conn.cursor().execute(sql))
        return df
    except Exception as e:
        st.error(f"❌ Error running query: {e}")
        return pd.DataFrame()

# ==========================================================
# 🧮 SIDEBAR FILTERS
# ==========================================================
st.sidebar.header("🔍 Filters")

source_filter = st.sidebar.multiselect(
    "Select Data Sources:",
    ["batch", "stream", "shopify"],
    default=["batch", "stream", "shopify"]
)

# ==========================================================
# 💰 REVENUE OVERVIEW
# ==========================================================
st.header("💰 Revenue Overview")

query_revenue = f"""
SELECT 
  source,
  ROUND(SUM(total_amount), 2) AS total_revenue,
  COUNT(order_id) AS total_orders
FROM {ATHENA_DATABASE}.unified_orders
WHERE source IN ({','.join(f"'{s}'" for s in source_filter)})
GROUP BY source
ORDER BY total_revenue DESC
"""

df_revenue = run_query(query_revenue)

if df_revenue.empty:
    st.warning("⚠️ No data returned from Athena. Please check your unified_orders table.")
    st.stop()

# Normalize column names
df_revenue.columns = [col.lower() for col in df_revenue.columns]

if 'total_revenue' not in df_revenue.columns:
    possible = [c for c in df_revenue.columns if "revenue" in c]
    if possible:
        df_revenue.rename(columns={possible[0]: "total_revenue"}, inplace=True)

if 'total_orders' not in df_revenue.columns:
    possible = [c for c in df_revenue.columns if "order" in c]
    if possible:
        df_revenue.rename(columns={possible[0]: "total_orders"}, inplace=True)

col1, col2 = st.columns(2)
with col1:
    st.metric("💵 Total Revenue", f"₹{df_revenue['total_revenue'].sum():,.2f}")
with col2:
    st.metric("🧾 Total Orders", f"{int(df_revenue['total_orders'].sum()):,}")

fig = px.bar(
    df_revenue,
    x="source",
    y="total_revenue",
    color="source",
    text_auto=".2s",
    title="Revenue by Data Source"
)
st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# 🕒 DAILY SALES TREND
# ==========================================================
st.header("📅 Daily Sales Trend")

query_trend = f"""
SELECT 
  COALESCE(
    TRY(date_parse(regexp_replace(order_timestamp, '[Zz]|[-+][0-9]{{2}}:[0-9]{{2}}$', ''), '%Y-%m-%dT%H:%i:%s')),
    TRY(date_parse(order_timestamp, '%Y-%m-%d %H:%i:%s')),
    TRY(date_parse(order_timestamp, '%Y-%m-%d'))
  ) AS order_date,
  SUM(total_amount) AS total_revenue
FROM {ATHENA_DATABASE}.unified_orders
GROUP BY 1
ORDER BY 1
"""

df_trend = run_query(query_trend)

if not df_trend.empty:
    fig2 = px.line(df_trend, x="order_date", y="total_revenue",
                   title="Revenue Trend Over Time", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

# ==========================================================
# 🏙️ STATE-WISE PERFORMANCE
# ==========================================================
st.header("🌎 Top States by Revenue")

query_state = f"""
SELECT 
  state,
  ROUND(SUM(total_amount), 2) AS revenue
FROM {ATHENA_DATABASE}.unified_orders
WHERE state IS NOT NULL AND state <> 'Unknown'
GROUP BY state
ORDER BY revenue DESC
LIMIT 10
"""

df_state = run_query(query_state)

if not df_state.empty:
    fig3 = px.bar(df_state, x="state", y="revenue", color="state",
                  text_auto=".2s", title="Top 10 States by Revenue")
    st.plotly_chart(fig3, use_container_width=True)

# ==========================================================
# 🏷️ CATEGORY PERFORMANCE
# ==========================================================
st.header("🛍️ Top Product Categories")

query_cat = f"""
SELECT 
  category,
  ROUND(SUM(total_amount), 2) AS total_revenue
FROM {ATHENA_DATABASE}.unified_orders
WHERE category IS NOT NULL AND category <> 'Unknown'
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10
"""

df_cat = run_query(query_cat)

if not df_cat.empty:
    fig4 = px.pie(df_cat, values="total_revenue", names="category",
                  title="Revenue Distribution by Category", hole=0.4)
    st.plotly_chart(fig4, use_container_width=True)

# ==========================================================
# ⚠️ SIMPLE HIGH-VALUE TRANSACTION ALERTS
# ==========================================================
st.header("🚨 High-Value Transaction Alerts")

query_anomaly = f"""
SELECT 
  order_timestamp,
  total_amount
FROM {ATHENA_DATABASE}.unified_orders
WHERE total_amount > 5000
ORDER BY total_amount DESC
LIMIT 10
"""

df_anom_simple = run_query(query_anomaly)

if not df_anom_simple.empty:
    st.dataframe(df_anom_simple, use_container_width=True)
    st.caption("🧠 These transactions exceed ₹5000 — potential anomalies.")

# ==========================================================
# ⚠️ ADVANCED ANOMALY DETECTION DASHBOARD
# ==========================================================
st.header("⚠️ Anomaly Detection Insights")

st.markdown("""
This section highlights potential outliers or abnormal sales behavior detected from your unified order data.  
Anomalies may indicate fraud, unusual discounts, or sudden spikes in revenue.
""")

# --- Query 1: Fetch anomalies ---
query_anomaly_full = f"""
SELECT 
  u.order_timestamp,
  u.total_amount,
  u.category,
  u.state,
  u.source
FROM {ATHENA_DATABASE}.unified_orders u
JOIN (
  SELECT 
    source,
    category,
    AVG(total_amount) AS mean_val,
    STDDEV(total_amount) AS std_val
  FROM {ATHENA_DATABASE}.unified_orders
  GROUP BY source, category
) stats
  ON u.source = stats.source AND u.category = stats.category
WHERE u.total_amount > stats.mean_val + 3 * stats.std_val
ORDER BY u.total_amount DESC
LIMIT 300
"""

df_anom = run_query(query_anomaly_full)

if df_anom.empty:
    st.warning("✅ No major anomalies detected — data looks healthy!")
else:
    # --- Chart 1: Time-based anomalies ---
    st.subheader("🕒 Revenue Anomalies Over Time")
    df_anom["order_date"] = pd.to_datetime(df_anom["order_timestamp"], errors="coerce")

    fig_anom = px.scatter(
        df_anom,
        x="order_date",
        y="total_amount",
        color="source",
        hover_data=["category", "state"],
        title="Detected Revenue Anomalies (Z-score > 3σ)"
    )
    st.plotly_chart(fig_anom, use_container_width=True)

    # --- Chart 2: Anomalies by Category ---
    st.subheader("🏷️ Top Categories with Anomalies")
    df_cat_anom = (
        df_anom.groupby("category")["total_amount"]
        .count()
        .reset_index()
        .rename(columns={"total_amount": "anomaly_count"})
        .sort_values("anomaly_count", ascending=False)
        .head(10)
    )

    fig_cat = px.bar(
        df_cat_anom,
        x="category",
        y="anomaly_count",
        color="category",
        title="Top 10 Categories Showing Anomalous Activity",
        text_auto=True
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    # --- Chart 3: Anomalies by Source ---
    st.subheader("📦 Anomalies by Data Source")
    df_src_anom = (
        df_anom.groupby("source")["total_amount"]
        .count()
        .reset_index()
        .rename(columns={"total_amount": "anomaly_count"})
    )

    fig_src = px.pie(
        df_src_anom,
        values="anomaly_count",
        names="source",
        title="Anomaly Distribution by Source",
        hole=0.4
    )
    st.plotly_chart(fig_src, use_container_width=True)

    # --- Table: Top 10 Anomalous Orders ---
    st.subheader("🔍 Top 10 Anomalous Orders")
    st.dataframe(df_anom.head(10), use_container_width=True)

st.markdown("---")
st.caption("⚙️ Powered by statistical outlier detection on top of your unified SROAD data")

# ==========================================================
# 🤖 SROAD AI BUSINESS ASSISTANT
# ==========================================================
st.markdown("---")
st.header("🤖 SROAD AI Business Assistant")

st.markdown("""
Ask natural language business questions and let the **SROAD AI Agent**:
- translate them into Athena SQL  
- run them on your `unified_orders` table  
- summarize the insights in plain English  
""")

col_q, col_opts = st.columns([3, 1])

with col_q:
    user_question = st.text_area(
        "Ask a question about revenue, anomalies, customers, products, or channels:",
        height=100,
        placeholder="Examples:\n"
                    "- Which category had the biggest revenue spike in the last 7 days?\n"
                    "- Show me states where COD orders are unusually high.\n"
                    "- Compare Shopify vs synthetic stream revenue in the last 30 days."
    )

with col_opts:
    st.write("Options")
    reference_date = st.date_input(
        "Reference date (optional)",
        help="If set, 'last 7 days' etc. will be anchored to this date."
    )
    use_athena_agent = st.checkbox(
        "Use Athena (agent)",
        value=True,
        help="If disabled, the agent would need an S3-only mode (currently not implemented)."
    )
    max_rows_agent = st.number_input(
        "Max rows",
        min_value=10,
        max_value=500,
        value=150,
        step=10
    )

ask_clicked = st.button("🔎 Ask AI Assistant")

if ask_clicked:
    if not user_question.strip():
        st.warning("Please type a question for the AI assistant.")
    else:
        with st.spinner("Thinking with SROAD AI Agent..."):
            try:
                payload = {
                    "question": user_question.strip(),
                    "use_athena": use_athena_agent,
                    "max_rows": int(max_rows_agent)
                }
                # only send reference_date if selected
                if reference_date:
                    payload["reference_date"] = reference_date.strftime("%Y-%m-%d")

                resp = requests.post(
                    AI_AGENT_URL,
                    json=payload,
                    timeout=180
                )
                if resp.status_code != 200:
                    st.error(f"❌ Agent error: HTTP {resp.status_code} — {resp.text}")
                else:
                    data = resp.json()

                    st.subheader("📜 SQL the Agent Executed")
                    st.code(data.get("sql", "-- no sql returned --"), language="sql")

                    st.subheader("🧠 Business Explanation")
                    st.write(data.get("explanation", "_No explanation returned_"))

                    sample = data.get("sample") or []
                    if sample:
                        st.subheader("📋 Sample Results (first 10 rows)")
                        df_sample = pd.DataFrame(sample)
                        st.dataframe(df_sample, use_container_width=True)
                    else:
                        st.info("The query returned no rows (empty result set).")

                    trend = data.get("trend") or {}
                    if trend and isinstance(trend, dict):
                        anomaly_days = trend.get("anomaly_days") or []
                        if anomaly_days:
                            st.subheader("🚨 Detected Anomalous Days")
                            st.write(", ".join(anomaly_days))
                        else:
                            st.caption("No anomaly days were flagged in this particular query result.")
            except Exception as e:
                st.error(f"❌ Failed to contact AI agent: {e}")

# ==========================================================
# 📊 FOOTER
# ==========================================================
st.markdown("---")
st.caption("Built with ❤️ using Kafka, S3, Athena, Streamlit, and an Agentic AI Layer for SROAD.")
st.caption("© 2025 SROAD")