resource "aws_db_instance" "unencrypted" {
  identifier          = "unencrypted-db"
  engine              = "postgres"
  storage_encrypted   = false
  publicly_accessible = false
}
