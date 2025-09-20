Explaining the System Architecture Design with the numbers (same as in the png):

1. Digitraffic API → Data Collector
- The Data Collector Lambda function fetches raw train data from the external Digitraffic API.

2. Data Collector → Raw Data
- The raw JSON data is saved to the Raw Data S3 bucket for initial storage.

3. Raw Data → Producer
- The Producer Lambda function reads batches of historical data from the Raw Data bucket to simulate a stream.

4. Producer → Data Stream
- The Producer function sends records to the Kinesis Data Stream to simulate real-time data ingestion.

5. Data Stream → Consumer
- The Consumer Lambda function is triggered by new records in the stream, processing them in near-real-time.

6. Consumer → Processed Data
- The Consumer function saves its results (e.g., calculated delays) to the Processed Data S3 bucket.

7. Raw Data → ETL Job
- The AWS Glue ETL job reads the raw data for batch processing and cleaning.

8. ETL Job → Processed Data
- The Glue job writes the transformed, structured data (e.g., Parquet/CSV) to the Processed Data bucket.

9. Processed Data → Athena
- Amazon Athena queries the processed data directly from S3 using SQL.

10. Athena → QuickSight
- Query results from Athena are visualized in the Amazon QuickSight dashboard.

11. Athena → API Handler
- The API Handler Lambda function executes Athena queries to fetch data for API requests.

12. API Handler → Our API
- The API Handler returns structured data (e.g., JSON) to the end-user through the API Gateway.