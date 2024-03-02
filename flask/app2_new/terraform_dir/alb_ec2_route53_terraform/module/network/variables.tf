variable "general_config" {
  type = map(any)
}
variable "vpc_cidr" {}
variable "availability_zones" {}
variable "public_subnets" {}
variable "private_subnets" {}