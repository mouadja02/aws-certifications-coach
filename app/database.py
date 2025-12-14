"""
Database connection and operations for AWS Certifications Coach
Uses Snowflake for data storage (integrates seamlessly with Streamlit Cloud)
"""

import os
import streamlit as st
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# SNOWFLAKE CONNECTION (Streamlit Native)
# ============================================

@st.cache_resource
def get_snowflake_connection():
    """
    Get Snowflake connection using Streamlit's native connection
    This is cached for performance
    """
    try:
        return st.connection("snowflake")
    except Exception as e:
        logger.error(f"Failed to connect to Snowflake: {e}")
        return None

def execute_query(query, params=None):
    """Execute a Snowflake query and return results"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return None
        
        if params:
            return conn.query(query, params=params, ttl=0)
        else:
            return conn.query(query, ttl=0)
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        return None

def execute_update(query, params=None):
    """Execute a Snowflake update/insert query"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return False
        
        session = conn.session()
        if params:
            result = session.sql(query).collect()
        else:
            # Use parameterized query
            cursor = session.connection.cursor()
            cursor.execute(query, params if params else ())
            session.connection.commit()
            cursor.close()
        return True
    except Exception as e:
        logger.error(f"Update execution error: {e}")
        return False

# ============================================
# USER OPERATIONS
# ============================================

def check_if_user_exists(email: str) -> bool:
    """Check if a user exists in Snowflake"""
    try:
        query = """
        SELECT id FROM logged_users 
        WHERE email = %s
        """
        conn = get_snowflake_connection()
        if conn is None:
            return False
        
        session = conn.session()
        result = session.sql(f"SELECT id FROM logged_users WHERE email = '{email}'").collect()
        return len(result) > 0
    except Exception as e:
        logger.error(f"Error checking if user exists: {e}")
        return False

