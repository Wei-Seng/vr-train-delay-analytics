# --- Lambda Function Definition ---
data "archive_file" "api_handler_zip" {
  type        = "zip"
  source_dir  = "../src/lambda_api_handler/"
  output_path = "../dist/api_handler.zip"
}

resource "aws_lambda_function" "api_handler" {
  function_name = "api-top-delays-handler"

  filename         = data.archive_file.api_handler_zip.output_path
  source_code_hash = data.archive_file.api_handler_zip.output_base64sha256

  handler = "main.handler"
  runtime = "python3.9"
  role    = aws_iam_role.lambda_exec_role.arn # Reusing the same shared role

  environment {
    variables = {
      ATHENA_OUTPUT_LOCATION = "s3://${aws_s3_bucket.athena_results.bucket}/"
      ATHENA_DATABASE        = "vr_train_analytics"
      ATHENA_TABLE           = "processed_data_parquet"
    }
  }
}

# --- API Gateway Definition ---
resource "aws_api_gateway_rest_api" "analytics_api" {
  name = "TrainDelayAnalyticsAPI"
}

resource "aws_api_gateway_resource" "analytics_resource" {
  rest_api_id = aws_api_gateway_rest_api.analytics_api.id
  parent_id   = aws_api_gateway_rest_api.analytics_api.root_resource_id
  path_part   = "analytics"
}

resource "aws_api_gateway_resource" "top_delays_resource" {
  rest_api_id = aws_api_gateway_rest_api.analytics_api.id
  parent_id   = aws_api_gateway_resource.analytics_resource.id
  path_part   = "top-delays"
}

resource "aws_api_gateway_method" "get_top_delays" {
  rest_api_id   = aws_api_gateway_rest_api.analytics_api.id
  resource_id   = aws_api_gateway_resource.top_delays_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

# --- Connecting API Gateway to Lambda ---
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.analytics_api.id
  resource_id             = aws_api_gateway_resource.top_delays_resource.id
  http_method             = aws_api_gateway_method.get_top_delays.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_handler.invoke_arn
}

# --- Deployment ---
resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.analytics_api.id

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.analytics_api.body))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.analytics_api.id
  stage_name    = "v1"
}

# --- Permissions ---
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayToInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.analytics_api.execution_arn}/*/*"
}

# --- Output the API URL ---
output "api_endpoint_url" {
  description = "The public URL for the API endpoint"
  value       = "${aws_api_gateway_deployment.api_deployment.invoke_url}${aws_api_gateway_stage.api_stage.path}"
}