import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_sample_data
from utils.visualizations import create_delay_charts

# Page config
st.set_page_config(
    page_title="VR Train Delay Analytics",
    page_icon="🚂",
    layout="wide"
)

# Title
st.title("🚂 VR Train Delay Analytics Dashboard")
st.markdown("Analytics-as-a-Service platform for Finnish railway delay data")

# Sidebar
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Select Date Range", value=[])

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Trains Analyzed", "1,234")
with col2:
    st.metric("Average Delay", "4.2 min")
with col3:
    st.metric("On-Time Performance", "87%")

# Load sample data
df = load_sample_data()

# Charts
st.header("📊 Delay Analysis")

# Top 5 delayed routes
fig1 = px.bar(df.head(), x='route', y='avg_delay', 
              title="Top 5 Most Delayed Routes")
st.plotly_chart(fig1, use_container_width=True)

# Monthly trends
st.header("📈 Monthly Trends")
fig2 = px.line(df, x='month', y='avg_delay', 
               title="Average Delays by Month")
st.plotly_chart(fig2, use_container_width=True)