def insert_user(name: str, email: str, password: str, target_certification: str, age: int = None):
    """Insert a new user into Snowflake"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return False
        
        session = conn.session()
        
        # Insert user
        query = f"""
        INSERT INTO logged_users 
        (name, email, password, target_certification, age, is_active, created_at, updated_at)
        VALUES ('{name}', '{email}', '{password}', '{target_certification}', {age if age else 'NULL'}, 1, 
                CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        """
        
        session.sql(query).collect()
        
        # Get user ID and create progress
        user = get_user_by_email(email)
        if user:
            create_user_progress(user['ID'])
        
        logger.info(f"User created successfully: {email}")
        return True
    except Exception as e:
        logger.error(f"Error inserting user: {e}")
        return False

def get_user_by_email(email: str):
    """Retrieve a user by email from Snowflake"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return None
        
        session = conn.session()
        query = f"""
        SELECT id, name, email, password, age, target_certification, 
               created_at, updated_at
        FROM logged_users 
        WHERE email = '{email}' AND is_active = 1
        """
        
        result = session.sql(query).collect()
        
        if result and len(result) > 0:
            row = result[0]
            return {
                'ID': row['ID'],
                'NAME': row['NAME'],
                'EMAIL': row['EMAIL'],
                'PASSWORD': row['PASSWORD'],
                'AGE': row['AGE'],
                'TARGET_CERTIFICATION': row['TARGET_CERTIFICATION'],
                'CREATED_AT': row['CREATED_AT'],
                'UPDATED_AT': row['UPDATED_AT']
            }
        return None
    except Exception as e:
        logger.error(f"Error retrieving user: {e}")
        return None

def update_last_login(email: str):
    """Update user's last login timestamp"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return False
        
        session = conn.session()
        query = f"""
        UPDATE logged_users 
        SET last_login = CURRENT_TIMESTAMP() 
        WHERE email = '{email}'
        """
        
        session.sql(query).collect()
        return True
    except Exception as e:
        logger.error(f"Error updating last login: {e}")
        return False

# ============================================
# USER PROGRESS OPERATIONS
# ============================================

def create_user_progress(user_id: int):
    """Create initial progress entry for a user"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return False
        
        session = conn.session()
        query = f"""
        INSERT INTO user_progress 
        (user_id)
        VALUES ({user_id})
        """
        
        session.sql(query).collect()
        logger.debug(f"User progress created for user_id: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error creating user progress: {e}")
        return False

def get_user_progress(user_id: int):
    """Get user progress data"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return None
        
        session = conn.session()
        query = f"""
        SELECT * FROM user_progress WHERE user_id = {user_id}
        """
        
        result = session.sql(query).collect()
        
        if result and len(result) > 0:
            row = result[0]
            return row.as_dict()
        return None
    except Exception as e:
        logger.error(f"Error retrieving user progress: {e}")
        return None

def get_topic_progress(user_id: int):
    """Get topic progress data"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return None
        
        session = conn.session()
        query = f"""
        SELECT * FROM topic_progress WHERE user_id = {user_id}
        """
        
        result = session.sql(query).collect()
        
        if result and len(result) > 0:
            row = result[0]
            return {
                'USER_ID': row['USER_ID'],
                'TOPIC': row['TOPIC'],
                'PROGRESS_PERCENTAGE': row['PROGRESS_PERCENTAGE'],
                'UPDATED_AT': row['UPDATED_AT']
            }
        return None
    except Exception as e:
        logger.error(f"Error retrieving topic progress: {e}")

def get_activity_log(user_id: int):
    """Get activity log data"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return None
        
        session = conn.session()
        query = f"""
        SELECT * FROM activity_log WHERE user_id = {user_id} LIMIT 3"""
        
        result = session.sql(query).collect()
        
        if result and len(result) > 0:
            return result
        return None
    except Exception as e:
        logger.error(f"Error retrieving activity log: {e}")
        return None

# ============================================
# CHAT HISTORY OPERATIONS
# ============================================

def save_chat_message(user_id: int, question: str, answer: str):
    """Save chat message to Snowflake"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return False
        
        session = conn.session()
        # Escape single quotes
        question = question.replace("'", "''")
        answer = answer.replace("'", "''")
        
        query = f"""
        INSERT INTO chat_history (user_id, question, answer, created_at)
        VALUES ({user_id}, '{question}', '{answer}', CURRENT_TIMESTAMP())
        """
        
        session.sql(query).collect()
        logger.debug(f"Chat message saved for user_id: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving chat message: {e}")
        return False

def get_chat_history(user_id: int, limit: int = 50):
    """Retrieve chat history for a user"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return []
        
        session = conn.session()
        query = f"""
        SELECT id, question, answer, created_at 
        FROM chat_history 
        WHERE user_id = {user_id} 
        ORDER BY created_at DESC 
        LIMIT {limit}
        """
        
        result = session.sql(query).collect()
        
        history = []
        for row in result:
            history.append({
                'ID': row['ID'],
                'QUESTION': row['QUESTION'],
                'ANSWER': row['ANSWER'],
                'CREATED_AT': row['CREATED_AT']
            })
        
        return history
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        return []

# ============================================
# ACTIVITY LOGGING
# ============================================

def log_activity(user_id: int, action: str, details: str = None, ip_address: str = None):
    """Log user activity for auditing"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return False
        
        session = conn.session()
        details_str = f"'{details.replace(chr(39), chr(39)+chr(39))}'" if details else 'NULL'
        ip_str = f"'{ip_address}'" if ip_address else 'NULL'
        
        query = f"""
        INSERT INTO activity_log (user_id, action, details, ip_address, created_at)
        VALUES ({user_id if user_id else 'NULL'}, '{action}', {details_str}, {ip_str}, CURRENT_TIMESTAMP())
        """
        
        session.sql(query).collect()
        return True
    except Exception as e:
        logger.error(f"Error logging activity: {e}")
        return False

def get_qa_data(category: str, difficulty: str, target_certification: str):
    """Get Q&A data from Snowflake"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return None
        
        session = conn.session()

        if category != "All":
            query = f"SELECT * FROM aws_scenarios WHERE target_certification ILIKE '%{target_certification}%' AND lower(category) = lower('{category}')"
        else:
            query = f"SELECT * FROM aws_scenarios WHERE target_certification ILIKE '%{target_certification}%'"
        
        if difficulty != "All":
            query = query + f" AND lower(difficulty) = lower('{difficulty}')"

        result = session.sql(query).collect()
        return result
    except Exception as e:
        logger.error(f"Error retrieving Q&A data: {e}")
        return None

# ============================================
# TESTING & INITIALIZATION
# ============================================

def test_connection():
    """Test Snowflake connection"""
    try:
        conn = get_snowflake_connection()
        if conn is None:
            return False
        
        session = conn.session()
        result = session.sql("SELECT CURRENT_VERSION()").collect()
        logger.info(f"✅ Snowflake connection test successful: {result[0][0]}")
        return True
    except Exception as e:
        logger.error(f"❌ Snowflake connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔍 Testing Snowflake Connection")
    print("="*60 + "\n")
    
    if test_connection():
        print("✅ Connection test passed")
    else:
        print("❌ Connection test failed")
    
    print("\n" + "="*60)
