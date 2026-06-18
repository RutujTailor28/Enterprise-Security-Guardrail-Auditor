# Secure network — restricted security groups with no internet-wide ingress.

resource "aws_security_group" "bastion" {
  name        = "bastion-restricted"
  description = "SSH limited to operations VPN"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["203.0.113.10/32"]
  }
}

resource "aws_security_group" "web_tier" {
  name        = "web-tier-secure"
  description = "HTTP/HTTPS from load balancer subnet only"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["172.16.10.0/24"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["172.16.10.0/24"]
  }
}
