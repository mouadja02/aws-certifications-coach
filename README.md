# AWS Certifications Coach

A production-ready, AI-powered learning platform to help students prepare for AWS certification exams. Designed for deployment on AWS with Streamlit Cloud, featuring enterprise-grade security, auto-scaling, and comprehensive monitoring.

## 🎯 Overview

AWS Certifications Coach provides:
- **AI-Powered Chat**: Get instant answers to AWS certification questions
- **Progress Tracking**: Monitor your learning journey
- **Study Resources**: Access curated videos and materials
- **Practice Tests**: Test your knowledge with realistic exams
- **Multiple Certifications**: Support for all AWS certification paths

## 🏗️ Architecture

```
Streamlit Cloud (Frontend - Global CDN)
         ↓ HTTPS/TLS 1.3
AWS Elastic Beanstalk (Backend API - Auto-scaled)
         ↓
    ┌────┴────┬──────────┬──────────┐
    ↓         ↓          ↓          ↓
AWS RDS   AWS EC2    AWS S3   AWS Secrets
(PostgreSQL) (n8n)  (Backups) Manager
Multi-AZ   Workflows Encrypted Rotated
```

## ✨ Features

### For Students
- ✅ User registration and authentication
- ✅ AI chatbot for AWS questions
- ✅ Progress tracking dashboard
- ✅ Curated study resources
- ✅ Multiple certification paths

### Production Features
- ✅ **Security**: Bcrypt hashing, JWT auth, rate limiting, HTTPS/TLS 1.3
- ✅ **Scalability**: Auto-scaling 2-4 instances, load balancing
- ✅ **Monitoring**: CloudWatch logs/alarms, Sentry error tracking
- ✅ **Reliability**: Multi-AZ database, automated backups
- ✅ **Compliance**: GDPR ready, audit logging

## 🚀 Quick Start

### Prerequisites

- AWS account with billing configured
- Domain name (optional but recommended)
- Terraform installed (v1.0+)
- AWS CLI installed and configured
- Streamlit Cloud account (free)

### 1. Clone Repository

```bash
git clone https://github.com/your-username/aws-certifications-coach.git
cd aws-certifications-coach
```

### 2. Deploy AWS Infrastructure

```bash
cd aws-infrastructure/terraform

# Configure variables
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Edit with your values

# Deploy
terraform init
terraform apply
```

### 3. Configure Secrets

```bash
# Generate secrets
openssl rand -hex 32  # For JWT

# Store in AWS Secrets Manager
aws secretsmanager create-secret \
    --name prod/aws-coach/db \
    --secret-string '{"username":"awscoach_prod","password":"YOUR_PASSWORD","host":"YOUR_RDS_ENDPOINT","port":"5432","dbname":"aws_certifications_prod"}'
```

### 4. Deploy Backend

```bash
# Initialize Elastic Beanstalk
eb init -p python-3.11 aws-certifications-coach --region us-east-1

# Create environment
eb create aws-coach-prod --instance-type t3.small --min-instances 2

# Deploy
eb deploy
```

### 5. Deploy Frontend (Streamlit Cloud)

1. Push code to GitHub
2. Go to https://share.streamlit.app
3. Connect repository
4. Set main file: `frontend/home.py`
5. Add secrets in Streamlit Cloud settings

## 📁 Project Structure

```
aws-certifications-coach/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database operations
│   ├── ai_service.py           # AI integration
│   ├── auth.py                 # Authentication
│   ├── models.py               # Data models
│   ├── requirements.txt        # Dependencies
│   └── init_db.sql            # Database schema
├── frontend/
│   ├── home.py                 # Main Streamlit app
│   ├── dashboard.py            # User dashboard
│   ├── utils.py                # Helper functions
│   ├── requirements.txt        # Dependencies
│   ├── .streamlit/
│   │   ├── config.toml         # Streamlit config
│   │   └── secrets.toml.example # Secrets template
│   └── images/
│       └── logo.png
├── aws-infrastructure/
│   └── terraform/
│       ├── main.tf             # Infrastructure as Code
│       ├── variables.tf        # Terraform variables
│       └── terraform.tfvars.example
├── scripts/
│   ├── backup_database.sh      # Backup script
│   └── restore_database.sh     # Restore script
├── .env.example                # Environment template
├── .gitignore
└── workflow.json               # n8n workflows
```

