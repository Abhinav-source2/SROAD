# -------------------------------
# AWS Region (YOUR region)
# -------------------------------
aws_region = "ap-southeast-2"

# -------------------------------
# S3 buckets already exist
# -------------------------------
manage_buckets           = false
s3_data_bucket           = "sroad-data-2"
s3_athena_results_bucket = "sroad-athena-results-2"

# -------------------------------
# Glue Database already exists
# -------------------------------
manage_glue        = false
glue_database_name = "sroad_analytics"

# -------------------------------
# Athena Workgroup already exists
# -------------------------------
manage_athena_workgroup = false
athena_workgroup_name   = "primary"

# -------------------------------
# IAM is already created manually
# (must stay false because your
#  IAM user has no permission to
#  create users or policies)
# -------------------------------
manage_iam      = false
iam_user_name   = "AmazonS3FullAccess"
iam_policy_name = "SROAD-AI-Agent-Policy"
