# Defines the core data infrastructure

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

# Use a random suffix to ensure globally unique bucket names
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# 1. S3 Bucket for raw JSON data
resource "aws_s3_bucket" "raw_data" {
  bucket = "vr-trains-raw-data-${random_string.suffix.result}"
}

# 2. S3 Bucket for processed Parquet data
resource "aws_s3_bucket" "processed_data" {
  bucket = "vr-trains-processed-data-${random_string.suffix.result}"
}

# 3. S3 Bucket for Athena query results
resource "aws_s3_bucket" "athena_results" {
  bucket = "vr-trains-athena-results-${random_string.suffix.result}"
}

# 4. Athena Database
resource "aws_athena_database" "train_delays_db" {
  name   = "train_delays_database"
  bucket = aws_s3_bucket.athena_results.id
}

# 5. Glue Crawler to catalog the processed data
resource "aws_glue_crawler" "data_crawler" {
  name          = "vr-data-crawler"
  database_name = aws_athena_database.train_delays_db.name
  
  # IMPORTANT: This assumes the LabRole has Glue and S3 permissions.
  # If you can't attach policies, this resource might fail.
  role          = "LabRole" 

  s3_target {
    path = "s3://${aws_s3_bucket.processed_data.id}/"
  }
}
