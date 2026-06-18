# Secure data tier — encrypted RDS with backups and least-privilege IAM.

resource "aws_db_instance" "analytics" {
  identifier              = "analytics-db-secure"
  engine                  = "postgres"
  instance_class          = "db.t3.small"
  storage_encrypted       = true
  kms_key_id              = "arn:aws:kms:us-east-1:123456789012:key/example"
  publicly_accessible     = false
  backup_retention_period = 30
  skip_final_snapshot     = true
}

resource "aws_iam_policy" "read_only" {
  name = "analytics-read-only"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
        ]
        Resource = [
          "arn:aws:s3:::company-analytics",
          "arn:aws:s3:::company-analytics/objects",
        ]
      },
    ]
  })
}
