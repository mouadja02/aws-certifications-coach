"""
Database connection and operations for AWS Certifications Coach - PRODUCTION VERSION
Enhanced for AWS RDS PostgreSQL with SSL, connection pooling, and monitoring
"""

import os
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, DateTime, Text, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from dotenv import load_dotenv
import logging
import ssl

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# ============================================
# DATABASE CONFIGURATION
# ============================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "aws_certifications")
DB_USER = os.getenv("DB_USER", "awscoach")
DB_PASSWORD = os.getenv("DB_PASSWORD", "changeme123")
DB_SSL_MODE = os.getenv("DB_SSL_MODE", "prefer")  # require, verify-ca, verify-full for production

# Connection pool configuration for production
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "40"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour

# ============================================
# SSL CONFIGURATION FOR AWS RDS
# ============================================

connect_args = {}

if DB_SSL_MODE == "require":
    # For AWS RDS, SSL is required
    connect_args["sslmode"] = "require"
    logger.info("Database SSL mode: require (AWS RDS)")
elif DB_SSL_MODE in ["verify-ca", "verify-full"]:
    # For stricter SSL verification
    connect_args["sslmode"] = DB_SSL_MODE
    # Optional: specify CA certificate path
    ca_cert_path = os.getenv("DB_SSL_CA_CERT")
    if ca_cert_path:
        connect_args["sslrootcert"] = ca_cert_path
    logger.info(f"Database SSL mode: {DB_SSL_MODE}")
else:
    # Development mode
    connect_args["sslmode"] = "prefer"
    logger.info("Database SSL mode: prefer (development)")

# ============================================
# CREATE DATABASE ENGINE
# ============================================

# Build connection string
connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine with production settings
engine = sqlalchemy.create_engine(
    connection_string,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,  # Recycle connections after 1 hour
    echo=os.getenv("DB_ECHO", "false").lower() == "true",  # Log SQL queries (debug only)
    connect_args=connect_args,
    execution_options={
        "isolation_level": "READ COMMITTED"
    }
)

Base = declarative_base()
metadata = MetaData()

# ============================================
# DATABASE SCHEMA DEFINITIONS
# ============================================

# Users table
logged_users = Table(
    'logged_users',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('age', Integer, nullable=True),
    Column('target_certification', String(255), nullable=False),
    Column('email', String(255), nullable=False, unique=True, index=True),
    Column('password', String(255), nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
    Column('is_active', Integer, default=1),
    Column('last_login', DateTime, nullable=True),
)

# Chat history table
chat_history = Table(
    'chat_history',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, nullable=False, index=True),
    Column('question', Text, nullable=False),
    Column('answer', Text, nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
)

# User progress table
user_progress = Table(
    'user_progress',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, nullable=False, unique=True, index=True),
    Column('study_time_minutes', Integer, default=0),
    Column('practice_tests_taken', Integer, default=0),
    Column('average_score', Integer, default=0),
    Column('progress_percentage', Integer, default=0),
    Column('last_activity', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
)

# Activity log table (for auditing)
activity_log = Table(
    'activity_log',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, nullable=True, index=True),
    Column('action', String(100), nullable=False),
    Column('details', Text, nullable=True),
    Column('ip_address', String(50), nullable=True),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
)

# ============================================
# CONNECTION MANAGEMENT
# ============================================

def get_db_connection():
    """
    Establish a connection to the database with error handling
    Returns: connection object or None if failed
    """
    try:
        connection = engine.connect()
        logger.debug("Database connection established")
        return connection
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error connecting to database: {e}")
        return None

