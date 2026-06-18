# Kitchen-sink insecure stack — multiple misconfigurations in one scan.

resource "aws_s3_bucket" "exposed" {
  bucket = "multi-risk-exposed"
  acl    = "public-read"
}

resource "aws_security_group" "edge" {
  name = "multi-risk-edge"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_policy" "wildcard" {
  name = "multi-risk-admin"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      },
    ]
  })
}

resource "aws_db_instance" "public_db" {
  identifier            = "multi-risk-db"
  engine                = "postgres"
  password              = "PlaintextDbPassword!"
  storage_encrypted     = false
  publicly_accessible   = true
  backup_retention_period = 0
}
