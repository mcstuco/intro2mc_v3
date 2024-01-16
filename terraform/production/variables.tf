# Whenever the contents of this block changes, the host should be re-provisioned
locals {
  reprovision_trigger = <<EOF
    # Trigger reprovision on variable changes:
    ${var.hostname}
    ${var.ssh_username}
    ${var.ssh_private_key_path}
    ${var.ssh_public_key_path}
    ${var.swap_file_size}
    ${var.swap_swappiness}
    ${var.reprovision_trigger}
    # Trigger reprovision on file changes:
    ${file("${path.module}/scripts/provision-ssh.sh")}
    ${file("${path.module}/scripts/provision-docker.sh")}
    ${file("${path.module}/scripts/provision-ebs.sh")}
    ${file("${path.module}/scripts/provision-mc.sh")}
    ${file("${path.module}/scripts/provision-swap.sh")}
  EOF
}

# Instance

locals {
  availability_zone = data.aws_availability_zones.this.names[0] # use the first available AZ in the region (AWS ensures this is constant per user)
}

variable "hostname" {
  description = "Hostname by which this service is identified in metrics, logs etc"
  default     = "mcstuco"
}

variable "instance_type" {
  description = "See https://aws.amazon.com/ec2/instance-types/ for options; for example, typical values for small workloads are `\"t2.nano\"`, `\"t2.micro\"`, `\"t2.small\"`, `\"t2.medium\"`, and `\"t2.large\"`"
  # default     = "t2.xlarge"
  default     = "t4g.xlarge" # t4g is arm, t2 is amd
}

variable "instance_ami" {
  description = "See https://cloud-images.ubuntu.com/locator/ec2/ for options"
  # default     = "ami-02675d30b814d1daa" # us-east-1	Jammy Jellyfish	22.04 LTS	amd64	hvm:ebs-ssd	20230728 ami-02675d30b814d1daa	hvm (use with t2)
  default     = "ami-067cf009aedb2612d" # us-east-1	Jammy Jellyfish	22.04 LTS	arm64	hvm:ebs-ssd	20230728	ami-067cf009aedb2612d	hvm (use with t4g)
}

variable "root_volume_size" {
  description = "Size (in GiB) of the EBS volume that will be created and mounted as the root fs for the host. Minimum >= 8 GiB"
  default     = 16 # this matches the other defaults, including the selected AMI
}

# SSH

variable "ssh_private_key_path" {
  description = "SSH private key file path, relative to Terraform project root"
  default     = "~/.ssh/id_rsa"
}

variable "ssh_public_key_path" {
  description = "SSH public key file path, relative to Terraform project root"
  default     = "~/.ssh/id_rsa.pub"
}

variable "ssh_username" {
  description = "Default username built into the AMI (see 'instance_ami')"
  default     = "ubuntu"
}

# VPC

variable "vpc_id" {
  description = "ID of the VPC our host should join; if empty, joins your Default VPC"
  default     = ""
}

# Reprovisioning

variable "reprovision_trigger" {
  description = "An arbitrary string value; when this value changes, the host needs to be reprovisioned"
  default     = ""
}

# EBS

variable "ebs_volume_size" {
  description = "Size (in GiB) of the separated EBS volume. Minimum >= 8 GiB"
  default     = 16 # this matches the other defaults, including the selected AMI
}

# Swap

variable "swap_file_size" {
  description = "Size of the swap file allocated on the root volume"
  default     = "2048M" # a smallish default to match default 8 GiB EBS root volume
}

variable "swap_swappiness" {
  description = "Swappiness value provided when creating the swap file"
  default     = "10" # 100 will make the host use the swap as much as possible, 0 will make it use only in case of emergency
}

# Ports

variable "allow_incoming_http" {
  description = "Whether to allow incoming HTTP traffic on the host security group"
  default     = true
}

variable "allow_incoming_https" {
  description = "Whether to allow incoming HTTPS traffic on the host security group"
  default     = true
}

variable "allow_incoming_dns" {
  description = "Whether to allow incoming DNS traffic on the host security group"
  default     = false
}

variable "allow_incoming_minecraft" {
  description = "Whether to allow incoming Minecraft traffic on the host security group"
  default     = true
}

# Tags

variable "tags" {
  description = "AWS Tags to add to all resources created (where possible); see https://aws.amazon.com/answers/account-management/aws-tagging-strategies/"
  type        = map(string)
  default = {
    "Name"      = "mcstuco"
    "ManagedBy" = "Terraform"
  }
}
