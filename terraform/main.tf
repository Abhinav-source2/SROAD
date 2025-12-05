terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# -------------------------
# Get caller identity (for outputs)
# -------------------------
data "aws_caller_identity" "current" {}

# -------------------------
# S3: either manage (create) or use existing
# -------------------------
# If manage_buckets = true -> create buckets
resource "aws_s3_bucket" "sroad_data" {
  count         = var.manage_buckets ? 1 : 0
  bucket        = var.s3_data_bucket
  acl           = "private"
  force_destroy = false
}

resource "aws_s3_bucket" "athena_results" {
  count         = var.manage_buckets ? 1 : 0
  bucket        = var.s3_athena_results_bucket
  acl           = "private"
  force_destroy = false
}

# If not managing, reference existing buckets
data "aws_s3_bucket" "sroad_data" {
  count  = var.manage_buckets ? 0 : 1
  bucket = var.s3_data_bucket
}

data "aws_s3_bucket" "athena_results" {
  count  = var.manage_buckets ? 0 : 1
  bucket = var.s3_athena_results_bucket
}

# -------------------------
# Glue database: create only if requested
# -------------------------
resource "aws_glue_catalog_database" "sroad_db" {
  count = var.manage_glue ? 1 : 0
  name  = var.glue_database_name
}

# -------------------------
# Athena Workgroup (create or use existing name)
# -------------------------
resource "aws_athena_workgroup" "sroad_workgroup" {
  count = var.manage_athena_workgroup ? 1 : 0
  name  = var.athena_workgroup_name
  state = "ENABLED"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = false

    result_configuration {
      output_location = "s3://${var.s3_athena_results_bucket}/"
    }
  }
}

# -------------------------
# IAM: optional — create user + policy only if enabled
# -------------------------
resource "aws_iam_user" "sroad_user" {
  count = var.manage_iam ? 1 : 0
  name  = var.iam_user_name
  path  = "/"
}

resource "aws_iam_policy" "sroad_policy" {
  count = var.manage_iam ? 1 : 0
  name  = var.iam_policy_name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:StopQueryExecution",
          "athena:GetWorkGroup",
          "athena:ListWorkGroups"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:GetTables",
          "glue:GetTable"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_data_bucket}",
          "arn:aws:s3:::${var.s3_data_bucket}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_athena_results_bucket}",
          "arn:aws:s3:::${var.s3_athena_results_bucket}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "sroad_attach" {
  count      = var.manage_iam ? 1 : 0
  user       = aws_iam_user.sroad_user[0].name
  policy_arn = aws_iam_policy.sroad_policy[0].arn
}

# -------------------------
# Outputs
# -------------------------
output "current_account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "s3_data_bucket" {
  value = var.s3_data_bucket
}

output "s3_athena_results_bucket" {
  value = var.s3_athena_results_bucket
}

output "glue_database" {
  value = var.glue_database_name
}

output "athena_workgroup" {
  value = var.athena_workgroup_name
}

output "iam_user" {
  value = var.manage_iam ? aws_iam_user.sroad_user[0].name : "not-managed"
}
