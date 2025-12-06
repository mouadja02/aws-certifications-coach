# AWS Certifications Coach

A production-ready, AI-powered learning platform to help students prepare for AWS certification exams. **Optimized for AWS Free Tier + Snowflake + Streamlit Cloud** for minimal cost deployment.

## 🎯 Overview

AWS Certifications Coach provides:
- **AI-Powered Chat**: Get instant answers to AWS certification questions via n8n workflows
- **Progress Tracking**: Monitor your learning journey with Snowflake analytics
- **Study Resources**: Access curated videos and materials
- **Practice Tests**: Test your knowledge with realistic exams
- **Multiple Certifications**: Support for all AWS certification paths

## 💰 Cost-Optimized Architecture

**Total Monthly Cost: ~$0** (within free tiers)

```
Streamlit Cloud (Frontend) - FREE
         ↓ HTTPS
AWS Elastic Beanstalk (Backend) - FREE TIER
         ↓
    ┌────┴────┬──────────┐
    ↓         ↓          ↓
Snowflake  AWS EC2    AWS S3
(FREE)   (t2.micro)  (5GB FREE)
         FREE TIER
```

### Free Tier Breakdown

| Service | Free Tier | Usage | Cost |
|---------|-----------|-------|------|
| **Streamlit Cloud** | Unlimited | Frontend hosting | $0 |
| **Snowflake** | $400 credits | Database storage | $0 |
| **AWS EC2** | 750 hrs/month | n8n (t2.micro) | $0 |
| **Elastic Beanstalk** | 750 hrs/month | Backend (t2.micro) | $0 |
| **S3** | 5 GB | Backups | $0 |
| **Data Transfer** | 100 GB/month | API calls | $0 |
| **Total** | | | **$0/month** |

## ✨ Features

### For Students
- ✅ User registration and authentication
- ✅ AI chatbot for AWS questions
- ✅ Progress tracking dashboard
- ✅ Curated study resources
- ✅ Multiple certification paths

### Production Features
- ✅ **Security**: Bcrypt hashing, JWT auth, rate limiting, HTTPS/TLS
- ✅ **Scalability**: Snowflake auto-scales, AWS auto-scaling
- ✅ **Monitoring**: CloudWatch (free tier) + Sentry
- ✅ **Reliability**: Snowflake 99.99% uptime
- ✅ **Cost**: $0/month within free tiers

## 🚀 Quick Start (30 Minutes)

### Prerequisites

1. **Snowflake Account** (Free trial - $400 credits)
   - Sign up at https://signup.snowflake.com
   - Choose AWS as cloud provider
   - Select same region as your AWS deployment

2. **AWS Account** (Free tier)
   - Sign up at https://aws.amazon.com/free
   - Enable Free Tier usage alerts

3. **Streamlit Cloud Account** (Free)
   - Sign up at https://share.streamlit.io

4. **Tools**
   - Terraform installed
   - AWS CLI configured
   - Git installed

### Step 1: Setup Snowflake (5 min)

```sql
-- Login to Snowflake Web UI and run:

-- Create database
CREATE DATABASE AWS_CERTIFICATIONS;
USE DATABASE AWS_CERTIFICATIONS;
USE SCHEMA PUBLIC;

-- Create warehouse (XSmall for free tier)
CREATE WAREHOUSE COMPUTE_WH 
  WAREHOUSE_SIZE = XSMALL 
  AUTO_SUSPEND = 60 
  AUTO_RESUME = TRUE;

-- Create tables (run backend/init_db.sql queries adapted for Snowflake)

-- Get your account identifier
SELECT CURRENT_ACCOUNT();  -- Save this for configuration
```

### Step 2: Deploy AWS Infrastructure (10 min)

```bash
cd aws-infrastructure/terraform

# Configure
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Add your values

# Create SSH key in AWS Console first
# EC2 > Key Pairs > Create Key Pair > Download .pem file

# Deploy (FREE TIER: Only EC2 t2.micro + S3)
terraform init
terraform apply

# Save the n8n URL from output
```

### Step 3: Deploy Backend to Elastic Beanstalk (FREE TIER - 5 min)

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 aws-certifications-coach --region us-east-1

