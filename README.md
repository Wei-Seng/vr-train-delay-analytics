# VR Train Delay Analytics

An **Analytics-as-a-Service (AaaS)** platform built on AWS that collects, processes, analyzes, and visualizes Finnish railway delay data from the Digitraffic API using a fully distributed Spark pipeline.

## Project Overview

This project builds a cloud-based system to analyze train delay patterns within Finland's national train system, providing insights through multiple access methods: batch downloads, streaming simulation with interactive dashboards.

## Features
- **Automated Data Ingestion** – Cron-driven collector pulls live train positions every 2 minutes
- **Distributed Batch Processing** – Spark job on Amazon EMR (3-node cluster) transforms raw JSON → enriched Parquet
- **Serverless Analytics** – Amazon Athena queries over partitioned Parquet data
- **Interactive Dashboard** – Streamlit app hosted on EC2 with real-time insights
- **Cost-Optimized & Auto-Terminating** – EMR cluster shuts down after 60 min idle (~$0.20 per run)

## Architecture

![System Architecture](diagrams/SystemArchitectureDiagram.png)

*High-level system architecture showing AWS services and data flow*

## Data Flow
![Data Pipeline](diagrams/DataFlowDiagram.png)
1. `collector.py` (on EC2) → raw JSON files in S3 raw bucket (partitioned by date)
2. Spark job submitted via EMR console → reads all raw data → calls Digitraffic timetable API → calculates delays → writes Snappy-compressed Parquet to processed bucket
3. Athena external table points to processed Parquet
4. Streamlit dashboard queries Athena and visualizes results

## Technology Stack

### Data Layer
* **Data Storage:** Amazon S3 (Raw JSON & Processed Parquet/CSV)
* **Data Processing:** Python scripts (collector.py for data fetching to raw S3, spark_processor.py for processing to Parquet)
* **Analytics & Querying:** Amazon Athena
* **Database:** Partitioned external tables for cost efficiency

### Application Layer
* **API Layer:** direct API calls to public endpoints like rata.digitraffic.fi
* **Dashboard:** Streamlit (hosted on AWS EC2)

### Infrastructure
* **Infrastructure as Code:** Terraform
* **Monitoring:** AWS CloudWatch (with alarms and SNS notifications)
* **Version Control:** Git with collaborative workflows

## Dashboard Setup (Streamlit)

### Local Development
1. Navigate to streamlit directory: 
cd src/
2. Install dependencies:
pip install -r requirements.txt
3. Run dashboard locally: 
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
4. Open browser to `http://[PUBLICHOSTIP]:8501`

### Dashboard Features
The Streamlit dashboard provides 5 key visualizations:
- **Top 10 Most Delayed Train Types**
- **Average Delay by Train Type** 
- **Top 7 Most Delayed Routes** 
- **Average Delay by Route** 

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with credentials (AWS Learner Lab)
- Terraform installed (v1.0+)
- Python 3.7 for local dashboard development
- Git for version control

### Infrastructure Deployment
1. Clone this repository:
git clone https://github.com/Wei-Seng/vr-train-delay-analytics.git

2. Navigate to terraform directory:
cd terraform

3. Initialize Terraform:
terraform init

4. Review and deploy infrastructure:
terraform plan
terraform apply


### Accessing the System
* **Dashboard URL:** Available after Streamlit deployment
* **Data Storage:** Check AWS S3 console for bucket creation
* **Analytics:** Access via AWS Athena console

## Cost Optimization

This project is designed for student budgets (target: <100 SGD total):
- **S3 Storage:** ~$1-2 for entire project duration
- **Athena:** Pay-per-query (very affordable for coursework)

###  API 
data sourced directly from public API: https://rata.digitraffic.fi/api/v1/

## Development Workflow
1. **Data Development:** Work with sample data locally first
2. **Infrastructure:** Test Terraform changes in development environment  
3. **Dashboard:** Develop Streamlit app with mock data
4. **Integration:** Connect dashboard to real AWS services
5. **Deployment:** Deploy to streamlit dashboard

## External Resources
- [Digitraffic Railway API](https://www.digitraffic.fi/rautatieliikenne/)
- [AWS Terraform Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 📄 License
MIT License - see [LICENSE](LICENSE) file for details.

## Contributing
1. Create feature branches for new development
2. Follow commit message conventions  
3. Test changes locally before pushing
4. Update documentation as needed
