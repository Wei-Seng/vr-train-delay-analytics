# First, we need to package our Python code into a .zip file.
data "archive_file" "kinesis_consumer_zip" {
  type        = "zip"
  source_dir  = "../src/lambda_kinesis_consumer/" # Path to your Python code
  output_path = "../dist/kinesis_consumer.zip"
}

# Now, define the Lambda function itself.
resource "aws_lambda_function" "kinesis_consumer" {
  function_name = "kinesis-stream-consumer"

  filename         = data.archive_file.kinesis_consumer_zip.output_path
  source_code_hash = data.archive_file.kinesis_consumer_zip.output_base64sha256

  handler = "main.handler" # The file is main.py, the function is handler
  runtime = "python3.9"
  role    = aws_iam_role.lambda_exec_role.arn # Using the shared role from Person A

  environment {
    variables = {
      # Pass the name of the processed data bucket to the Lambda
      PROCESSED_S3_BUCKET = aws_s3_bucket.processed_data.bucket
    }
  }
}

# Finally, create the trigger that connects the Kinesis stream to the Lambda.
resource "aws_lambda_event_source_mapping" "kinesis_trigger" {
  event_source_arn  = aws_kinesis_stream.realtime_trains.arn
  function_name     = aws_lambda_function.kinesis_consumer.arn
  starting_position = "LATEST"
}
