variable "general_config" {
  type = map(any)
}
variable "private_subnet_ids" {}
variable "engine_name" {}
variable "major_engine_version" {}
variable "engine" {}
variable "engine_version" {}
variable "username" {}
variable "password" {}
variable "instance_class" {}
variable "storage_type" {}
variable "allocated_storage" {}
variable "multi_az" {}
variable "internal_sg_id" {}
variable "auto_minor_version_upgrade" {}
variable "backup_retention_period" {}
variable "deletion_protection" {}