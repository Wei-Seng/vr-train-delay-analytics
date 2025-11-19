"""
VR Train Delay Spark ETL Job
Processes raw JSON from S3 using distributed Spark on EMR
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, expr, when, to_timestamp, unix_timestamp, 
    count, avg, max as spark_max 
) 
from pyspark.sql.types import (
    IntegerType, StructType, StructField, StringType, ArrayType
)
import requests 
import sys

# Define the function to fetch data in a distributed way
def fetch_timetable_data_distributed(partition_of_rows):
    """
    Called by Spark Executors to fetch API data for a partition of unique trains.
    """
    session = requests.Session() 
    
    for row in partition_of_rows:
        dep_date = row['departureDate']
        train_num = row['trainNumber']
        url = f"https://rata.digitraffic.fi/api/v1/trains/{dep_date}/{train_num}"
        
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    yield data[0] # Yield the train detail object
        except Exception:
            pass

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
print("VR TRAIN DELAY SPARK PROCESSING JOB (Distributed API Fetch)")
print("=" * 60)

# Step 1: Read raw JSON files
print("\n[Step 1/7] Reading raw JSON files from S3...")
raw_path = f"s3://{RAW_BUCKET}/"
df_positions = spark.read.option("basePath", raw_path).json(raw_path)
print("✓ Raw data loaded")

# Step 2: Get unique trains
print("\n[Step 2/7] Extracting unique trains...")
unique_trains = df_positions.select("trainNumber", "departureDate").distinct()
unique_count = unique_trains.count()
print(f"✓ Found {unique_count} unique trains")

# Step 3: Fetch timetable details (Distributed/Parallel)
print("\n[Step 3/7] Fetching timetable details via API in parallel...")
train_rdd = unique_trains.rdd.mapPartitions(fetch_timetable_data_distributed)

# Define a schema for the fetched JSON data
timetable_schema = StructType([
    StructField("trainNumber", IntegerType(), True),
    StructField("trainType", StringType(), True),
    StructField("departureDate", StringType(), True),
    StructField("timeTableRows", ArrayType(StructType([
        StructField("stationShortCode", StringType(), True),
        StructField("type", StringType(), True), 
        StructField("scheduledTime", StringType(), True),
        StructField("actualTime", StringType(), True)
    ])), True),
])

# Step 4: Create DataFrame and Cache
print("\n[Step 4/7] Creating DataFrame from fetched timetables...")
df = spark.createDataFrame(train_rdd, schema=timetable_schema) 
df.persist() 

df_count = df.count() 
if df_count == 0:
    print("ERROR: No train details fetched. Check network/logs.")
    sys.exit(1)
print(f"✓ Fetched and cached {df_count} train timetables")

# Step 5: Extract departure/arrival info (FIXED LOGIC)
print("\n[Step 5/7] Extracting departure and arrival info...")

# Use 'expr' to filter the array directly using SQL syntax
# filter(array, x -> condition) returns an array of matching elements
# [0] takes the first match
df = df.withColumn("departure_info", expr("filter(timeTableRows, x -> x.type == 'DEPARTURE')[0]"))

# element_at(array, -1) takes the LAST element (final destination)
df = df.withColumn("arrival_info", expr("element_at(filter(timeTableRows, x -> x.type == 'ARRIVAL'), -1)"))

# Filter out valid journeys
df = df.filter(col("departure_info").isNotNull() & col("arrival_info").isNotNull())
filtered_count = df.count()
print(f"✓ Filtered to {filtered_count} valid journeys")

# Step 6: Calculate delays
print("\n[Step 6/7] Calculating delay metrics...")
df = df.withColumn("departureStation", col("departure_info.stationShortCode"))
df = df.withColumn("destinationStation", col("arrival_info.stationShortCode"))

# Convert timestamps
df = df.withColumn("scheduled_time_ts", to_timestamp(col("departure_info.scheduledTime")))
df = df.withColumn("actual_time_ts", 
    to_timestamp(
        when(col("departure_info.actualTime").isNotNull(), col("departure_info.actualTime"))
        .otherwise(col("departure_info.scheduledTime"))
    )
)

# Calculate delay
df = df.withColumn("delay_minutes", ((unix_timestamp("actual_time_ts") - unix_timestamp("scheduled_time_ts")) / 60).cast(IntegerType()))

final_df = df.select("trainNumber", "trainType", "departureStation", "destinationStation", "scheduled_time_ts", "actual_time_ts", "delay_minutes").filter(col("delay_minutes").isNotNull())

# Step 7: Write output
output_path = f"s3://{PROCESSED_BUCKET}/train_delays_spark.parquet"
print(f"\n[Step 7/7] Writing Parquet output to S3...")
final_df.write.mode("overwrite").parquet(output_path)  
print("\n✅ SPARK JOB COMPLETED SUCCESSFULLY")
spark.stop()