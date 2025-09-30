import streamlit as st
from pyathena import connect
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="VR Train Delay Analytics",
    page_icon="🚆",
    layout="wide"
)

# --- AWS & Athena Configuration ---
ATHENA_S3_STAGING_DIR = "s3://vr-trains-athena-results-..." # IMPORTANT: Replace with your actual bucket name
ATHENA_DB_NAME = "train_delays_database"
AWS_REGION = "us-east-1"

# --- Caching ---
# Cache the connection and data fetching to prevent re-running on every interaction
@st.cache_resource
def get_athena_connection():
    """Creates and returns a connection to Athena."""
    return connect(s3_staging_dir=ATHENA_S3_STAGING_DIR, region_name=AWS_REGION)

@st.cache_data(ttl=600) # Cache data for 10 minutes
def run_athena_query(query):
    """Runs a query on Athena and returns the result as a pandas DataFrame."""
    conn = get_athena_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    
    # Fetch column names from cursor description
    columns = [desc[0] for desc in cursor.description]
    
    # Fetch results and build DataFrame
    results_df = pd.DataFrame(cursor.fetchall(), columns=columns)
    return results_df

# --- UI Layout ---
st.title("🚆 VR Train Delay Analytics Dashboard")
st.markdown("Live analytics on train delay data, powered by AWS.")

# --- Data Fetching ---
try:
    # Query 1: Top 10 most delayed train types
    top_delays_query = """
    SELECT trainType, AVG(delay_minutes) as avg_delay
    FROM "processed_data" -- Assumes crawler creates a table named "processed_data"
    WHERE delay_minutes > 0
    GROUP BY trainType
    ORDER BY avg_delay DESC
    LIMIT 10;
    """
    df_top_delays = run_athena_query(top_delays_query)

    # --- Display Metrics & Charts ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Most Delayed Train Types")
        st.dataframe(df_top_delays)

    with col2:
        st.subheader("Average Delay by Train Type (Bar Chart)")
        # Ensure avg_delay is numeric for plotting
        df_top_delays['avg_delay'] = pd.to_numeric(df_top_delays['avg_delay'])
        st.bar_chart(df_top_delays, x='trainType', y='avg_delay')

    st.success("Dashboard loaded successfully!")
    st.balloons()

except Exception as e:
    st.error(f"An error occurred while loading the dashboard: {e}")
    st.warning("This may be due to the Athena table not being created yet. Please ensure the Glue Crawler has run successfully at least once.")

