# Quick Start with Snowflake

## Issue Resolved
The error you're seeing is because the frontend is trying to connect to a backend API at `localhost:8000`, but no backend is running.

**Solution**: We've updated the frontend to connect **directly to Snowflake** (no backend API needed for authentication). This is the recommended approach for Streamlit + Snowflake.

## Setup Steps (5 Minutes)

### 1. Configure Snowflake Secrets

Edit `frontend/.streamlit/secrets.toml`:

```toml
[connections.snowflake]
account = "YOUR_ACCOUNT.us-east-1"  # Get from Snowflake
user = "your_username"
password = "your_password"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
database = "AWS_CERTIFICATIONS"
schema = "PUBLIC"
client_session_keep_alive = true
```

**How to get your Snowflake account identifier:**
1. Login to Snowflake: https://app.snowflake.com
2. Look at URL: `https://app.snowflake.com/ABC12345/...`
3. Your account is: `abc12345.us-east-1` (lowercase + region)

OR run in Snowflake:
```sql
SELECT CURRENT_ACCOUNT(), CURRENT_REGION();
-- Result: ABC12345, AWS_US_EAST_1
-- Format as: abc12345.us-east-1
```

### 2. Create Snowflake Tables

Login to Snowflake Web UI and run:

```sql
-- Use your database
USE DATABASE AWS_CERTIFICATIONS;
USE SCHEMA PUBLIC;
USE WAREHOUSE COMPUTE_WH;

-- Create users table
CREATE TABLE IF NOT EXISTS logged_users (
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

-- Create chat history table
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Create user progress table
CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    study_time_minutes INTEGER DEFAULT 0,
    practice_tests_taken INTEGER DEFAULT 0,
    average_score INTEGER DEFAULT 0,
    progress_percentage INTEGER DEFAULT 0,
    last_activity TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Verify tables
SHOW TABLES;

-- Check if tables are empty
SELECT 'logged_users' as table_name, COUNT(*) as count FROM logged_users
UNION ALL
SELECT 'chat_history', COUNT(*) FROM chat_history
UNION ALL
SELECT 'user_progress', COUNT(*) FROM user_progress;
```

### 3. Install Dependencies

```bash
cd frontend
pip install -r requirements.txt
```

### 4. Run Streamlit

```bash
streamlit run home.py
```

### 5. Test Connection

The app should now:
- ✅ Connect directly to Snowflake
- ✅ No backend API needed
- ✅ Register/Login works directly with Snowflake

## What Changed

**Before:**
```
Frontend → Backend API (port 8000) → PostgreSQL
```

**After:**
```
Frontend → Snowflake (direct connection)
```

**Benefits:**
- ✅ No backend server needed for auth
- ✅ Native Streamlit-Snowflake integration
- ✅ Better caching and performance
- ✅ Simpler architecture
- ✅ Lower latency

## Checking Data in Snowflake

### View Users
```sql
SELECT * FROM logged_users ORDER BY created_at DESC;
```

### View Chat History
```sql
SELECT 
    u.name,
    u.email,
    c.question,
    c.answer,
    c.created_at
FROM chat_history c
JOIN logged_users u ON c.user_id = u.id
ORDER BY c.created_at DESC
LIMIT 10;
```

### View User Progress
```sql
SELECT 
    u.name,
    u.email,
    u.target_certification,
    p.study_time_minutes / 60.0 as study_hours,
    p.practice_tests_taken,
    p.average_score,
    p.progress_percentage
FROM user_progress p
JOIN logged_users u ON p.user_id = u.id
ORDER BY p.progress_percentage DESC;
```

## Troubleshooting

### Error: "Failed to connect to Snowflake"

Check `frontend/.streamlit/secrets.toml`:
1. Account identifier format: `account123.us-east-1` (lowercase)
2. Username and password are correct
3. Database and warehouse exist
4. User has permissions

Test connection in Snowflake UI first:
```sql
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE();
```

### Error: "Table not found"

Run the table creation SQL above in Snowflake Web UI.

### Error: "Insufficient privileges"

Grant permissions:
```sql
GRANT ALL ON DATABASE AWS_CERTIFICATIONS TO ROLE ACCOUNTADMIN;
GRANT ALL ON SCHEMA AWS_CERTIFICATIONS.PUBLIC TO ROLE ACCOUNTADMIN;
GRANT ALL ON ALL TABLES IN SCHEMA AWS_CERTIFICATIONS.PUBLIC TO ROLE ACCOUNTADMIN;
```

## Optional: Backend API (for n8n AI features)

If you want AI chatbot features via n8n, you still need the backend API:

```bash
# Terminal 1: Start backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2: Start frontend
cd frontend
streamlit run home.py
```

But for authentication and database operations, the frontend now connects directly to Snowflake!

---

**You're all set! The app now works with Snowflake directly** 🎉

