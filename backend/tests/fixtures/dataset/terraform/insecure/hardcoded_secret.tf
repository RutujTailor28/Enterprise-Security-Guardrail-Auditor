variable "db_password" {
  default = "SuperSecret123!"
}

resource "aws_db_instance" "main" {
  identifier = "main-db-insecure"
  engine     = "postgres"
  password   = "HardcodedPassword!"
}
