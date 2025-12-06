# Terraform Configuration for AWS Certifications Coach Infrastructure
# This creates all necessary AWS resources for production deployment

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "aws-certifications-coach-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "AWS Certifications Coach"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ============================================
# VPC AND NETWORKING
# ============================================

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "aws-coach-vpc"
  }
}

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "aws-coach-public-a"
  }
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "aws-coach-public-b"
  }
}

resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "${var.aws_region}a"
  
  tags = {
    Name = "aws-coach-private-a"
  }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = "${var.aws_region}b"
  
  tags = {
    Name = "aws-coach-private-b"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "aws-coach-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "aws-coach-public-rt"
  }
}

resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

# ============================================
# SECURITY GROUPS
# ============================================

resource "aws_security_group" "rds" {
  name        = "aws-coach-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
    description     = "PostgreSQL from backend"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "aws-coach-rds-sg"
  }
}

resource "aws_security_group" "backend" {
  name        = "aws-coach-backend-sg"
  description = "Security group for backend API"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "aws-coach-backend-sg"
  }
}

resource "aws_security_group" "n8n" {
  name        = "aws-coach-n8n-sg"
  description = "Security group for n8n instance"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_ip]
    description = "SSH for admin"
  }
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "aws-coach-n8n-sg"
  }
}

# ============================================
# RDS POSTGRESQL
# ============================================

resource "aws_db_subnet_group" "main" {
  name       = "aws-coach-db-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  
  tags = {
    Name = "aws-coach-db-subnet-group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier             = "aws-coach-db"
  engine                 = "postgres"
  engine_version         = "15.4"
  instance_class         = var.db_instance_class
  allocated_storage      = 20
  storage_type           = "gp3"
  storage_encrypted      = true
  
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  
  multi_az               = var.environment == "production" ? true : false
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  skip_final_snapshot = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "aws-coach-db-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null
  
  tags = {
    Name = "aws-coach-postgresql"
  }
}

# ============================================
# S3 BUCKET FOR BACKUPS
# ============================================

resource "aws_s3_bucket" "backups" {
  bucket = "aws-certifications-coach-backups-${var.account_id}"
  
  tags = {
    Name = "aws-coach-backups"
  }
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id
  
  rule {
    id     = "transition-to-ia"
    status = "Enabled"
    
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    
    expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket = aws_s3_bucket.backups.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ============================================
# EC2 INSTANCE FOR N8N
# ============================================

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "n8n" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = var.n8n_instance_type
  
  subnet_id              = aws_subnet.public_a.id
  vpc_security_group_ids = [aws_security_group.n8n.id]
  key_name              = var.ssh_key_name
  
  user_data = <<-EOF
              #!/bin/bash
              # Install Node.js
              curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
              export NVM_DIR="$HOME/.nvm"
              [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
              nvm install 18
              nvm use 18
              
              # Install n8n
              npm install -g n8n
              
              # Create systemd service
              cat > /etc/systemd/system/n8n.service <<SERVICE
              [Unit]
              Description=n8n Workflow Automation
              After=network.target
              
              [Service]
              Type=simple
              User=ec2-user
              Environment="N8N_BASIC_AUTH_ACTIVE=true"
              Environment="N8N_BASIC_AUTH_USER=${var.n8n_username}"
              Environment="N8N_BASIC_AUTH_PASSWORD=${var.n8n_password}"
              Environment="N8N_HOST=0.0.0.0"
              Environment="N8N_PORT=5678"
              ExecStart=/home/ec2-user/.nvm/versions/node/v18.*/bin/n8n
              Restart=always
              
              [Install]
              WantedBy=multi-user.target
              SERVICE
              
              systemctl daemon-reload
              systemctl enable n8n
              systemctl start n8n
              EOF
  
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }
  
  tags = {
    Name = "aws-coach-n8n"
  }
}

resource "aws_eip" "n8n" {
  instance = aws_instance.n8n.id
  domain   = "vpc"
  
  tags = {
    Name = "aws-coach-n8n-eip"
  }
}

# ============================================
# SECRETS MANAGER
# ============================================

resource "aws_secretsmanager_secret" "db_credentials" {
  name        = "${var.environment}/aws-coach/db"
  description = "Database credentials for AWS Certifications Coach"
  
  recovery_window_in_days = 30
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  
  secret_string = jsonencode({
    username = aws_db_instance.postgres.username
    password = var.db_password
    host     = aws_db_instance.postgres.address
    port     = aws_db_instance.postgres.port
    dbname   = aws_db_instance.postgres.db_name
  })
}

# ============================================
# CLOUDWATCH LOG GROUP
# ============================================

resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/certifications-coach"
  retention_in_days = 30
  
  tags = {
    Name = "aws-coach-logs"
  }
}

# ============================================
# OUTPUTS
# ============================================

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.address
}

output "n8n_public_ip" {
  description = "N8N instance public IP"
  value       = aws_eip.n8n.public_ip
}

output "s3_backup_bucket" {
  description = "S3 backup bucket name"
  value       = aws_s3_bucket.backups.id
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