# Create environment (FREE TIER: t2.micro)
eb create aws-coach-prod \
    --instance-type t2.micro \
    --single \
    --envvars \
        SNOWFLAKE_ACCOUNT=abc12345.us-east-1,\
        SNOWFLAKE_USER=your_user,\
        SNOWFLAKE_PASSWORD=your_pass,\
        SNOWFLAKE_WAREHOUSE=COMPUTE_WH,\
        SNOWFLAKE_DATABASE=AWS_CERTIFICATIONS,\
        APP_ENV=production

# Deploy
eb deploy

# Get URL
eb status
```

### Step 4: Configure n8n (3 min)

```bash
# Get n8n IP from Terraform output
N8N_IP=$(terraform output -raw n8n_public_ip)

# Access n8n
open http://${N8N_IP}:5678

# Login with credentials from terraform.tfvars
# Import workflow.json from repository
# Activate all workflows
```

### Step 5: Deploy Frontend to Streamlit Cloud (5 min)

1. **Push to GitHub**
```bash
git add .
git commit -m "Configure for Snowflake + AWS Free Tier"
git push origin main
```

2. **Deploy on Streamlit**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select repository
   - Main file: `frontend/home.py`
   - Python version: 3.11

3. **Add Secrets** (Streamlit Cloud dashboard > Settings > Secrets)
```toml
[general]
BACKEND_URL = "http://your-eb-url.elasticbeanstalk.com"

[connections.snowflake]
account = "abc12345.us-east-1"
user = "your_username"
password = "your_password"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
database = "AWS_CERTIFICATIONS"
schema = "PUBLIC"
```

### Step 6: Verify (2 min)

```bash
# Test backend
curl http://your-eb-url.elasticbeanstalk.com/health

# Test n8n
curl http://${N8N_IP}:5678/healthz

# Test frontend
open https://your-app.streamlit.app
```

## 📁 Project Structure

```
aws-certifications-coach/
├── backend/
│   ├── main.py                 # FastAPI with Snowflake
│   ├── database.py             # Snowflake connector
│   ├── ai_service.py           # n8n integration
│   ├── auth.py                 # Authentication
│   ├── models.py               # Data models
│   └── requirements.txt        # Dependencies
├── frontend/
│   ├── home.py                 # Streamlit app
│   ├── dashboard.py            # Dashboard
│   ├── utils.py                # Helpers
│   ├── requirements.txt        # Dependencies
│   └── .streamlit/
│       ├── config.toml
│       └── secrets.toml.example
├── aws-infrastructure/
│   └── terraform/
│       ├── main.tf             # AWS Free Tier resources
│       ├── variables.tf
│       └── terraform.tfvars.example
├── scripts/
│   ├── backup_database.sh
│   └── restore_database.sh
└── workflow.json               # n8n workflows
```

## 🔒 Security

- **Authentication**: Bcrypt password hashing + JWT tokens
- **Encryption**: TLS in transit, Snowflake encryption at rest
- **Secrets**: AWS Secrets Manager + Streamlit Secrets
- **Network**: AWS Security Groups, Snowflake IP whitelist
- **Rate Limiting**: 60 requests/minute per IP

## 📊 Snowflake Setup Details

### Database Schema

```sql
-- Users table
CREATE TABLE logged_users (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    age INTEGER,
    target_certification VARCHAR(255) NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    last_login TIMESTAMP_NTZ
);

