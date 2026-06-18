resource "aws_s3_bucket" "no_logs" {
  bucket = "no-logs-bucket"
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "no_logs" {
  bucket                  = aws_s3_bucket.no_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
