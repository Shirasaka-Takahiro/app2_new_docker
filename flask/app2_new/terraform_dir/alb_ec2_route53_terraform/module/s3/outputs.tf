output "bucket_id" {
  value = aws_s3_bucket.bucket_alb_access_log.id
}

output "bucket_domain_name" {
  value = aws_s3_bucket.bucket_alb_access_log.bucket_domain_name
}

output "bucket_name" {
  value = aws_s3_bucket.bucket_alb_access_log.bucket
}