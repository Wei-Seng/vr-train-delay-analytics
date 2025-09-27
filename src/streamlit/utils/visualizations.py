import plotly.express as px
import plotly.graph_objects as go

def create_delay_charts(df):
    """Create standard delay visualization charts"""
    
    charts = {}
    
    # Top delayed routes
    charts['top_routes'] = px.bar(
        df.groupby('route')['avg_delay'].mean().head().reset_index(),
        x='route', y='avg_delay',
        title="Top 5 Most Delayed Routes"
    )
    
    # Monthly trends
    charts['monthly_trend'] = px.line(
        df.groupby('month')['avg_delay'].mean().reset_index(),
        x='month', y='avg_delay',
        title="Monthly Delay Trends"
    )
    
    return charts