-- Chat history
CREATE TABLE chat_history (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- User progress
CREATE TABLE user_progress (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    study_time_minutes INTEGER DEFAULT 0,
    practice_tests_taken INTEGER DEFAULT 0,
    average_score INTEGER DEFAULT 0,
    progress_percentage INTEGER DEFAULT 0,
    last_activity TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

### Snowflake Cost Optimization

```sql
-- Auto-suspend after 5 minutes of inactivity
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 300;

-- Auto-resume when queries arrive
ALTER WAREHOUSE COMPUTE_WH SET AUTO_RESUME = TRUE;

-- Use XSmall warehouse (cheapest, still powerful)
ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = XSMALL;

-- Monitor credit usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
ORDER BY START_TIME DESC
LIMIT 10;
```

## 🛠️ AWS Free Tier Resources

### What's Deployed

| Resource | Type | Free Tier | Monthly Limit |
|----------|------|-----------|---------------|
| EC2 (n8n) | t2.micro | ✅ Yes | 750 hours |
| Elastic Beanstalk | t2.micro | ✅ Yes | 750 hours |
| S3 Storage | Standard | ✅ Yes | 5 GB |
| Data Transfer | Outbound | ✅ Yes | 100 GB |
| CloudWatch | Logs/Metrics | ✅ Yes | 10 metrics |
| Secrets Manager | 2 secrets | ✅ Yes | 30 days trial |

### Free Tier Limits

```bash
# Monitor your usage
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics BlendedCost

# Set billing alert
aws budgets create-budget \
    --account-id 123456789012 \
    --budget file://budget.json
```

## 📈 Monitoring

### CloudWatch (Free Tier)
- 10 custom metrics
- 10 alarms
- 1GB log ingestion
- 5GB log storage

### Snowflake Monitoring
```sql
-- Query performance
SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
ORDER BY START_TIME DESC
LIMIT 100;

-- Storage usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.DATABASE_STORAGE_USAGE_HISTORY
ORDER BY USAGE_DATE DESC;
```

## 🔧 Development

### Local Setup with Snowflake

```bash
# Backend
cd backend
pip install -r requirements.txt

# Create .env with Snowflake credentials
cp .env.example .env
nano .env

# Test connection
python database.py

# Run backend
python main.py

# Frontend
cd frontend
pip install -r requirements.txt
streamlit run home.py
```

### Testing Snowflake Connection

```python
import snowflake.connector

conn = snowflake.connector.connect(
    account='abc12345.us-east-1',
    user='your_user',
    password='your_password',
    warehouse='COMPUTE_WH',
    database='AWS_CERTIFICATIONS',
    schema='PUBLIC'
)

cursor = conn.cursor()
cursor.execute("SELECT CURRENT_VERSION()")
print(cursor.fetchone())
```

## 🔄 Backup & Recovery

### Snowflake Time Travel (Free - 1 day)

```sql
-- Restore table to 1 hour ago
CREATE OR REPLACE TABLE logged_users 
AS SELECT * FROM logged_users 
AT(OFFSET => -3600);

-- View historical data
SELECT * FROM chat_history 
AT(TIMESTAMP => '2024-01-15 10:00:00'::TIMESTAMP_NTZ);
```

### S3 Backups (Free - 5GB)

```bash
# Manual backup
./scripts/backup_database.sh

# Automated via CloudWatch Events (FREE)
```

## 🆘 Troubleshooting

### Snowflake Connection Issues

```python
# Check credentials
import snowflake.connector
from snowflake.connector import OperationalError

try:
    conn = snowflake.connector.connect(...)
    print("✅ Connected!")
except OperationalError as e:
    print(f"❌ Error: {e}")
```

### AWS Free Tier Exceeded

```bash
# Check your usage
aws ce get-cost-forecast \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --metric UNBLENDED_COST \
    --granularity MONTHLY
```

## 💡 Tips for Staying in Free Tier

1. **EC2**: Use t2.micro only (750 hours/month free)
2. **RDS**: Not used - Snowflake instead (free trial)
3. **S3**: Keep under 5GB, use lifecycle policies
4. **Data Transfer**: Keep under 100GB/month
5. **Elastic Beanstalk**: Use single instance mode
6. **Stop Resources**: Stop EC2 when not using

## 📚 Documentation

- **Snowflake Docs**: https://docs.snowflake.com
- **AWS Free Tier**: https://aws.amazon.com/free
- **Streamlit Docs**: https://docs.streamlit.io
- **n8n Docs**: https://docs.n8n.io

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- Snowflake for seamless Streamlit integration
- AWS Free Tier for infrastructure
- Streamlit Cloud for free hosting
- n8n for workflow automation

---

**Version**: 2.1.0  
**Status**: ✅ Production Ready (Snowflake + AWS Free Tier)  
**Monthly Cost**: $0 (within free tiers)

**Made with ❤️ for AWS certification learners worldwide**
