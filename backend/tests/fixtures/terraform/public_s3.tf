resource "aws_s3_bucket" "logs" {
  bucket = "my-logs-bucket"
  acl    = "public-read"
}
