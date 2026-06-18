resource "aws_s3_bucket" "logs" {
  bucket = "public-logs-insecure"
  acl    = "public-read"
}
