variable "db_password" {
  default = "SuperSecret123!"
}

resource "aws_db_instance" "main" {
  password = "HardcodedPassword!"
}
