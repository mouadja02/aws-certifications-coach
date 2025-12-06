# Terraform Variables for AWS Certifications Coach

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "production"
}

variable "account_id" {
  description = "AWS account ID"
  type        = string
}

variable "admin_ip" {
  description = "Admin IP address for SSH access (CIDR format)"
  type        = string
  default     = "0.0.0.0/0"  # CHANGE THIS IN PRODUCTION
}

# ============================================
# DATABASE VARIABLES
# ============================================

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "aws_certifications_prod"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "awscoach_prod"
  sensitive   = true
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

# ============================================
# N8N VARIABLES
# ============================================

variable "n8n_instance_type" {
  description = "EC2 instance type for n8n"
  type        = string
  default     = "t3.small"
}

variable "ssh_key_name" {
  description = "SSH key pair name for EC2 instances"
  type        = string
}

variable "n8n_username" {
  description = "n8n basic auth username"
  type        = string
  sensitive   = true
}

variable "n8n_password" {
  description = "n8n basic auth password"
  type        = string
  sensitive   = true
}

