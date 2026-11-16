resource "aws_s3_bucket" "image_storage" {
  bucket = var.bucket_id


  force_destroy = true


  tags = {
    Name        = var.bucket_id
    Environment = "prod"
    Project     = "Sharingan-ai"
  }
}


resource "aws_s3_bucket_server_side_encryption_configuration" "image_storage_encryption" {
  bucket = aws_s3_bucket.image_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "image_storage_cors" {
  bucket = aws_s3_bucket.image_storage.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["*"] //will change it in future
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}





resource "aws_dynamodb_table" "shariangan_table" {
  name         = var.dynamo_table_id
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {
    name = "pk"
    type = "S"
  }
  attribute {
    name = "sk"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    Name        = var.dynamo_table_id
    Environment = "prod"
    Project     = "Sharingan-ai"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }
}





