variable "aws_region" {
  description = "The AWS region where resources will be created"
  type        = string
  # choosing eu-north-1 (Stockholm) as it's typically the cheapest region in Europe
  # it provides good performance for our Finnish data source (Digitraffic API)
  default     = "eu-north-1"
}