# Terraform Variables for AWS Certifications Coach
# Optimized for AWS Free Tier

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"  # Free tier available in all regions
}

variable "environment" {
  description = "Environment name"
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
  default     = "0.0.0.0/0"  # CHANGE THIS to your IP for security
}

# ============================================
# N8N VARIABLES
# ============================================

variable "ssh_key_name" {
  description = "SSH key pair name for EC2 instances"
  type        = string
}

variable "n8n_username" {
  description = "n8n basic auth username"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "n8n_password" {
  description = "n8n basic auth password"
  type        = string
  sensitive   = true
}
