data "archive_file" "ai_worker_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../build/ai-worker"
  output_path = "${path.module}/.terraform/tmp/ai-worker.zip"
  excludes    = ["__pycache__"]
}

resource "aws_s3_object" "ai_worker_package" {
  bucket = aws_s3_bucket.image_storage.id
  key    = "deployments/ai-worker.zip"
  source = data.archive_file.ai_worker_zip.output_path
  etag   = data.archive_file.ai_worker_zip.output_md5
}


resource "aws_lambda_function" "ai_worker" {
  function_name    = "${var.prj_name}-ai-worker"
  role             = aws_iam_role.ai_worker_role.arn
  runtime          = "python3.12"
  handler          = "worker.lambda_handler"
  s3_bucket        = aws_s3_object.ai_worker_package.bucket
  s3_key           = aws_s3_object.ai_worker_package.key
  source_code_hash = data.archive_file.ai_worker_zip.output_base64sha256
  memory_size      = 512
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