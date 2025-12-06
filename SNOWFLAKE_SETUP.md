# Snowflake Setup Guide

## 🎯 Quick Setup (10 Minutes)

### Step 1: Create Snowflake Account (2 min)

1. Go to https://signup.snowflake.com
2. Choose **Standard Edition** (Free $400 credits)
3. Select **AWS** as cloud provider
4. Choose same region as your AWS deployment (e.g., us-east-1)
5. Complete registration

### Step 2: Initial Configuration (3 min)

Login to Snowflake Web UI (https://app.snowflake.com)

```sql
-- Create database
CREATE DATABASE AWS_CERTIFICATIONS;

-- Use the database
USE DATABASE AWS_CERTIFICATIONS;
USE SCHEMA PUBLIC;

-- Create warehouse (XSmall - cheapest option)
CREATE WAREHOUSE COMPUTE_WH 
WITH 
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 300        -- 5 minutes
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

-- Use the warehouse
USE WAREHOUSE COMPUTE_WH;
```

### Step 3: Create Tables (3 min)

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

-- Chat history table
CREATE TABLE chat_history (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- User progress table
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

-- Activity log table
CREATE TABLE activity_log (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Verify tables
SHOW TABLES;
```

### Step 4: Get Connection Details (2 min)

```sql
-- Get your account identifier
SELECT CURRENT_ACCOUNT();
-- Result example: ABC12345

-- Get your region
SELECT CURRENT_REGION();
-- Result example: AWS_US_EAST_1

-- Your full account identifier will be:
-- abc12345.us-east-1
```

Save these values for configuration!

## 🔐 Security Setup

### Create Application User

```sql
-- Create role for application
CREATE ROLE AWS_COACH_ROLE;

-- Grant permissions
GRANT USAGE ON DATABASE AWS_CERTIFICATIONS TO ROLE AWS_COACH_ROLE;
GRANT USAGE ON SCHEMA AWS_CERTIFICATIONS.PUBLIC TO ROLE AWS_COACH_ROLE;
GRANT ALL ON ALL TABLES IN SCHEMA AWS_CERTIFICATIONS.PUBLIC TO ROLE AWS_COACH_ROLE;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE AWS_COACH_ROLE;

-- Create user for application
CREATE USER aws_coach_app
    PASSWORD = 'STRONG_PASSWORD_HERE'
    DEFAULT_ROLE = AWS_COACH_ROLE
    DEFAULT_WAREHOUSE = COMPUTE_WH
    DEFAULT_NAMESPACE = AWS_CERTIFICATIONS.PUBLIC
    MUST_CHANGE_PASSWORD = FALSE;

-- Grant role to user
GRANT ROLE AWS_COACH_ROLE TO USER aws_coach_app;
```

## 💰 Cost Optimization

### Auto-Suspend Configuration

```sql
-- Suspend warehouse after 5 minutes of inactivity
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 300;

-- Auto-resume when queries arrive
ALTER WAREHOUSE COMPUTE_WH SET AUTO_RESUME = TRUE;

-- Keep warehouse size at XSmall
ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = XSMALL;
```

### Resource Monitoring

```sql
-- Check credit usage (last 7 days)
SELECT 
    DATE_TRUNC('day', START_TIME) as DAY,
    WAREHOUSE_NAME,
    SUM(CREDITS_USED) as CREDITS_USED
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
GROUP BY 1, 2
ORDER BY 1 DESC, 3 DESC;

-- Check storage usage
SELECT 
    DATABASE_NAME,
    SUM(AVERAGE_DATABASE_BYTES) / POWER(1024, 3) as STORAGE_GB
FROM SNOWFLAKE.ACCOUNT_USAGE.DATABASE_STORAGE_USAGE_HISTORY
WHERE USAGE_DATE >= DATEADD(day, -7, CURRENT_DATE())
GROUP BY 1
ORDER BY 2 DESC;

-- Query performance
SELECT 
    QUERY_TEXT,
    TOTAL_ELAPSED_TIME/1000 as DURATION_SECONDS,
    EXECUTION_STATUS,
    START_TIME
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE START_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
ORDER BY TOTAL_ELAPSED_TIME DESC
LIMIT 10;
```

## 🔗 Connection Testing

### Python Test

```python
import snowflake.connector

# Test connection
try:
    conn = snowflake.connector.connect(
        account='abc12345.us-east-1',
        user='aws_coach_app',
        password='your_password',
        warehouse='COMPUTE_WH',
        database='AWS_CERTIFICATIONS',
        schema='PUBLIC'
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_VERSION()")
    version = cursor.fetchone()
    print(f"✅ Connected to Snowflake version: {version[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM logged_users")
    count = cursor.fetchone()
    print(f"✅ Users table accessible. Count: {count[0]}")
    
    conn.close()
    print("✅ Connection test successful!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Streamlit Test

```python
import streamlit as st

# Use Streamlit's native Snowflake connection
conn = st.connection("snowflake")

# Query data
df = conn.query("SELECT * FROM logged_users LIMIT 5")
st.dataframe(df)
```

## 📊 Useful Queries

### User Analytics

```sql
-- Active users by certification
SELECT 
    target_certification,
    COUNT(*) as user_count
FROM logged_users
WHERE is_active = 1
GROUP BY target_certification
ORDER BY user_count DESC;

-- Recent activity
SELECT 
    u.name,
    u.email,
    COUNT(c.id) as chat_messages,
    MAX(c.created_at) as last_chat
FROM logged_users u
LEFT JOIN chat_history c ON u.id = c.user_id
GROUP BY u.id, u.name, u.email
ORDER BY last_chat DESC;

-- User progress summary
SELECT 
    u.name,
    u.target_certification,
    p.study_time_minutes / 60.0 as study_hours,
    p.practice_tests_taken,
    p.average_score,
    p.progress_percentage
FROM logged_users u
JOIN user_progress p ON u.id = p.user_id
ORDER BY p.progress_percentage DESC;
```

## 🛠️ Troubleshooting

### Common Issues

**1. Connection timeout**
```sql
-- Check if warehouse is running
SHOW WAREHOUSES LIKE 'COMPUTE_WH';

-- Resume warehouse
ALTER WAREHOUSE COMPUTE_WH RESUME;
```

**2. Permission denied**
```sql
-- Check user roles
SHOW GRANTS TO USER aws_coach_app;

-- Re-grant permissions if needed
GRANT ALL ON ALL TABLES IN SCHEMA AWS_CERTIFICATIONS.PUBLIC 
TO ROLE AWS_COACH_ROLE;
```

**3. Account identifier issues**
```sql
-- Verify account identifier format
SELECT 
    CURRENT_ACCOUNT() as ACCOUNT,
    CURRENT_REGION() as REGION;

-- Should be: account.region (e.g., abc12345.us-east-1)
```

## 📈 Monitoring Dashboard

```sql
-- Create monitoring view
CREATE OR REPLACE VIEW monitoring_dashboard AS
SELECT 
    -- Credit usage
    (SELECT SUM(CREDITS_USED) 
     FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
     WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP())) as CREDITS_LAST_30_DAYS,
    
    -- Storage
    (SELECT SUM(AVERAGE_DATABASE_BYTES) / POWER(1024, 3)
     FROM SNOWFLAKE.ACCOUNT_USAGE.DATABASE_STORAGE_USAGE_HISTORY
     WHERE USAGE_DATE >= DATEADD(day, -1, CURRENT_DATE())) as STORAGE_GB,
    
    -- Active users
    (SELECT COUNT(*) FROM logged_users WHERE is_active = 1) as ACTIVE_USERS,
    
    -- Total chats
    (SELECT COUNT(*) FROM chat_history) as TOTAL_CHATS;

-- Query dashboard
SELECT * FROM monitoring_dashboard;
```

## 🔄 Backup & Recovery

### Time Travel (Free - 1 day retention)

```sql
-- View data from 1 hour ago
SELECT * FROM logged_users 
AT(OFFSET => -3600);  -- seconds

-- Restore table to previous state
CREATE OR REPLACE TABLE logged_users 
AS SELECT * FROM logged_users 
AT(TIMESTAMP => '2024-01-15 10:00:00'::TIMESTAMP_NTZ);

-- Undrop table (if accidentally dropped)
UNDROP TABLE logged_users;
```

### Data Export

```sql
-- Export to S3 (requires setup)
COPY INTO @my_s3_stage/backup/logged_users_
FROM logged_users
FILE_FORMAT = (TYPE = 'CSV' COMPRESSION = 'GZIP');
```

## 🎓 Best Practices

1. **Always use AUTO_SUSPEND** - Saves credits
2. **Use XSmall warehouse** - Sufficient for most workloads
3. **Monitor credit usage** - Set up alerts
4. **Use Time Travel** - Instead of manual backups
5. **Leverage clustering** - For large tables
6. **Use Streamlit integration** - Native caching

## 📞 Support

- **Snowflake Docs**: https://docs.snowflake.com
- **Community**: https://community.snowflake.com
- **Support**: support@snowflake.com

---

**Setup Time**: ~10 minutes  
**Monthly Cost**: $0 (Free $400 credits)  
**Retention**: 1 day Time Travel (free tier)

