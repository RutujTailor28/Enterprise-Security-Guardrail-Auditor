resource "aws_security_group" "wide_open" {
  name = "wide-open-sg-insecure"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