def close_db_connection(connection):
    """
    Close the database connection safely
    """
    if connection:
        try:
            connection.close()
            logger.debug("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

def test_db_connection():
    """
    Test database connectivity
    Returns: True if successful, False otherwise
    """
    try:
        connection = get_db_connection()
        if connection:
            # Execute a simple query
            result = connection.execute(sqlalchemy.text("SELECT 1"))
            result.fetchone()
            close_db_connection(connection)
            logger.info("✅ Database connection test successful")
            return True
        else:
            logger.error("❌ Database connection test failed")
            return False
    except Exception as e:
        logger.error(f"❌ Database connection test error: {e}")
        return False

# ============================================
# SCHEMA MANAGEMENT
# ============================================

def create_tables():
    """
    Create all tables defined in the metadata
    """
    try:
        metadata.create_all(engine)
        logger.info("✅ Database tables created/verified successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

def drop_tables():
    """
    Drop all tables (USE WITH CAUTION - PRODUCTION SAFETY)
    """
    if os.getenv("APP_ENV") == "production":
        logger.error("❌ Cannot drop tables in production environment")
        return False
    
    try:
        metadata.drop_all(engine)
        logger.warning("⚠️ All tables dropped")
        return True
    except Exception as e:
        logger.error(f"❌ Error dropping tables: {e}")
        return False

# ============================================
# USER OPERATIONS
# ============================================

def check_if_user_exists(email: str) -> bool:
    """
    Check if a user with the given email exists in the database
    """
    connection = get_db_connection()
    if connection is None:
        return False
    
    try:
        query = select(logged_users).where(logged_users.c.email == email)
        result = connection.execute(query)
        user_exists = result.fetchone() is not None
        return user_exists
    except SQLAlchemyError as e:
        logger.error(f"Error checking if user exists: {e}")
        return False
    finally:
        close_db_connection(connection)

def insert_user(name: str, email: str, password: str, target_certification: str, age: int = None):
    """
    Insert a new user into the database with transaction support
    """
    connection = get_db_connection()
    if connection is None:
        return False
    
    try:
        # Begin transaction
        trans = connection.begin()
        
        # Insert new user
        query = logged_users.insert().values(
            name=name,
            email=email,
            password=password,  # Should already be hashed
            target_certification=target_certification,
            age=age,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=1
        )
        connection.execute(query)
        
        # Commit transaction
        trans.commit()
        
        # Create initial user progress entry
        user = get_user_by_email(email)
        if user:
            create_user_progress(user['id'])
        
        logger.info(f"User created successfully: {email}")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error inserting user: {e}")
        try:
            trans.rollback()
        except:
            pass
        return False
    finally:
        close_db_connection(connection)

def get_user_by_email(email: str):
    """
    Retrieve a user by their email address
    """
    connection = get_db_connection()
    if connection is None:
        return None
    
    try:
        query = select(logged_users).where(
            logged_users.c.email == email,
            logged_users.c.is_active == 1
        )
        result = connection.execute(query)
        row = result.fetchone()
        
        if row:
            return {
                'id': row.id,
                'name': row.name,
                'email': row.email,
                'password': row.password,
                'age': row.age,
                'target_certification': row.target_certification,
                'created_at': row.created_at,
                'updated_at': row.updated_at,
                'last_login': row.last_login
            }
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving user: {e}")
        return None
    finally:
        close_db_connection(connection)

def update_last_login(email: str):
    """
    Update user's last login timestamp
    """
    connection = get_db_connection()
    if connection is None:
        return False
    
    try:
        query = logged_users.update().where(
            logged_users.c.email == email
        ).values(last_login=datetime.utcnow())
        
        connection.execute(query)
        connection.commit()
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error updating last login: {e}")
        return False
    finally:
        close_db_connection(connection)

# ============================================
# USER PROGRESS OPERATIONS
# ============================================

def create_user_progress(user_id: int):
    """
    Create initial progress entry for a user
    """
    connection = get_db_connection()
    if connection is None:
        return False
    
    try:
        query = user_progress.insert().values(
            user_id=user_id,
            study_time_minutes=0,
            practice_tests_taken=0,
            average_score=0,
            progress_percentage=0,
            last_activity=datetime.utcnow()
        )
        connection.execute(query)
        connection.commit()
        logger.debug(f"User progress created for user_id: {user_id}")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error creating user progress: {e}")
        return False
    finally:
        close_db_connection(connection)

def get_user_progress(user_id: int):
    """
    Get user progress data
    """
    connection = get_db_connection()
    if connection is None:
        return None
    
    try:
        query = select(user_progress).where(user_progress.c.user_id == user_id)
        result = connection.execute(query)
        row = result.fetchone()
        
        if row:
            return {
                'user_id': row.user_id,
                'study_time_minutes': row.study_time_minutes,
                'practice_tests_taken': row.practice_tests_taken,
                'average_score': row.average_score,
                'progress_percentage': row.progress_percentage,
                'last_activity': row.last_activity,
                'updated_at': row.updated_at
            }
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving user progress: {e}")
        return None
    finally:
        close_db_connection(connection)

# ============================================
# CHAT HISTORY OPERATIONS
# ============================================

def save_chat_message(user_id: int, question: str, answer: str):
    """
    Save chat message to history
    """
    connection = get_db_connection()
    if connection is None:
        return False
    
    try:
        query = chat_history.insert().values(
            user_id=user_id,
            question=question,
            answer=answer,
            created_at=datetime.utcnow()
        )
        connection.execute(query)
        connection.commit()
        logger.debug(f"Chat message saved for user_id: {user_id}")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error saving chat message: {e}")
        return False
    finally:
        close_db_connection(connection)

def get_chat_history(user_id: int, limit: int = 50):
    """
    Retrieve chat history for a user
    """
    connection = get_db_connection()
    if connection is None:
        return []
    
    try:
        query = select(chat_history).where(
            chat_history.c.user_id == user_id
        ).order_by(chat_history.c.created_at.desc()).limit(limit)
        
        result = connection.execute(query)
        rows = result.fetchall()
        
        history = []
        for row in rows:
            history.append({
                'id': row.id,
                'question': row.question,
                'answer': row.answer,
                'created_at': row.created_at
            })
        
        return history
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving chat history: {e}")
        return []
    finally:
        close_db_connection(connection)

# ============================================
# ACTIVITY LOGGING
# ============================================

def log_activity(user_id: int, action: str, details: str = None, ip_address: str = None):
    """
    Log user activity for auditing purposes
    """
    connection = get_db_connection()
    if connection is None:
        return False
    
    try:
        query = activity_log.insert().values(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            created_at=datetime.utcnow()
        )
        connection.execute(query)
        connection.commit()
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error logging activity: {e}")
        return False
    finally:
        close_db_connection(connection)

# ============================================
# CONNECTION POOL MONITORING
# ============================================

@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Event listener for new connections"""
    logger.debug("New database connection established")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Event listener for connection checkout from pool"""
    logger.debug("Connection checked out from pool")

# ============================================
# INITIALIZATION & TESTING
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔍 Testing Production Database Configuration")
    print("="*60 + "\n")
    
    print(f"Database Host: {DB_HOST}")
    print(f"Database Name: {DB_NAME}")
    print(f"SSL Mode: {DB_SSL_MODE}")
    print(f"Pool Size: {POOL_SIZE}")
    print(f"Max Overflow: {MAX_OVERFLOW}\n")
    
    # Test connection
    if test_db_connection():
        print("✅ Connection test passed")
        
        # Create tables
        if create_tables():
            print("✅ Tables created/verified")
        else:
            print("❌ Failed to create tables")
    else:
        print("❌ Connection test failed")
    
    print("\n" + "="*60)
