import streamlit as st # type: ignore
from pyathena import connect # type: ignore
import pandas as pd # type: ignore

# --- Page Configuration ---
st.set_page_config(
    page_title="VR Train Delay Analytics",
    page_icon="🚆",
    layout="wide"
)

# --- AWS & Athena Configuration ---
ATHENA_S3_STAGING_DIR = "s3://vr-trains-athena-results-..."
ATHENA_DB_NAME = "train_delays_database"
AWS_REGION = "us-east-1"

# --- Caching ---
@st.cache_resource
def get_athena_connection():
    """Creates and returns a connection to Athena."""
    return connect(
        s3_staging_dir=ATHENA_S3_STAGING_DIR,
        region_name=AWS_REGION,
        schema_name=ATHENA_DB_NAME  
    )

@st.cache_data(ttl=600)
def run_athena_query(query):
    """Runs a query on Athena and returns the result as a pandas DataFrame."""
    conn = get_athena_connection()
    cursor = conn.cursor()
    cursor.execute(query)

    columns = [desc[0] for desc in cursor.description]
    results_df = pd.DataFrame(cursor.fetchall(), columns=columns)
    return results_df

# --- UI Layout ---
st.title("🚆 VR Train Delay Analytics Dashboard")
st.markdown("Live analytics on train delay data, powered by AWS.")

# --- Data Fetching ---
try:
    # Query with explicit database reference
    top_delays_query = """
    SELECT trainType, AVG(delay_minutes) as avg_delay
    FROM "train_delays_database"."processed_data"
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
        df_top_delays['avg_delay'] = pd.to_numeric(df_top_delays['avg_delay'])
        st.bar_chart(df_top_delays, x='trainType', y='avg_delay')

    st.success("Dashboard loaded successfully!")
    st.balloons()

except Exception as e:
    st.error(f"An error occurred while loading the dashboard: {e}")
    st.warning("Please ensure the Athena table 'processed_data' exists in the 'train_delays_database' database.")