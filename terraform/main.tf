# terraform/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# S3 Buckets
resource "aws_s3_bucket" "raw_data" {
  bucket = "vr-trains-raw-data-${random_string.suffix.result}"
}

resource "aws_s3_bucket" "processed_data" {
  bucket = "vr-trains-processed-data-${random_string.suffix.result}"
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# Athena Database
resource "aws_athena_database" "train_delays_db" {
  name   = "train_delays_database"
  bucket = aws_s3_bucket.processed_data.bucket
}

# API Gateway
resource "aws_api_gateway_rest_api" "train_api" {
  name        = "vr-train-delay-api"
  description = "API for VR train delay analytics"
}