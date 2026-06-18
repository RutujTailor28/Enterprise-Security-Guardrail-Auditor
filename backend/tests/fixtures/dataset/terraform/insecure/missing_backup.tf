resource "aws_db_instance" "no_backup" {
  identifier              = "no-backup-db-insecure"
  engine                  = "postgres"
  backup_retention_period = 0
  storage_encrypted       = true
  publicly_accessible     = false
}

resource "aws_s3_bucket" "no_versioning" {
  bucket = "no-version-bucket-insecure"
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "no_versioning" {
  bucket                  = aws_s3_bucket.no_versioning.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
