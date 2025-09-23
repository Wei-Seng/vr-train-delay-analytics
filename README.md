# VR Train Delay Analytics

An **Analytics-as-a-Service (AaaS)** platform built on AWS for processing, analyzing, and visualizing Finnish railway delay data from the Digitraffic API.

## Features

*   **Batch Processing:** Download historical delay data as CSV/Parquet files from S3
*   **Streaming Simulation:** Simulate real-time train delay events using Kinesis Data Streams
*   **REST API:** Query average delays for specific routes and stations over custom time periods
*   **Interactive Dashboard:** Visualize trends and patterns with Amazon QuickSight

## Architecture

![System Architecture](docs/system-architecture.png)
*High-level system architecture showing AWS services and data flow*

## Data Flow

![Data Pipeline](docs/data-flow.png)
*Step-by-step journey of data from source to dashboard*

## Technology Stack

*   **Data Storage:** Amazon S3 (Raw JSON & Processed Parquet/CSV)
*   **Data Processing:** AWS Glue Jobs, AWS Lambda
*   **Real-time Streaming:** Amazon Kinesis Data Streams
*   **API Layer:** Amazon API Gateway, AWS Lambda
*   **Analytics & Querying:** Amazon Athena
*   **Data Visualization:** Amazon QuickSight
*   **Infrastructure as Code:** Terraform

## 📁 Project Structure

vr-train-delay-analytics/
├── terraform/ # Infrastructure as Code
├── src/ # Source code
│ ├── data-collection/ # Data ingestion scripts
│ ├── data-cleaning/ # ETL and transformation
│ └── lambda/ # Lambda function code
├── docs/ # Documentation & diagrams
└── README.md # This file


## Team

*   **Person A:** Data Pipeline & Infrastructure (S3, Glue, Data Collection)
*   **Person B:** API & Streaming (Kinesis, API Gateway, Lambda Functions)
*   **Person C:** Analytics & Coordination (Terraform, Athena, QuickSight, Documentation)

## Quick Start

### Prerequisites
- AWS CLI configured with credentials
- Terraform installed

### Deployment
1.  Clone this repository: `git clone https://github.com/Wei-Seng/vr-train-delay-analytics.git`
2.  Navigate to terraform directory: `cd terraform`
3.  Initialize Terraform: `terraform init`
4.  Deploy infrastructure: `terraform apply`

### Accessing the System
*   **Dashboard URL:** Available after deployment via AWS QuickSight
*   **API Endpoint:** Output displayed after `terraform apply`

## License

MIT License - see [LICENSE](LICENSE) file for details.