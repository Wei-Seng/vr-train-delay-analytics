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
ATHENA_S3_STAGING_DIR = "s3://vr-trains-athena-results-..."  # Your actual bucket
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
    # Query 1: Top 10 most delayed train types
    top_delays_query = """
    SELECT trainType, AVG(delay_minutes) as avg_delay
    FROM "train_delays_database"."processed_data"
    WHERE delay_minutes > 0
    GROUP BY trainType
    ORDER BY avg_delay DESC
    LIMIT 10;
    """
    df_top_delays = run_athena_query(top_delays_query)

    # Query 2: Route Performance Comparison
    route_performance_query = """
    SELECT
        departureStation,
        destinationStation,
        CONCAT(departureStation, ' → ', destinationStation) as route,
        AVG(delay_minutes) as avg_delay,
        COUNT(*) as num_trips,
        MAX(delay_minutes) as max_delay
    FROM "train_delays_database"."processed_data"
    WHERE delay_minutes > 0
    GROUP BY departureStation, destinationStation
    HAVING COUNT(*) >= 3
    ORDER BY avg_delay DESC
    LIMIT 15;
    """
    df_routes = run_athena_query(route_performance_query)

    # --- Display Metrics & Charts ---

    # Section 1: Train Type Analysis
    st.header("🚂 Train Type Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Most Delayed Train Types")
        st.dataframe(df_top_delays, use_container_width=True)

    with col2:
        st.subheader("Average Delay by Train Type")
        df_top_delays['avg_delay'] = pd.to_numeric(df_top_delays['avg_delay'])
        st.bar_chart(df_top_delays, x='trainType', y='avg_delay')

    # Section 2: Route Performance Analysis
    st.markdown("---")
    st.header("📍 Route Performance Analysis")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Top 15 Most Delayed Routes")
        # Format for better display
        display_df = df_routes[['route', 'avg_delay', 'num_trips', 'max_delay']].copy()
        display_df['avg_delay'] = display_df['avg_delay'].round(1)
        display_df['max_delay'] = display_df['max_delay'].astype(int)
        display_df.columns = ['Route', 'Avg Delay (min)', 'Trips', 'Max Delay (min)']
        st.dataframe(display_df, use_container_width=True)

    with col4:
        st.subheader("Average Delay by Route")
        df_routes['avg_delay'] = pd.to_numeric(df_routes['avg_delay'])
        # Use horizontal bar chart for better route label visibility
        st.bar_chart(df_routes.head(10), x='route', y='avg_delay')

    # Section 3: Summary Statistics
    st.markdown("---")
    st.subheader("📊 Summary Statistics")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        total_routes = len(df_routes)
        st.metric("Routes Analyzed", total_routes)

    with metric_col2:
        worst_route = df_routes.iloc[0]
        st.metric(
            "Worst Route",
            worst_route['route'],
            f"↑ {worst_route['avg_delay']:.1f} min"
        )

    with metric_col3:
        total_trips = int(df_routes['num_trips'].sum())
        st.metric("Delayed Trips", total_trips)

    with metric_col4:
        overall_avg = df_routes['avg_delay'].mean()
        st.metric("Overall Avg Delay", f"{overall_avg:.1f} min")

    st.success("✅ Dashboard loaded successfully!")
    st.balloons()

except Exception as e:
    st.error(f"❌ An error occurred while loading the dashboard: {e}")
    st.warning("⚠️ Please ensure the Athena table 'processed_data' exists in the 'train_delays_database' database.")
