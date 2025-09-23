# terraform/iam.tf
# IAM role for Lambda functions
resource "aws_iam_role" "lambda_execution_role" {
  name = "vr-train-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for Lambda to access S3 and CloudWatch
resource "aws_iam_role_policy" "lambda_basic_policy" {
  name = "lambda-basic-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::vr-trains-raw-data",
          "arn:aws:s3:::vr-trains-raw-data/*",
          "arn:aws:s3:::vr-trains-processed-data", 
          "arn:aws:s3:::vr-trains-processed-data/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}