terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }

    google = {
      source  = "hashicorp/google"
      version = "~> 8.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "google" {
  region = var.gcp_region
  zone   = var.gcp_zone
}