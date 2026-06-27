import streamlit as st
import psycopg2
import pandas as pd
import plotly.graph_objects as go
import time

# Force clean dark theme base layout
st.set_page_config(
    page_title="Compressed Air Network",
    page_icon="💨",
    layout="wide"
)

# Base dark theme styling
st.markdown("""
    <style>
        div[data-testid="stMetricValue"] { font-size: 28px; }
        div[data-testid="stMetricLabel"] { font-size: 14px; color: #A3A3A3; }
        .block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("🎛️ Control Center")
refresh_rate = st.sidebar.slider("🔄 Auto-Refresh Interval (s)", 2, 30, 10)

# --- Define Safety Thresholds ---
CRITICAL_LOW_PRESSURE = 6.0  # Bar
CRITICAL_LOW_FLOW = 200.0    # Nm³/h

# --- Database Connection ---
def run_query(query, params=None):
    conn = psycopg2.connect(st.secrets["DATABASE_URL"])
    with conn.cursor() as cur:
        cur.execute(query, params)
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()
    conn.close()
    return pd.DataFrame(data, columns=columns)

st.title("💨 Compressed Air Ring Main Network")

try:
    # 1. Fetch Latest Global KPI Metrics for the Top Row
    kpi_query = """
        SELECT DISTINCT ON (tag_name) tag_name, value, department 
        FROM compressed_air_readings 
        ORDER BY tag_name, ts DESC;
    """
    df_kpis = run_query(kpi_query)
    
    if not df_kpis.empty:
        cols = st.columns(min(len(df_kpis), 4))
        for idx, row in df_kpis.head(4).iterrows():
            with cols[idx % 4]:
                is_pressure = "PRESSURE" in row['tag_name'].upper()
                unit = " Bar" if is_pressure else " Nm³/h"
                val = row['value']
                
                # Check thresholds to determine status color
                if is_pressure and val < CRITICAL_LOW_PRESSURE:
                    color_style = "#FF4B4B"  # Critical Red
                    label_suffix = " ⚠️ CRITICAL LOW"
                elif not is_pressure and val < CRITICAL_LOW_FLOW:
                    color_style = "#FF4B4B"  # Critical Red
                    label_suffix = " ⚠️ CRITICAL LOW"
                else:
                    color_style = "#56B37F"  # Normal Vibrant Green
                    label_suffix = " ✅ Normal"
                
                # Inject a unique styled container for each metric card based on its status
                st.markdown(f"""
                    <style>
                        div[data-testid="stMetricColumn"]:nth-of-type({(idx % 4) + 1}) div[data-testid="stMetricValue"] {{
                            color: {color_style} !important;
                        }}
                    </style>
                """, unsafe_allow_html=True)
                
                st.metric(
                    label=f"{row['department']} ({row['tag_name']}){label_suffix}", 
                    value=f"{val:.1f}{unit}"
                )
    
    st.markdown("---")
    
    # 2. Dropdown Filter Section
    st.subheader("📊 Historical Trend Analysis")
    
    dept_list_df = run_query("SELECT DISTINCT department FROM compressed_air_readings ORDER BY department;")
    departments = dept_list_df['department'].tolist() if not dept_list_df.empty else ["Engg Shops"]
    
    selected_dept = st.selectbox("Select a Department to Filter Trend Matrix:", departments)
    
    # 3. Fetch Trend Data for Selected Department
    trend_query = """
        SELECT ts, tag_name, value 
        FROM compressed_air_readings 
        WHERE department = %s 
        ORDER BY ts DESC LIMIT 150;
    """
    df_trend = run_query(trend_query, (selected_dept,))
    
    if not df_trend.empty:
        df_trend = df_trend.iloc[::-1]
        
        mean_val = df_trend['value'].mean()
        max_val = df_trend['value'].max()
        last_val = df_trend['value'].iloc[-1]
        
        fig = go.Figure()
        
        for tag in df_trend['tag_name'].unique():
            df_tag = df_trend[df_trend['tag_name'] == tag]
            fig.add_trace(go.Scatter(
                x=df_tag['ts'], 
                y=df_tag['value'],
                mode='lines',
                name=f"{tag} (Mean: {mean_val:.1f} Max: {max_val:.1f} Last: {last_val:.1f})",
                line=dict(color='#56B37F', width=2)
            ))
            
        fig.update_layout(
            title=f"Historical Flow Trend — {selected_dept}",
            template="plotly_dark",
            paper_bgcolor="#161719",
            plot_bgcolor="#161719",
            xaxis=dict(showgrid=True, gridcolor="#24262b", title="Timestamp (ts)"),
            yaxis=dict(showgrid=True, gridcolor="#24262b", title="Flow / Pressure Rates"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0),
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("👁️ View Live Raw Metric Logs"):
            st.dataframe(df_trend, use_container_width=True)
    else:
        st.info("No timeline records matching the selected filter query found.")

except Exception as e:
    st.error(f"Error streaming visualization parameters: {e}")

time.sleep(refresh_rate)
st.rerun()