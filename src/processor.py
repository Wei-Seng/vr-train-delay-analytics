import boto3
import pandas as pd
import json
from datetime import datetime
import requests
import tempfile

# Attempt to configure X-Ray if present to avoid [Errno 90] errors
try:
    from aws_xray_sdk.core import xray_recorder
    xray_recorder.configure(streaming_threshold=0)
except ImportError:
    pass

# ==============================================================================
# Configuration
# ==============================================================================
# IMPORTANT: Replace these with your actual, correct bucket names.
# Double-check them against the AWS S3 console.
RAW_BUCKET_NAME = "vr-trains-raw-data-..." #rmb to replace with the actual name before running
PROCESSED_BUCKET_NAME = "vr-trains-processed-data-..." #rmb to replace with the actual name before running

# The name of the final, single Parquet file we will create.
OUTPUT_PARQUET_FILENAME = "train_delays.parquet"
# ==============================================================================


def process_all_data():
    """
    Reads all raw JSON files from the source S3 bucket, processes them,
    and saves the result as a single Parquet file in the destination bucket.
    """
    print("--- Starting Data Processing Job (Simple Version) ---")

    s3_client = boto3.client('s3')
    all_position_records = []

    # 1. List all raw JSON files in the source bucket
    try:
        print(f"Listing files in raw data bucket: {RAW_BUCKET_NAME}")
        response = s3_client.list_objects_v2(Bucket=RAW_BUCKET_NAME)
        if 'Contents' not in response:
            print("!!! ERROR: No files found in the raw data bucket. Run collector.py first.")
            return
        
        raw_files = [item['Key'] for item in response['Contents']]
        print(f"Found {len(raw_files)} raw files to process.")

    except Exception as e:
        print(f"!!! FATAL ERROR: Could not list files in bucket '{RAW_BUCKET_NAME}'.")
        print(f"!!! Please check if the bucket exists and you have permissions.")
        print(f"!!! AWS Error: {e}")
        return

    # 2. Read and decode every raw file
    for file_key in raw_files:
        print(f"  -> Processing file: {file_key}")
        s3_object = s3_client.get_object(Bucket=RAW_BUCKET_NAME, Key=file_key)
        file_content = s3_object['Body'].read().decode('utf-8')
        # The content of our file is a list of JSON objects
        records = json.loads(file_content)
        all_position_records.extend(records)

    if not all_position_records:
        print("!!! ERROR: No records were loaded from the raw files.")
        return

    print(f"\nLoaded {len(all_position_records)} total position records.")

    # 3. Convert position records to a pandas DataFrame to find unique trains
    df_positions = pd.DataFrame(all_position_records)
    print("Available columns are:", list(df_positions.columns))

    # 4. Get unique trainNumber and departureDate pairs
    unique_trains = df_positions[['trainNumber', 'departureDate']].drop_duplicates()
    print(f"Found {len(unique_trains)} unique trains.")

    # 5. Fetch timetable details for each unique train
    train_details = []
    for _, row in unique_trains.iterrows():
        dep_date = row['departureDate']
        train_num = row['trainNumber']
        url = f"https://rata.digitraffic.fi/api/v1/trains/{dep_date}/{train_num}"
        print(f"  -> Fetching timetable for train {train_num} on {dep_date}")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data:
                    train_details.append(data[0])
        except Exception as e:
            print(f"    !!! Error fetching data for train {train_num} on {dep_date}: {e}")

    if not train_details:
        print("!!! ERROR: No train details were fetched from the API.")
        return

    print(f"\nSuccessfully fetched details for {len(train_details)} trains.")

    # 6. Convert fetched train details to a pandas DataFrame for processing
    df = pd.DataFrame(train_details)
    print("Successfully converted fetched data to DataFrame.")

    # 7. Clean and transform the data
    print("Cleaning and transforming data...")
    
    # Select and rename columns (trainNumber, departureDate already present)
    df = df[['trainNumber', 'trainType', 'departureDate', 'timeTableRows']]
    
    # Extract departure and arrival information
    df['departure_info'] = df['timeTableRows'].apply(
        lambda rows: next((row for row in rows if row['type'] == 'DEPARTURE'), None)
    )
    df['arrival_info'] = df['timeTableRows'].apply(
        lambda rows: next((row for row in reversed(rows) if row['type'] == 'ARRIVAL'), None)
    )
    
    # Drop rows where departure or arrival info is missing
    df.dropna(subset=['departure_info', 'arrival_info'], inplace=True)

    # Extract station names
    df['departureStation'] = df['departure_info'].apply(lambda x: x['stationShortCode'])
    df['destinationStation'] = df['arrival_info'].apply(lambda x: x['stationShortCode'])

    # Extract and convert timestamps
    df['scheduled_time_ts'] = pd.to_datetime(df['departure_info'].apply(lambda x: x.get('scheduledTime')))
    df['actual_time_ts'] = pd.to_datetime(df['departure_info'].apply(lambda x: x.get('actualTime', x.get('scheduledTime'))))

    # Calculate delay in minutes
    df['delay_minutes'] = (df['actual_time_ts'] - df['scheduled_time_ts']).dt.total_seconds() / 60
    df['delay_minutes'] = df['delay_minutes'].astype(int)

    # Final column selection
    final_df = df[['trainNumber', 'trainType', 'departureStation', 'destinationStation', 
                   'scheduled_time_ts', 'actual_time_ts', 'delay_minutes']]

    print("Data cleaning complete.")

    # 8. Save the final DataFrame as a single Parquet file to S3 using temp file to avoid direct write issues
    print(f"\nAttempting to save final Parquet file to: s3://{PROCESSED_BUCKET_NAME}/{OUTPUT_PARQUET_FILENAME}")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            final_df.to_parquet(tmp_file.name, index=False, engine='pyarrow')
            s3_client.upload_file(tmp_file.name, PROCESSED_BUCKET_NAME, OUTPUT_PARQUET_FILENAME)
        import os
        os.unlink(tmp_file.name)  # Clean up temp file
        print("\n--- SUCCESS! ---")
        print(f"Successfully saved {len(final_df)} processed records to s3://{PROCESSED_BUCKET_NAME}/{OUTPUT_PARQUET_FILENAME}")
        print("------------------")
    except Exception as e:
        print(f"!!! FATAL ERROR: Failed to write Parquet file to S3.")
        print(f"!!! Please check if the bucket '{PROCESSED_BUCKET_NAME}' exists and you have permissions.")
        print(f"!!! AWS Error: {e}")


if __name__ == "__main__":
    process_all_data()