## 🔒 Security

- **Authentication**: Bcrypt password hashing + JWT tokens
- **Encryption**: TLS 1.3 in transit, AES-256 at rest
- **Secrets**: AWS Secrets Manager with rotation
- **Network**: VPC with security groups
- **Rate Limiting**: 60 requests/minute per IP
- **Headers**: HSTS, CSP, X-Frame-Options, etc.
- **Compliance**: GDPR ready with data export/deletion APIs

## 📊 Monitoring

- **CloudWatch**: Logs, metrics, and alarms
- **Sentry**: Real-time error tracking
- **Health Checks**: Automated endpoint monitoring
- **Alarms**: CPU, memory, errors, failed logins

## 💰 Cost Estimate

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| RDS | db.t3.micro Multi-AZ | $30 |
| EC2 | t3.small (n8n) | $15 |
| Elastic Beanstalk | 2x t3.small | $30 |
| Other | S3, CloudWatch, etc | $17 |
| **Total** | | **~$92/month** |

**With Reserved Instances**: ~$55/month (40% savings)

## 📚 Documentation

- [Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [Security Best Practices](SECURITY_BEST_PRACTICES.md) - Comprehensive security guide
- [Final Deployment Checklist](FINAL_DEPLOYMENT_CHECKLIST.md) - Pre-launch verification
- [Quick Deployment Reference](QUICK_DEPLOYMENT_REFERENCE.md) - 30-minute quick start
- [Migration Summary](MIGRATION_SUMMARY.md) - Docker to cloud migration details

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit 1.29.0 |
| Backend | FastAPI 0.108.0 |
| Database | PostgreSQL 15 (AWS RDS) |
| AI/Workflows | n8n (self-hosted) |
| Infrastructure | AWS (Terraform) |
| Hosting | Streamlit Cloud + Elastic Beanstalk |
| Monitoring | CloudWatch + Sentry |

## 🔧 Development

### Local Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
pip install -r requirements.txt
streamlit run home.py
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=aws_certifications_prod
DB_USER=awscoach_prod
DB_PASSWORD=your-password

# Security
JWT_SECRET_KEY=your-jwt-secret
SECRET_KEY=your-secret-key

# n8n Webhooks
N8N_CHAT_WEBHOOK_URL=https://your-n8n/webhook/chat
```

## 🧪 Testing

```bash
# Security scanning
safety check -r backend/requirements.txt
bandit -r backend/

# Load testing
ab -n 1000 -c 50 https://your-api-url/health
```

## 🔄 Backup & Recovery

### Automated Backups
- RDS: Daily automated backups (7-day retention)
- S3: Manual backups via script

### Manual Backup
```bash
./scripts/backup_database.sh
```

### Restore
```bash
./scripts/restore_database.sh backup-file.sql.gz
```

## 🆘 Troubleshooting

### Backend Issues
```bash
eb logs              # View logs
eb ssh               # SSH into instance
eb restart           # Restart application
```

### Database Issues
```bash
# Test connection
psql -h YOUR_RDS_ENDPOINT -U awscoach_prod -d aws_certifications_prod

# Check status
aws rds describe-db-instances --db-instance-identifier aws-coach-db
```

### Frontend Issues
- Check Streamlit Cloud logs in dashboard
- Verify secrets are configured correctly
- Test backend API connectivity

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- AWS for cloud infrastructure
- Streamlit for frontend hosting
- n8n for workflow automation
- OpenAI/Anthropic for AI capabilities
- Open source community

## 📞 Support

- **Documentation**: See documentation files
- **Issues**: GitHub Issues
- **Email**: support@your-domain.com

---

**Version**: 2.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: December 2025

**Made with ❤️ for AWS certification learners worldwide**

