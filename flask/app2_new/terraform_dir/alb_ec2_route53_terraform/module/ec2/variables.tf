variable "general_config" {
  type = map(any)
}
variable "internal_sg_id" {}
variable "operation_sg_1_id" {}
variable "operation_sg_2_id" {}
variable "operation_sg_3_id" {}
variable "public_subnets" {}
variable "count_number" {}
variable "ami" {}
variable "instance_type" {}
variable "volume_type" {}
variable "volume_size" {}
variable "key_name" {}
variable "public_subnet_ids" {}