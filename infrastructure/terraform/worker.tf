data "archive_file" "ai_worker_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../backend/ai-worker"
  output_path = "${path.module}/.terraform/tmp/ai-worker.zip"
}

resource "aws_lambda_function" "ai_worker" {
  function_name    = "${var.prj_name}-ai-worker"
  role             = aws_iam_role.ai_worker_role.arn
  runtime          = "python3.12"
  handler          = "worker.lambda_handler"
  filename         = data.archive_file.ai_worker_zip.output_path
  source_code_hash = data.archive_file.ai_worker_zip.output_base64sha256
  timeout          = 30
  architectures    = ["arm64"]

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.image_storage.id
      TABLE_NAME  = aws_dynamodb_table.shariangan_table.name
    }
  }
}


resource "aws_lambda_permission" "allow_s3_trigger" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ai_worker.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.image_storage.arn
}

resource "aws_s3_bucket_notification" "ai_worker_trigger" {
  bucket = aws_s3_bucket.image_storage.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.ai_worker.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "uploads/"
  }
  depends_on = [aws_lambda_permission.allow_s3_trigger]
}