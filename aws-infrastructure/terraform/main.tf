# Terraform Configuration for AWS Certifications Coach
# Optimized for AWS FREE TIER - Minimal resources

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "AWS Certifications Coach"
      Environment = var.environment
      ManagedBy   = "Terraform"
      FreeTier    = "true"
    }
  }
}

# ============================================
# VPC (Default VPC - Free Tier)
# ============================================

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ============================================
# SECURITY GROUPS
# ============================================

resource "aws_security_group" "n8n" {
  name        = "aws-coach-n8n-sg"
  description = "Security group for n8n instance"
  vpc_id      = data.aws_vpc.default.id
  
  # SSH access (restrict to your IP in production)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_ip]
    description = "SSH for admin"
  }
  
  # HTTP for Let's Encrypt
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }
  
  # HTTPS for n8n
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }
  
  # n8n direct access (can be removed after SSL setup)
  ingress {
    from_port   = 5678
    to_port     = 5678
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "n8n HTTP (temporary)"
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
# EC2 INSTANCE FOR N8N (FREE TIER ELIGIBLE)
# ============================================

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "n8n" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = "t2.micro"  # FREE TIER: 750 hours/month free for 12 months
  
  subnet_id              = tolist(data.aws_subnets.default.ids)[0]
  vpc_security_group_ids = [aws_security_group.n8n.id]
  key_name              = var.ssh_key_name
  
  user_data = <<-EOF
              #!/bin/bash
              set -e
              
              # Update system
              yum update -y
              
              # Install Node.js via NVM
              curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
              export NVM_DIR="$HOME/.nvm"
              [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
              
              # Install Node.js 18
              nvm install 18
              nvm use 18
              nvm alias default 18
              
              # Install n8n globally
              npm install -g n8n
              
              # Create n8n data directory
              mkdir -p /home/ec2-user/.n8n
              chown -R ec2-user:ec2-user /home/ec2-user/.n8n
              
              # Create systemd service for n8n
              cat > /etc/systemd/system/n8n.service <<SERVICE
              [Unit]
              Description=n8n Workflow Automation
              After=network.target
              
              [Service]
              Type=simple
              User=ec2-user
              Environment="HOME=/home/ec2-user"
              Environment="N8N_BASIC_AUTH_ACTIVE=true"
              Environment="N8N_BASIC_AUTH_USER=${var.n8n_username}"
              Environment="N8N_BASIC_AUTH_PASSWORD=${var.n8n_password}"
              Environment="N8N_HOST=0.0.0.0"
              Environment="N8N_PORT=5678"
              Environment="N8N_PROTOCOL=http"
              Environment="GENERIC_TIMEZONE=UTC"
              ExecStart=/home/ec2-user/.nvm/versions/node/v18.*/bin/n8n
              WorkingDirectory=/home/ec2-user
              Restart=always
              RestartSec=10
              
              [Install]
              WantedBy=multi-user.target
              SERVICE
              
              # Start n8n service
              systemctl daemon-reload
              systemctl enable n8n
              systemctl start n8n
              
              # Wait for n8n to start
              sleep 10
              
              echo "n8n installation complete!"
              EOF
  
  root_block_device {
    volume_size = 8  # FREE TIER: 30 GB EBS storage free
    volume_type = "gp2"
    encrypted   = true
  }
  
  # FREE TIER: No additional EBS volumes
  
  tags = {
    Name = "aws-coach-n8n"
  }
}

# Elastic IP for n8n (FREE TIER: 1 EIP free when attached)
resource "aws_eip" "n8n" {
  instance = aws_instance.n8n.id
  domain   = "vpc"
  
  tags = {
    Name = "aws-coach-n8n-eip"
  }
}

# ============================================
# S3 BUCKET FOR BACKUPS (FREE TIER: 5GB)
# ============================================

resource "aws_s3_bucket" "backups" {
  bucket = "aws-coach-backups-${var.account_id}"
  
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
    id     = "delete-old-backups"
    status = "Enabled"
    
    expiration {
      days = 30  # Keep backups for 30 days only
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
# SECRETS MANAGER (Minimal usage)
# ============================================

resource "aws_secretsmanager_secret" "n8n_credentials" {
  name        = "${var.environment}/aws-coach/n8n"
  description = "n8n credentials"
  
  recovery_window_in_days = 7  # Minimum recovery window
  
  tags = {
    Name = "aws-coach-n8n-credentials"
  }
}

resource "aws_secretsmanager_secret_version" "n8n_credentials" {
  secret_id = aws_secretsmanager_secret.n8n_credentials.id
  
  secret_string = jsonencode({
    username = var.n8n_username
    password = var.n8n_password
    url      = "https://${aws_eip.n8n.public_ip}:5678"
  })
}

# ============================================
# OUTPUTS
# ============================================

output "n8n_public_ip" {
  description = "N8N instance public IP"
  value       = aws_eip.n8n.public_ip
}

output "n8n_url" {
  description = "N8N access URL"
  value       = "http://${aws_eip.n8n.public_ip}:5678"
}

output "s3_backup_bucket" {
  description = "S3 backup bucket name"
  value       = aws_s3_bucket.backups.id
}

output "deployment_info" {
  description = "Deployment information"
  value = <<-EOT
  
  ✅ AWS Free Tier Deployment Complete!
  
  n8n URL: http://${aws_eip.n8n.public_ip}:5678
  n8n Username: ${var.n8n_username}
  n8n Password: ${var.n8n_password}
  
  S3 Backup Bucket: ${aws_s3_bucket.backups.id}
  
  SSH Command: ssh -i ${var.ssh_key_name}.pem ec2-user@${aws_eip.n8n.public_ip}
  
  Next Steps:
  1. Access n8n at the URL above
  2. Import workflow.json
  3. Configure Snowflake connection in backend
  4. Deploy backend to AWS Elastic Beanstalk (Free Tier: 750 hours/month)
  5. Deploy frontend to Streamlit Cloud (Free)
  
  💰 Estimated Monthly Cost: $0 (within Free Tier limits)
  EOT
}
