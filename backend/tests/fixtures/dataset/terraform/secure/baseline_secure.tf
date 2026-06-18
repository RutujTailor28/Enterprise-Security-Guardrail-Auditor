# Secure baseline — private S3 with encryption, logging, versioning, and public access block.

resource "aws_s3_bucket" "app_data" {
  bucket = "company-app-data-secure"
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  versioning {
    enabled = true
  }

  logging {
    target_bucket = "company-audit-logs"
    target_prefix = "s3-access/"
  }
}

resource "aws_s3_bucket_public_access_block" "app_data" {
  bucket                  = aws_s3_bucket.app_data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_security_group" "app" {
  name        = "app-sg-secure"
  description = "HTTPS from corporate network only"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "app" {
  identifier                = "app-db-secure"
  engine                    = "postgres"
  instance_class            = "db.t3.micro"
  storage_encrypted         = true
  publicly_accessible       = false
  backup_retention_period   = 14
  skip_final_snapshot       = true
}
