data "archive_file" "api_handler_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../backend/api-handler"
  output_path = "${path.module}/../../api-handler.zip"
}

resource "aws_lambda_function" "api_handler" {
  function_name    = "${var.prj_name}-api-handler"
  role             = aws_iam_role.api_handler_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  architectures    = ["arm64"]
  filename         = data.archive_file.api_handler_zip.output_path
  source_code_hash = data.archive_file.api_handler_zip.output_base64sha256
  timeout          = 10

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.image_storage.id
      TABLE_NAME  = aws_dynamodb_table.shariangan_table.name
    }
  }

}


resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.prj_name}-http-api"
  protocol_type = "HTTP"
  route_key     = "POST /uploads"
  target        = aws_lambda_function.api_handler.arn

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET", "OPTIONS"]
    allow_headers = ["content-type"]
  }
}


resource "aws_apigatewayv2_integration" "api_handler_integration"{
  api_id = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri = aws_lambda_function.api_handler.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "get_upload_status"{
  api_id = aws_apigatewayv2_api.http_api.id
  route_key = "GET /uploads/{image_id}"
  target = "integrations/${aws_apigatewayv2_integration.api_handler_integration.id}"
}



output "api_endpoint_url" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
}