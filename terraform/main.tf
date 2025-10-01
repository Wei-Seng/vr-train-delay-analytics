# Defines the core data infrastructure

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
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

resource "aws_s3_bucket" "raw_data" {
  bucket = "vr-trains-raw-data-${random_string.suffix.result}"
}

resource "aws_s3_bucket" "processed_data" {
  bucket = "vr-trains-processed-data-${random_string.suffix.result}"
}

resource "aws_s3_bucket" "athena_results" {
  bucket = "vr-trains-athena-results-${random_string.suffix.result}"
}

resource "aws_athena_database" "train_delays_db" {
  name   = "train_delays_database"
  bucket = aws_s3_bucket.athena_results.id
}
