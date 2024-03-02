output "instance_ids" {
  value = aws_instance.ec2-web.*.id
}

output "public_ip" {
  value = aws_eip.eip_ec2.*.public_ip
}