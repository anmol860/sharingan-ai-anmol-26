// creating user pool for storing user details
resource "aws_cognito_user_pool" "user_pool" {
  name = "${var.prj_name}-user-pool"
  username_attributes = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length = 8
    require_lowercase = true
    require_numbers = true
    require_symbols = false
    require_uppercase = false
  }
}


// aws login domain
resource "aws_cognito_user_pool_domain" "auth_domain" {
  domain = "${var.prj_name}-anmol-26"
  user_pool_id = aws_cognito_user_pool.user_pool.id
}


// connects congito to cloudfornt
resource "aws_cognito_user_pool_client" "web_client" {
  name = "${var.prj_name}-web-client"
  user_pool_id = aws_cognito_user_pool.user_pool.id
  generate_secret = false
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows = ["implicit"]
  allowed_oauth_scopes = ["openid", "email"]
  supported_identity_providers = ["COGNITO"]

  callback_urls = [
    "https://${aws_cloudfront_distribution.frontend_cdn.domain_name}",
    "https://${aws_cloudfront_distribution.frontend_cdn.domain_name}/"
  ]

  logout_urls = [
    "https://${aws_cloudfront_distribution.frontend_cdn.domain_name}",
    "https://${aws_cloudfront_distribution.frontend_cdn.domain_name}/"
  ]
}


output "frontend_url" {
  value = "https://${aws_cloudfront_distribution.frontend_cdn.domain_name}"
}

output "cognito_domain" {
  value = "https://${aws_cognito_user_pool_domain.auth_domain.domain}.auth.${var.aws_region}.amazoncognito.com"
}

output "cognito_client" {
  value = aws_cognito_user_pool_client.web_client.id
}