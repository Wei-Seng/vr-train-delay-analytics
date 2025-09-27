# Configuration for Streamlit app
import os

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
ATHENA_DATABASE = 'train_delays_database'
ATHENA_TABLE = 'train_delays'
S3_STAGING_DIR = 's3://vr-trains-processed-data/athena-results/'

# App Configuration
APP_TITLE = "VR Train Delay Analytics"
APP_ICON = "🚂"

# Sample data for development
USE_SAMPLE_DATA = True  # Set to False when connecting to real AWS