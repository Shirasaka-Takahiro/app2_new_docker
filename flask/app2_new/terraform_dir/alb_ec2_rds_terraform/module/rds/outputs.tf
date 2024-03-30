output "rds_endpoint" {
  value = aws_db_instance.db_instance.endpoint
}

output "rds_identifier" {
  value = aws_db_instance.db_instance.identifier
}