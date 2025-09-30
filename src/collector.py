import boto3  # type: ignore
import requests # type: ignore
import json
from datetime import datetime

# Configuration
RAW_BUCKET_NAME = "vr-trains-raw-data-..." # IMPORTANT: Replace with your actual bucket name after deployment
API_URL = "https://rata.digitraffic.fi/api/v1/train-locations/latest/"

s3_client = boto3.client('s3' )

def fetch_and_save_data():
    """Fetches latest train data and saves it as a JSON file to S3."""
    print("Fetching latest train locations...")
    try:
        response = requests.get(API_URL, timeout=20)
        response.raise_for_status()
        live_trains = response.json()

        if not live_trains:
            print("No live trains reported.")
            return

        now = datetime.now()
        # Create a unique filename based on the current timestamp
        s3_key = f"year={now.year}/month={now.month:02d}/day={now.day:02d}/{now.strftime('%Y-%m-%d-%H-%M-%S')}.json"
        
        s3_client.put_object(
            Bucket=RAW_BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(live_trains)
        )
        print(f"Successfully saved {len(live_trains)} train records to s3://{RAW_BUCKET_NAME}/{s3_key}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
