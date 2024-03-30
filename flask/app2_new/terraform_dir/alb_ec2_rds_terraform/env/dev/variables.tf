##General Config
variable "general_config" {
  type = map(any)
  default = {
    project_name = "example"
    env          = "dev"
  }
}

##Access Key
variable "access_key" {
  description = "Access Key"
  type        = string
}

##Secret Key
variable "secret_key" {
  description = "Secret Key"
  type        = string
}

##Network
variable "vpc" {
  description = "CIDR BLOCK for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "availability_zones" {
  type = map(any)
  default = {
    availability_zones = {
      az-1a = {
        az = "ap-northeast-1a"
      },
      az-1c = {
        az = "ap-northeast-1c"
      }
    }
  }
}

variable "public_subnets" {
  type = map(any)
  default = {
    subnets = {
      public-1a = {
        name = "public-1a",
        cidr = "10.0.10.0/24",
        az   = "ap-northeast-1a"
      },
      public-1c = {
        name = "public-1c",
        cidr = "10.0.30.0/24",
        az   = "ap-northeast-1c"
      }
    }
  }
}

variable "private_subnets" {
  type = map(any)
  default = {
    subnets = {
      private-1a = {
        name = "private-1a"
        cidr = "10.0.20.0/24"
        az   = "ap-northeast-1a"
      },
      private-1c = {
        name = "private-1c"
        cidr = "10.0.40.0/24"
        az   = "ap-northeast-1c"
      }
    }
  }
}

##Security Group CIDR
variable "operation_sg_1_cidr" {
  type        = list(string)
  default = []
}

variable "operation_sg_2_cidr" {
  type        = list(string)
  default = []
}

variable "operation_sg_3_cidr" {
  type        = list(string)
  default = []
}

##EC2
variable "count_number" {
  description = "Number of ec2 instance"
  type        = string
}

variable "ami" {
  description = "ID of AMI to use for ec2 instance"
  type        = string
}

variable "instance_type" {
  description = "The type of instance"
  type        = string
}

variable "volume_type" {
  description = "The type of root block device"
  type        = string
}

variable "volume_size" {
  description = "The size of root block device"
  type        = string
}

variable "key_name" {
  description = "key name of the key pair"
  type        = string
  default     = "example.pub"
}

##RDS Option Group
variable "engine_name" {
  type    = string
  default = "mysql"
}

variable "major_engine_version" {
  type    = string
  default = "8.0"
}

##RDS Instance
variable "engine" {
  type    = string
  default = "mysql"
}

variable "engine_version" {
  type    = string
  default = "8.0"
}

variable "username" {
  description = "root username of db instance"
  type        = string
}

variable "password" {
  description = "root password of db instance"
  type        = string
}

variable "instance_class" {
  description = "The class of db instance"
  type        = string
  default     = "db.t3.medium"
}

variable "storage_type" {
  description = "The storage type of db instance"
  type        = string
  default     = "gp2"
}

variable "allocated_storage" {
  description = "The allocated storage of db instance"
  default     = 20
}

variable "multi_az" {
  description = "multi az of db instance"
  type        = string
  default     = "true"
}

variable "auto_minor_version_upgrade" {
  description = "enable or disable of auto minor version upgrade, true or false"
  type        = string
}

variable "backup_retention_period" {
  description = "retention period of backup"
  type        = string
}

variable "deletion_protection" {
  description = "enable or disable of deletion protection, true or false"
  type        = string
}