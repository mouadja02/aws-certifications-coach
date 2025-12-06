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
    update_last_login
)
from auth import get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)

def register_user(name: str, email: str, password: str, certification: str, age: int):
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
            target_certification=certification,
            age=age
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

