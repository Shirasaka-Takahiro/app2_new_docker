variable "general_config" {
  type = map(any)
}
variable "vpc_id" {}
variable "public_subnet_ids" {}
variable "alb_http_sg_id" {}
variable "alb_https_sg_id" {}
variable "instance_ids" {}
variable "alb_access_log_bucket_id" {}