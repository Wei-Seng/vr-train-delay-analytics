import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_sample_data():
    """Load sample data for dashboard development"""
    
    # Generate sample train delay data
    routes = [
        "Helsinki → Tampere",
        "Helsinki → Turku", 
        "Tampere → Oulu",
        "Helsinki → Lahti",
        "Turku → Helsinki"
    ]
    
    data = []
    for route in routes:
        for month in range(1, 13):
            avg_delay = np.random.uniform(2, 15)  # 2-15 minutes delay
            data.append({
                'route': route,
                'month': f"2024-{month:02d}",
                'avg_delay': round(avg_delay, 1),
                'trip_count': np.random.randint(50, 200)
            })
    
    return pd.DataFrame(data)

def connect_to_athena():
    """Future function to connect to AWS Athena"""
    # TODO: Implement Athena connection
    pass