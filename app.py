import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import time

st.set_page_config(
    page_title="Compressed Air Ring Main Network",
    page_icon="💨",
    layout="wide"
)

st.sidebar.title("Control Center")
st.sidebar.markdown("---")
refresh_rate = st.sidebar.slider("🔄 Auto-Refresh Interval (s)", 2, 30, 10)

# --- Database Connection Logic ---
def run_query(query):
    conn = psycopg2.connect(st.secrets["DATABASE_URL"])
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()
    conn.close()
    return pd.DataFrame(data, columns=columns)

# --- Main Dashboard Body ---
st.title("💨 Compressed Air Live Network Monitor")
st.markdown("Fetching live real-time metrics from Neon Cloud Postgres...")

try:
    df = run_query("SELECT ts, department, tag_name, value FROM compressed_air_readings ORDER BY ts DESC LIMIT 100;")
    if not df.empty:
        st.dataframe(df)
        fig = px.line(df, x="ts", y="value", color="tag_name", title="Live Pressure / Flow Matrix")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Connected to database, but no data records found yet. Ensure simulator script is active!")
except Exception as e:
    st.error(f"Waiting for database metrics connection... Error details: {e}")

time.sleep(refresh_rate)
st.rerun()