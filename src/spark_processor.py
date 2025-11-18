"""
VR Train Delay Spark ETL Job
Processes raw JSON from S3 using distributed Spark on EMR
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, first, reverse, when, to_timestamp, unix_timestamp
from pyspark.sql.types import IntegerType
import requests
import json
import sys

# Initialize Spark
spark = SparkSession.builder \
    .appName("VR-Train-Delay-ETL") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Get bucket names from command line
if len(sys.argv) < 3:
    print("ERROR: Usage: spark_processor.py <raw_bucket> <processed_bucket>")
    sys.exit(1)
RAW_BUCKET = sys.argv[1]
PROCESSED_BUCKET = sys.argv[2]

print("=" * 60)
print("VR TRAIN DELAY SPARK PROCESSING JOB")
print("=" * 60)
print(f"Raw Data Bucket : s3://{RAW_BUCKET}/")
print(f"Output Bucket : s3://{PROCESSED_BUCKET}/")
print(f"Spark Version : {spark.version}")
print(f"Parallelism Level : {spark.sparkContext.defaultParallelism}")
print("=" * 60)

# Step 1: Read raw JSON files (train locations)
print("\n[Step 1/7] Reading raw JSON files from S3...")
raw_path = f"s3://{RAW_BUCKET}/**/*.json"  # Recursive read for partitions
df_positions = spark.read.json(raw_path)
raw_count = df_positions.count()
print(f"✓ Loaded {raw_count} raw position records")

# Step 2: Get unique trains (distributed dedup)
print("\n[Step 2/7] Extracting unique trains...")
unique_trains = df_positions.select("trainNumber", "departureDate").distinct()
unique_count = unique_trains.count()
print(f"✓ Found {unique_count} unique trains")

# Step 3: Fetch timetable details (serial on driver)
print("\n[Step 3/7] Fetching timetable details via API...")
train_details = []
unique_list = unique_trains.collect()  # Collect to driver (small set)
for row in unique_list:
    dep_date = row['departureDate']
    train_num = row['trainNumber']
    url = f"https://rata.digitraffic.fi/api/v1/trains/{dep_date}/{train_num}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                train_details.append(data[0])  # Assume first item is the train
    except Exception as e:
        print(f"Warning: Failed to fetch {url}: {e}")
fetch_count = len(train_details)
print(f"✓ Fetched timetables for {fetch_count} trains")

# Step 4: Create Spark DF from fetched data
print("\n[Step 4/7] Creating DataFrame from fetched timetables...")
if train_details:
    df = spark.createDataFrame(train_details)
else:
    print("ERROR: No train details fetched")
    sys.exit(1)
df_count = df.count()
print(f"✓ Created DataFrame with {df_count} records")

# Step 5: Extract departure/arrival info
print("\n[Step 5/7] Extracting departure and arrival info...")
df = df.withColumn("departure_info", explode(col("timeTableRows")).alias("row").filter(col("row.type") == "DEPARTURE")[0])
df = df.withColumn("arrival_info", reverse(explode(col("timeTableRows")).alias("row").filter(col("row.type") == "ARRIVAL"))[0])
df = df.filter(col("departure_info").isNotNull() & col("arrival_info").isNotNull())
filtered_count = df.count()
print(f"✓ Filtered to {filtered_count} valid journeys")

# Step 6: Calculate delays and select columns
print("\n[Step 6/7] Calculating delay metrics...")
df = df.withColumn("departureStation", col("departure_info.stationShortCode"))
df = df.withColumn("destinationStation", col("arrival_info.stationShortCode"))
df = df.withColumn("scheduled_time_ts", to_timestamp(col("departure_info.scheduledTime")))
df = df.withColumn("actual_time_ts", to_timestamp(when(col("departure_info.actualTime").isNotNull(), col("departure_info.actualTime")).otherwise(col("departure_info.scheduledTime"))))
df = df.withColumn("delay_minutes", ((unix_timestamp("actual_time_ts") - unix_timestamp("scheduled_time_ts")) / 60).cast(IntegerType()))

final_df = df.select("trainNumber", "trainType", "departureStation", "destinationStation", "scheduled_time_ts", "actual_time_ts", "delay_minutes").filter(col("delay_minutes").isNotNull())
final_count = final_df.count()
print(f"✓ Calculated delays for {final_count} train records")

# Display sample statistics
print("\n" + "=" * 60)
print("DELAY STATISTICS BY TRAIN TYPE")
print("=" * 60)
stats_df = final_df.groupBy("trainType") \
    .agg(
        avg("delay_minutes").alias("avg_delay"),
        count("*").alias("num_trains"),
        spark_max("delay_minutes").alias("max_delay")
    ) \
    .orderBy(col("avg_delay").desc())
stats_df.show(10, truncate=False)

# Step 7: Write output to S3
output_path = f"s3://{PROCESSED_BUCKET}/train_delays_spark.parquet"
print(f"\n[Step 7/7] Writing Parquet output to S3...")
print(f"Output path: {output_path}")
final_df.write.mode("overwrite").parquet(output_path)  # Removed coalesce(1) for better distribution
print("\n" + "=" * 60)
print("✅ SPARK JOB COMPLETED SUCCESSFULLY")
print("=" * 60)
print(f"Records processed : {final_count}")
print(f"Output format : Parquet (Snappy compressed)")
print(f"Output location : {output_path}")
print("=" * 60)
spark.stop()