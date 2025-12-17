"""
Utility functions for AWS Certifications Coach
Handles user authentication and registration with Snowflake
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import (
    check_if_user_exists,
    insert_user,
    get_user_by_email,
    update_last_login,
    log_activity,
    increment_user_streak
)
from auth import get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)

# ============================================
# CERTIFICATION TOPIC MAPPINGS
# ============================================

# Define topics tracked for each certification (6 topics per certification)
CERTIFICATION_TOPICS = {
    "AWS Certified Cloud Practitioner": [
        "Storage Services",
        "Compute Services",
        "Networking & Content Delivery",
        "Security, Identity & Compliance",
        "Database Services",
        "Cost Management"
    ],
    "AWS Certified Solutions Architect - Associate": [
        "Storage Services",
        "Compute Services",
        "Networking & Content Delivery",
        "Security, Identity & Compliance",
        "Database Services",
        "High Availability & Fault Tolerance"
    ],
    "AWS Certified Developer - Associate": [
        "Compute Services",
        "Database Services",
        "Application Integration",
        "Security, Identity & Compliance",
        "Developer Tools & DevOps",
        "Serverless Computing"
    ],
    "AWS Certified SysOps Administrator - Associate": [
        "Compute Services",
        "Networking & Content Delivery",
        "Security, Identity & Compliance",
        "Management & Governance",
        "High Availability & Fault Tolerance",
        "Cost Management"
    ],
    "AWS Certified Solutions Architect - Professional": [
        "Storage Services",
        "Compute Services",
        "Networking & Content Delivery",
        "Security, Identity & Compliance",
        "Database Services",
        "High Availability & Fault Tolerance"
    ],
    "AWS Certified DevOps Engineer - Professional": [
        "Compute Services",
        "Management & Governance",
        "Developer Tools & DevOps",
        "Security, Identity & Compliance",
        "Serverless Computing",
        "Containers"
    ],
    "AWS Certified Security - Specialty": [
        "Security, Identity & Compliance",
        "Networking & Content Delivery",
        "Management & Governance",
        "Storage Services",
        "Database Services",
        "Application Integration"
    ],
    "AWS Certified Machine Learning - Specialty": [
        "Machine Learning & AI",
        "Analytics & Big Data",
        "Storage Services",
        "Compute Services",
        "Security, Identity & Compliance",
        "Application Integration"
    ],
    "AWS Certified Data Analytics - Specialty": [
        "Analytics & Big Data",
        "Database Services",
        "Storage Services",
        "Application Integration",
        "Security, Identity & Compliance",
        "Management & Governance"
    ],
    "AWS Certified Database - Specialty": [
        "Database Services",
        "Storage Services",
        "Compute Services",
        "Security, Identity & Compliance",
        "High Availability & Fault Tolerance",
        "Migration & Transfer"
    ],
    "AWS Certified Advanced Networking - Specialty": [
        "Networking & Content Delivery",
        "Security, Identity & Compliance",
        "Hybrid Cloud & Edge",
        "High Availability & Fault Tolerance",
        "Management & Governance",
        "Application Integration"
    ],
    "AWS Certified Data Engineer - Associate": [
        "Analytics & Big Data",
        "Database Services",
        "Storage Services",
        "Compute Services",
        "Security, Identity & Compliance",
        "Application Integration"
    ],
    "AWS Certified AI Practitioner": [
        "Machine Learning & AI",
        "Serverless Computing",
        "Database Services",
        "Security, Identity & Compliance",
        "Application Integration",
        "Analytics & Big Data"
    ]
}

def get_topics_for_certification(certification: str):
    """
    Get the list of topics for a specific certification.
    Returns default topics if certification not found.
    """
    # Try exact match first
    if certification in CERTIFICATION_TOPICS:
        return CERTIFICATION_TOPICS[certification]
    
    # Try partial match (in case certification name has variations)
    for cert_name, topics in CERTIFICATION_TOPICS.items():
        if cert_name.lower() in certification.lower() or certification.lower() in cert_name.lower():
            return topics
    
    # Default fallback for unknown certifications
    return [
        "Storage Services",
        "Compute Services",
        "Networking & Content Delivery",
        "Security, Identity & Compliance",
        "Database Services",
        "Management & Governance"
    ]

def get_topic_index(topic: str, tracked_topics: list) -> int:
    """
    Get the index of a topic in the tracked topics list.
    Returns -1 if topic not found.
    """
    try:
        return tracked_topics.index(topic)
    except (ValueError, AttributeError):
        return -1

def register_user(name: str, email: str, password: str, certification: str):
    """
    Register a new user
    Returns: True if successful, False otherwise
    """
    try:
        # Check if user already exists
        if check_if_user_exists(email):
            st.error("❌ User with this email already exists")
            return False
        
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Insert user into Snowflake
        success = insert_user(
            name=name,
            email=email,
            password=hashed_password,
            target_certification=certification
        )
        
        if success:
            st.success("✅ Account created successfully! Please login.")
            return True
        else:
            st.error("❌ Failed to create account. Please try again.")
            return False
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        st.error(f"❌ An error occurred: {str(e)}")
        return False

def login_user(email: str, password: str):
    """
    Authenticate user login
    Returns: True if successful, False otherwise
    """
    try:
        # Get user from Snowflake
        user = get_user_by_email(email)
        
        if not user:
            logger.warning(f"Failed login attempt: {email}")
            st.error("❌ Invalid email or password")
            return False
        
        # Verify password
        if not verify_password(password, user['PASSWORD']):
            logger.warning(f"Failed login attempt: {email}")
            st.error("❌ Invalid email or password")
            return False
        
        # Update last login
        update_last_login(email)

        # Log activity
        log_activity(user['ID'], 'login', f"{user['NAME']} logged in successfully")

        # Increment user streak
        increment_user_streak(user['ID'])

        # Store user info in session
        st.session_state.authenticated = True
        st.session_state.user_email = email
        st.session_state.user_id = user['ID']
        st.session_state.user_name = user['NAME']

        logger.info(f"Successful login: {email}")
        return True
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        st.error(f"❌ An error occurred: {str(e)}")
        return False
