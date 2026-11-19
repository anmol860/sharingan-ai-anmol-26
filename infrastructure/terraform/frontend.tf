// s3 bucket for frontend
resource "aws_s3_bucket" "frontend_bucket" {
  bucket = "${var.prj_name}-frontend"
  force_destroy = true

  tags = {
    Name = "${var.prj_name}-frontend"
    Environment = "prod"
    Project = "Sharingan-ai"
  }
}


//for uploading index.html and index.js to S3 bucket automatically
resource "aws_s3_object" "index_html" {
  bucket = aws_s3_bucket.frontend_bucket.id
  key = "index.html"
  source = "${path.module}/../../frontend/index.html"
  content_type = "text/html"
  etag = filemd5("${path.module}/../../frontend/index.html")
}

resource "aws_s3_object" "index_js"{
    bucket = aws_s3_bucket.frontend_bucket.id
    key = "index.js"
    source = "${path.module}/../../frontend/index.js"
    content_type = "text/javascript"
    etag = filemd5("${path.module}/../../frontend/index.js")
}



// Cloudfront origin access control for s3 bucket
resource "aws_cloudfront_origin_access_control" "frontend_oac" {
    name = "${var.prj_name}-frontend-oac"
    description = "OAC for ${var.prj_name}-frontend"
    origin_access_control_origin_type = "s3"
    signing_behavior = "always"
    signing_protocol = "sigv4"
}



//creating cloudfront distribution for s3 bucket
resource "aws_cloudfront_distribution" "frontend_cdn" {
  enabled = true
  default_root_object = "index.html"

  origin {
    domain_name = aws_s3_bucket.frontend_bucket.bucket_regional_domain_name
    origin_id = "S3FrontendOrigin"
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend_oac.id
  }

  default_cache_behavior {
    allowed_methods = ["GET", "HEAD"]
    cached_methods = ["GET", "HEAD"]
    target_origin_id = "S3FrontendOrigin"
    viewer_protocol_policy = "redirect-to-https"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}



// bucket policy for s3 cdn
resource "aws_s3_bucket_policy" "frontend_bucket_policy" {
  bucket = aws_s3_bucket.frontend_bucket.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "s3:GetObject"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Resource = "${aws_s3_bucket.frontend_bucket.arn}/*"
        Condition = {
            StringEquals = {
                "AWS:SourceArn" = aws_cloudfront_distribution.frontend_cdn.arn
            }
        }
      }
    ]
  })
}


