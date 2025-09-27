import json
import boto3 # type: ignore
import time
import requests # type: ignore
import os

# --- CONFIGURATION ---
# This script is configured via environment variables for flexibility.
AWS_REGION = os.getenv("AWS_REGION", "eu-east-1")
STREAM_NAME = os.getenv("KINESIS_STREAM_NAME", "vr-realtime-train-stream")
# ---

# Initialize the AWS client. It will use your locally configured AWS credentials.
kinesis_client = boto3.client('kinesis', region_name=AWS_REGION)


def simulate_live_stream():
    """Fetches latest train locations and sends them to a Kinesis stream."""
    print(f"--- Starting Real-Time Producer for Kinesis Stream: {STREAM_NAME} ---")

    # This is the Digitraffic API endpoint for all currently moving trains.
    url = "https://rata.digitraffic.fi/api/v1/train-locations/latest/"

    while True:
        try:
            print("\nFetching latest train locations from API...")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            live_trains = response.json()

            if not live_trains:
                print("No live trains reported. Waiting...")
                time.sleep(60)
                continue

            print(f"Found {len(live_trains)} live trains. Preparing to send to Kinesis.")

            records_to_send = []
            for train in live_trains:
                # Each train's data is a "record". The PartitionKey ensures that
                # data for the same train consistently goes to the same "lane" (shard)
                # in our conveyor belt, which helps with ordered processing if needed.
                record = {
                    'Data': json.dumps(train),
                    'PartitionKey': str(train['trainNumber'])
                }
                records_to_send.append(record)

            # Send up to 500 records at once for efficiency.
            if records_to_send:
                response = kinesis_client.put_records(
                    StreamName=STREAM_NAME,
                    Records=records_to_send
                )
                print(f"Batch sent to Kinesis. Failed records: {response['FailedRecordCount']}")

            print("Cycle complete. Waiting for 30 seconds...")
            time.sleep(30)

        except Exception as e:
            print(f"An error occurred: {e}. Retrying in 60 seconds.")
            time.sleep(60)

if __name__ == "__main__":
    simulate_live_stream()