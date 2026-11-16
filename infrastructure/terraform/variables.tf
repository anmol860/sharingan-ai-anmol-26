variable "aws_region" {
  type        = string
  description = "AWS region for this project"
  default     = "us-west-2"
}

variable "gcp_region" {
  type        = string
  description = "GCP region for this project"
  default     = "us-west-1"
}

variable "gcp_zone" {
  type        = string
  description = "GCP zone for this project"
  default     = "us-west-1a"
}

variable "bucket_id" {
  type        = string
  description = "bucket id for this project"
  default     = "image-storage-anmol-26"
}

variable "dynamo_table_id" {
  type        = string
  description = "dynamo table name for this project"
  default     = "sharingan-ai-anmol-26"
}

variable "prj_name" {
  type        = string
  description = "Prj name"
  default     = "sharingan-ai"
}