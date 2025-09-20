# VR Train Delay Analytics

An **Analytics-as-a-Service (AaaS)** platform built on AWS for processing, analyzing, and visualizing Finnish railway delay data from the Digitraffic API.


## Features

*   **Batch Processing:** Download historical delay data as CSV files from S3.
*   **Streaming Simulation:** Simulate real-time train delay events using Kinesis Data Streams.
*   **REST API:** Query average delays for specific routes and stations over custom time periods.
*   **Interactive Dashboard:** Visualize trends, top delayed routes, and seasonal comparisons with Amazon QuickSight.


## Architecture & Technology Stack

Our cloud-native solution leverages the following AWS services:

*   **Data Storage:** Amazon S3 (Raw JSON & Processed Parquet/CSV)
*   **Data Processing:** AWS Glue Jobs, AWS Lambda
*   **Real-time Data Streaming:** Amazon Kinesis Data Streams
*   **API Layer:** Amazon API Gateway, AWS Lambda
*   **Analytics & Querying:** Amazon Athena
*   **Data Visualization:** Amazon QuickSight
*   **Infrastructure as Code (IaC):** Terraform


## Architecture

![Our System Architecture](docs/system-architecture.png)
*Diagram showing all AWS services and their connections.*


## Data Flow

![Our Data Pipeline](docs/data-flow.png)
*Diagram illustrating the step-by-step journey of data from source to dashboard.*


## 📁 Project Structure


## Team
- Person A: Data pipeline & infrastructure
- Person B: API & streaming
- Person C: Analytics & documentation


## License
MIT License - see LICENSE file for details.