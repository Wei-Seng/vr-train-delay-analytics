-- Create Athena table for processed train data
CREATE EXTERNAL TABLE IF NOT EXISTS train_delays (
  train_number STRING,
  departure_station STRING,
  scheduled_time TIMESTAMP,
  actual_time TIMESTAMP,
  delay_minutes INT,
  date_partition STRING
)
PARTITIONED BY (year STRING, month STRING, day STRING)
STORED AS PARQUET
LOCATION 's3://vr-trains-processed-data/parquet/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');