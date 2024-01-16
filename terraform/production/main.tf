# Snapshot EBS: https://stackoverflow.com/questions/49488416/terraform-create-snapshot-of-ebs-and-then-convert-snapshot-to-ebs-and-attach-t

terraform {
  # local backend
  backend "local" {
    path = "terraform.tfstate"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.14.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Create the main EBS volume
resource "aws_ebs_volume" "this" {
  availability_zone = local.availability_zone
  size              = var.ebs_volume_size
  encrypted         = false
  tags              = merge(var.tags, tomap({ "Name" = "${var.hostname}-root" })) # give the root EBS volume a name (+ other possible tags) that makes it easier to identify as belonging to this host
}

# Create the main EC2 instance
# https://www.terraform.io/docs/providers/aws/r/instance.html
resource "aws_instance" "this" {
  instance_type          = var.instance_type
  ami                    = var.instance_ami
  availability_zone      = local.availability_zone
  key_name               = aws_key_pair.this.id # the name of the SSH keypair to use for provisioning
  vpc_security_group_ids = ["${aws_security_group.this.id}"]
  subnet_id              = data.aws_subnet.this.id
  user_data              = sha1(local.reprovision_trigger) # this value isn't used by the EC2 instance, but its change will trigger re-creation of the resource
  tags                   = merge(var.tags, tomap({ "Name" = "${var.hostname}" }))
  volume_tags            = merge(var.tags, tomap({ "Name" = "${var.hostname}-root" })) # give the root EBS volume a name (+ other possible tags) that makes it easier to identify as belonging to this host

  root_block_device {
    volume_size = var.root_volume_size
  }

  connection {
    host = self.public_ip
    user = var.ssh_username
    # Uncomment the following and comment agent to use non-encrypted private key
    # private_key = file("${var.ssh_private_key_path}")
    # agent       = false # don't use SSH agent because we have the private key right here
    agent = true
  }

  provisioner "remote-exec" {
    inline = [
      "sudo hostnamectl set-hostname ${var.hostname}",
      "echo 127.0.0.1 ${var.hostname} | sudo tee -a /etc/hosts", # https://askubuntu.com/a/59517
    ]
  }

  provisioner "remote-exec" {
    script = "${path.module}/scripts/provision-ssh.sh"
  }

  provisioner "remote-exec" {
    script = "${path.module}/scripts/provision-docker.sh"
  }

  provisioner "file" {
    source      = "${path.module}/scripts/provision-swap.sh"
    destination = "/home/${var.ssh_username}/provision-swap.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "sh /home/${var.ssh_username}/provision-swap.sh ${var.swap_file_size} ${var.swap_swappiness}",
      "rm /home/${var.ssh_username}/provision-swap.sh",
    ]
  }
}

# Attach the separate data volume to the instance, if so configured

resource "aws_volume_attachment" "this" {
  count       = var.data_volume_id == "" ? 0 : 1 # only create this resource if an external EBS data volume was provided
  device_name = "/dev/xvdh"                      # note: this depends on the AMI, and can't be arbitrarily changed
  instance_id = aws_instance.this.id
  volume_id   = var.data_volume_id
}

resource "null_resource" "provisioners" {
  count      = var.data_volume_id == "" ? 0 : 1 # only create this resource if an external EBS data volume was provided
  depends_on = [aws_volume_attachment.this]     # because we depend on the EBS volume being available

  triggers = {
    public_ip            = aws_instance.this.public_ip
    ssh_username         = var.ssh_username
    ssh_private_key_path = var.ssh_private_key_path
    device_name          = aws_volume_attachment.this[count.index].device_name
  }

  connection {
    host = self.triggers.public_ip
    user = self.triggers.ssh_username
    # Uncomment the following and comment agent to use non-encrypted private key
    # private_key = file("${self.triggers.ssh_private_key_path}")
    # agent       = false # don't use SSH agent because we have the private key right here
    agent = true # don't use SSH agent because we have the private key right here
  }

  provisioner "remote-exec" {
    script = "${path.module}/scripts/provision-ebs.sh"
  }

  provisioner "remote-exec" {
    connection {
      agent = true
    }
    script = "${path.module}/scripts/provision-mc.sh"
  }

  # provisioner "file" {
  #   source      = "/home/koke_cacao/Documents/Koke_Cacao/Minecraft/mcstuco/lobby/world"
  #   destination = "/data/mcstuco/lobby/world"
  # }

  # provisioner "remote-exec" { # for some reason will fail?
  #   when   = destroy
  #   inline = ["sudo umount -v ${self.triggers.device_name}"]
  # }
}
