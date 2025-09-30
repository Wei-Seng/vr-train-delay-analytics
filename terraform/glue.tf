# terraform/glue.tf

resource "aws_glue_crawler" "data_crawler" {
  name          = "vr-data-crawler"
  database_name = aws_athena_database.train_delays_db.name
  role          = aws_iam_role.lambda_execution_role.arn # Reuse the role, but you might need to add Glue permissions to it

  s3_target {
    path = "s3://${aws_s3_bucket.processed_data.bucket}/" # Scan the processed data bucket
  }

  # Optional: Run the crawler on a schedule
  schedule = "cron(0 2 * * ? *)" # Run at 2 AM UTC daily
}
