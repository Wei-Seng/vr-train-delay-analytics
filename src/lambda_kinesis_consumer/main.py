import json
import base64
import boto3 # type: ignore
import os
from datetime import datetime

# This client is initialized outside the handler for performance.
s3_client = boto3.client('s3')

# The destination bucket is passed in via an environment variable for security.
PROCESSED_S3_BUCKET = os.environ['PROCESSED_S3_BUCKET']

def handler(event, context):
    """
    This function is triggered by Kinesis. It processes a batch of records
    from the stream and archives them to S3.
    """
    print(f"Received {len(event['Records'])} records from Kinesis stream.")

    for record in event['Records']:
        try:
            # Data from Kinesis is base64 encoded, so we must decode it first.
            payload_decoded = base64.b64decode(record['kinesis']['data']).decode('utf-8')
            train_data = json.loads(payload_decoded)

            train_number = train_data.get('trainNumber', 'unknown')
            # Use the timestamp from the data itself for accuracy.
            timestamp = datetime.fromtimestamp(train_data.get('timestamp'))

            # This creates a "folder" structure in S3 like:
            # realtime-ingest/year=2025/month=09/day=13/hour=14/...
            # This is called Hive-style partitioning and is critical for efficient querying later.
            s3_key = (
                f"realtime-ingest/year={timestamp.year}/month={timestamp.month:02d}/"
                f"day={timestamp.day:02d}/hour={timestamp.hour:02d}/"
                f"train_{train_number}_{timestamp.isoformat()}.json"
            )

            # Save the individual event as a JSON file in the processed data bucket.
            s3_client.put_object(
                Bucket=PROCESSED_S3_BUCKET,
                Key=s3_key,
                Body=json.dumps(train_data)
            )

        except Exception as e:
            print(f"Error processing record: {e}")

    return {'status': 'Success'}

