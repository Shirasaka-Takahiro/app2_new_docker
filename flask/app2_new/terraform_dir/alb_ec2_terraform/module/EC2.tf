##Web Instance
resource "aws_instance" "ec2-web" {
  count = var.count_number
  ami   = var.ami
  subnet_id = element(values(aws_subnet.public_subnets)[*].id, count.index % 2)
  vpc_security_group_ids = [
    aws_security_group.common.id,
    aws_security_group.ec2.id
  ]
  key_name      = aws_key_pair.key.id
  instance_type = var.instance_type
  root_block_device {
    volume_type = var.volume_type
    volume_size = var.volume_size
  }

  tags = {
    Name = "${var.general_config["project_name"]}-${var.general_config["env"]}-${format("web%02d", count.index + 1)}"
  }
}

##Elastic IP
resource "aws_eip" "eip_ec2" {
  vpc      = true
  count    = length(aws_instance.ec2-web)
  instance = element(aws_instance.ec2-web.*.id, count.index % 2)


  tags = {
    Name = "${var.general_config["project_name"]}-${var.general_config["env"]}-${format("eip%02d", count.index + 1)}"
  }
}

##Key Pair
resource "aws_key_pair" "key" {
  key_name   = var.key_name
  public_key = file("/home/example.pub")
}