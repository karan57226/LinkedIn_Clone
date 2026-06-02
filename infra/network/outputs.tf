output "vpc_id" {
  description = "VPC ID."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs for the load balancer and NAT Gateway."
  value       = values(aws_subnet.public)[*].id
}

output "private_app_subnet_ids" {
  description = "Private subnet IDs for the backend service."
  value       = values(aws_subnet.private_app)[*].id
}

output "private_db_subnet_ids" {
  description = "Private subnet IDs for RDS."
  value       = values(aws_subnet.private_db)[*].id
}

output "alb_security_group_id" {
  description = "Security group ID for the Application Load Balancer."
  value       = aws_security_group.alb.id
}

output "backend_security_group_id" {
  description = "Security group ID for the backend API."
  value       = aws_security_group.backend.id
}

output "rds_security_group_id" {
  description = "Security group ID for RDS PostgreSQL."
  value       = aws_security_group.rds.id
}
