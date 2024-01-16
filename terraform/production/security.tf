# Create an SSH key pair for accessing the EC2 instance
resource "aws_key_pair" "this" {
  public_key = file("${var.ssh_public_key_path}")
}

# Create our default security group to access the instance, over specific protocols
resource "aws_security_group" "this" {
  vpc_id = data.aws_vpc.this.id
  tags   = merge(var.tags, tomap({ "Name" = "${var.hostname}" }))
}

# Incoming SSH & outgoing ANY needs to be allowed for provisioning to work

resource "aws_security_group_rule" "outgoing_any" {
  security_group_id = aws_security_group.this.id
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "incoming_ssh" {
  security_group_id = aws_security_group.this.id
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}

# http/https ports

resource "aws_security_group_rule" "incoming_http" {
  count             = var.allow_incoming_http ? 1 : 0
  security_group_id = aws_security_group.this.id
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "incoming_https" {
  count             = var.allow_incoming_https ? 1 : 0
  security_group_id = aws_security_group.this.id
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}

# dns ports

resource "aws_security_group_rule" "incoming_dns_tcp" {
  count             = var.allow_incoming_dns ? 1 : 0
  security_group_id = aws_security_group.this.id
  type              = "ingress"
  from_port         = 53
  to_port           = 53
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "incoming_dns_udp" {
  count             = var.allow_incoming_dns ? 1 : 0
  security_group_id = aws_security_group.this.id
  type              = "ingress"
  from_port         = 53
  to_port           = 53
  protocol          = "udp"
  cidr_blocks       = ["0.0.0.0/0"]
}

# minecraft ports

resource "aws_security_group_rule" "incoming_mc_tcp" {
  count             = var.allow_incoming_minecraft ? 1 : 0
  security_group_id = aws_security_group.this.id
  type              = "ingress"
  from_port         = 25565
  to_port           = 25699
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "incoming_mc_udp" {
  count             = var.allow_incoming_minecraft ? 1 : 0
  security_group_id = aws_security_group.this.id
  type              = "ingress"
  from_port         = 25565
  to_port           = 25699
  protocol          = "udp"
  cidr_blocks       = ["0.0.0.0/0"]
}
