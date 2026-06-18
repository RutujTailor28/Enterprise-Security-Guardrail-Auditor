resource "aws_security_group" "windows" {
  name = "windows-sg-insecure"

  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
