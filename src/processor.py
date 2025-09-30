import boto3 # type: ignore
import pandas as pd # type: ignore
from datetime import datetime, timedelta

# Configuration
RAW_BUCKET_NAME = "vr-trains-raw-data-..." # IMPORTANT: Replace with your actual bucket name
PROCESSED_BUCKET_NAME = "vr-trains-processed-data-..." # IMPORTANT: Replace with your actual bucket name

s3 = boto3.resource('s3')

def process_recent_data():
    """Reads raw JSON files from the last hour, processes them, and saves as Parquet."""
    print("Starting data processing job...")
    
    raw_bucket = s3.Bucket(RAW_BUCKET_NAME)
    now = datetime.now()
    # Look for files created in the last hour
    prefix = f"year={now.year}/month={now.month:02d}/day={now.day:02d}/"

    all_trains = []
    
    # Filter for recent files to avoid reprocessing everything every time
    for obj in raw_bucket.objects.filter(Prefix=prefix):
        # A simple check if the file is recent
        if (now - obj.last_modified.replace(tzinfo=None)).total_seconds() < 3600:
            print(f"Processing file: {obj.key}")
            content = obj.get()['Body'].read().decode('utf-8')
            trains = json.loads(content)
            all_trains.extend(trains)

    if not all_trains:
        print("No new raw data to process.")
        return

    df = pd.DataFrame(all_trains)
    print(f"Loaded {len(df)} total records for processing.")

    # --- Data Cleaning (simplified) ---
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Add a dummy delay column for demonstration
    df['delay_minutes'] = df.apply(lambda row: random.randint(0, 20) if row['speed'] > 0 else 0, axis=1)
    
    # Add partition columns
    df['year'] = df['timestamp'].dt.year
    df['month'] = df['timestamp'].dt.month
    df['day'] = df['timestamp'].dt.day

    # Save to processed bucket, partitioned by date
    # This is a simplified save; for large data, you'd use a library like `awswrangler`
    # to handle partitioning efficiently.
    output_key = f"year={now.year}/month={now.month:02d}/day={now.day:02d}/{now.strftime('%Y-%m-%d-%H-%M-%S')}.parquet"
    
    df.to_parquet(f"s3://{PROCESSED_BUCKET_NAME}/{output_key}", index=False, engine='pyarrow')
    
    print(f"Successfully saved processed data to s3://{PROCESSED_BUCKET_NAME}/{output_key}")

if __name__ == "__main__":
    import json, random
    process_recent_data()
