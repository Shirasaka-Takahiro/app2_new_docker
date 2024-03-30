##Subnet Group
resource "aws_db_subnet_group" "default_subnet_group" {
  name       = "${var.general_config["project_name"]}-${var.general_config["env"]}-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${var.general_config["project_name"]}-${var.general_config["env"]}-subnet-group"
  }
}

##Parameter Group
resource "aws_db_parameter_group" "default_parameter_group" {
  name   = "${var.general_config["project_name"]}-${var.general_config["env"]}-parameter-group"
  family = "mysql8.0"

  parameter {
    name         = "character_set_server"
    value        = "utf8mb4"
    apply_method = "immediate"
  }

  parameter {
    name         = "character_set_client"
    value        = "utf8mb4"
    apply_method = "immediate"
  }

  parameter {
    name         = "general_log"
    value        = "1"
    apply_method = "immediate"
  }

  parameter {
    name         = "slow_query_log"
    value        = "1"
    apply_method = "immediate"
  }

  parameter {
    name         = "log_output"
    value        = "TABLE"
    apply_method = "immediate"
  }

  parameter {
    name         = "time_zone"
    value        = "Asia/Tokyo"
    apply_method = "immediate"
  }

}

##Option Group
resource "aws_db_option_group" "default_option_group" {
  name                 = "${var.general_config["project_name"]}-${var.general_config["env"]}-option-group"
  engine_name          = var.engine_name
  major_engine_version = var.major_engine_version
}

##DB Instance
resource "aws_db_instance" "db_instance" {
  engine                              = var.engine
  engine_version                      = var.engine_version
  license_model                       = "general-public-license"
  identifier                          = "${var.general_config["project_name"]}-${var.general_config["env"]}-db"
  username                            = var.username
  password                            = var.password
  instance_class                      = var.instance_class
  storage_type                        = var.storage_type
  allocated_storage                   = var.allocated_storage
  multi_az                            = var.multi_az
  db_subnet_group_name                = aws_db_subnet_group.default_subnet_group.name
  publicly_accessible                 = false
  vpc_security_group_ids              = [var.internal_sg_id]
  port                                = 3306
  iam_database_authentication_enabled = false
  name                                = "testdb"
  parameter_group_name                = aws_db_parameter_group.default_parameter_group.name
  option_group_name                   = aws_db_option_group.default_option_group.name
  auto_minor_version_upgrade          = var.auto_minor_version_upgrade
  backup_retention_period             = var.backup_retention_period
  backup_window                       = "19:00-20:00"
  copy_tags_to_snapshot               = true
  storage_encrypted                   = true
  performance_insights_enabled        = false
  maintenance_window                  = "Wed:20:00-Wed:21:00"
  deletion_protection                 = var.deletion_protection 
  skip_final_snapshot                 = true
  apply_immediately                   = false

  tags = {
    Name = "${var.general_config["project_name"]}-${var.general_config["env"]}-db"
  }
}