variable "aws_region" {
  type    = string
  default = "eu-central-1"
}

variable "manage_buckets" {
  description = "If true, Terraform will create S3 buckets. If false, it will use existing bucket names."
  type        = bool
  default     = false
}

variable "s3_data_bucket" {
  type    = string
  default = "sroad-data-2"
}

variable "s3_athena_results_bucket" {
  type    = string
  default = "sroad-athena-results-2"
}

variable "manage_glue" {
  type    = bool
  default = false
}

variable "glue_database_name" {
  type    = string
  default = "sroad_analytics"
}

variable "manage_athena_workgroup" {
  type    = bool
  default = false
}

variable "athena_workgroup_name" {
  type    = string
  default = "primary"
}

variable "manage_iam" {
  type    = bool
  default = false
}

variable "iam_user_name" {
  type    = string
  default = "SROADUser"
}

variable "iam_policy_name" {
  type    = string
  default = "SROADAccessPolicy"
}
