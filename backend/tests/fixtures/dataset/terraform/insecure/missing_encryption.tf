resource "aws_db_instance" "unencrypted" {
  identifier          = "unencrypted-db-insecure"
  engine              = "postgres"
  storage_encrypted   = false
  publicly_accessible = false
}

resource "aws_s3_bucket" "unencrypted" {
  bucket = "unencrypted-bucket-insecure"
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "unencrypted" {
  bucket                  = aws_s3_bucket.unencrypted.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
