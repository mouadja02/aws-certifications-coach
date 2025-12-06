"""
AWS Certifications Coach - Home Page (PRODUCTION VERSION)
Features: Logo, Headline, Login, Register
Enhanced with production security and error handling
"""

import streamlit as st
from pathlib import Path
import logging

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dashboard import show_dashboard
from utils import register_user, login_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AWS Certifications Coach",
    page_icon="☁️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# No backend API needed - using Snowflake directly

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #FF9900;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #232F3E;
        font-size: 1.5rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF9900;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #EC7211;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    /* Hide Streamlit branding in production */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Using Snowflake directly - no backend health check needed

def show_home_page():
    """Display the home page"""
    
    # Logo
    logo_path = Path(__file__).parent / "images" / "logo.png"
    if logo_path.exists():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(str(logo_path), use_column_width=True)
    
    # Header
    st.markdown('<h1 class="main-header">AWS Certifications Coach</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Master AWS Certifications with AI-Powered Learning</p>', unsafe_allow_html=True)
    
    # Add some spacing
    st.write("")
    st.write("")
    
    # Welcome message
    st.info("🚀 Welcome! Start your AWS certification journey today.")
    
    # Create two columns for Login and Register buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔐 Login"):
            st.session_state.page = "login"
            st.rerun()
    
    with col2:
        if st.button("📝 Register"):
            st.session_state.page = "register"
            st.rerun()
    
    # Add feature highlights
    st.write("")
    st.write("---")
    st.subheader("✨ Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📚 Study Materials")
        st.write("Comprehensive study guides for all AWS certifications")
    
    with col2:
        st.markdown("### 🎯 Practice Tests")
        st.write("Realistic practice exams to test your knowledge")
    
    with col3:
        st.markdown("### 🤖 AI Coach")
        st.write("Personalized learning recommendations powered by AI")
    
    # Add footer with version info
    st.write("")
    st.write("---")
    st.caption("Version 2.0.0 | Production")

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, ""

def show_login_page():
    """Display the login page with enhanced security"""
    st.markdown('<h1 class="main-header">Login</h1>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Login")
        with col2:
            if st.form_submit_button("Back to Home"):
                st.session_state.page = "home"
                st.rerun()
        
        if submit:
            # Validate inputs
            if not email or not password:
                st.error("❌ Please enter both email and password")
            elif not validate_email(email):
                st.error("❌ Please enter a valid email address")
            else:
                # Attempt login with error handling
                try:
                    with st.spinner("Logging in..."):
                        if login_user(email, password):
                            logger.info(f"Successful login: {email}")
                            st.session_state.page = "dashboard"
                            st.session_state.last_activity = st.session_state.get('last_activity', None)
                            st.rerun()
                        else:
                            logger.warning(f"Failed login attempt: {email}")
                except Exception as e:
                    logger.error(f"Login error: {e}")
                    st.error("❌ An unexpected error occurred. Please try again.")
    
    st.write("")
    st.info("Don't have an account? Go back and click Register!")

def show_register_page():
    """Display the registration page with enhanced validation"""
    st.markdown('<h1 class="main-header">Register</h1>', unsafe_allow_html=True)
    
    with st.form("register_form"):
        name = st.text_input("👤 Full Name", placeholder="Enter your full name")
        email = st.text_input("📧 Email", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Create a password (min 8 chars)")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
        age = st.number_input("👵 Age", min_value=18, max_value=100, value=25)

        certification = st.selectbox(
            "🎓 Which AWS certification are you interested in?",
            [
                "AWS Certified Cloud Practitioner",
                "AWS Certified AI Practitioner",
                "AWS Certified Solutions Architect - Associate",
                "AWS Certified Developer - Associate",
                "AWS Certified SysOps Administrator - Associate",
                "AWS Certified Solutions Architect - Professional",
                "AWS Certified DevOps Engineer - Professional",
                "AWS Certified Security - Specialty",
                "AWS Certified Machine Learning - Specialty",
                "AWS Certified Data Analytics - Specialty",
                "AWS Certified Database - Specialty",
                "AWS Certified Advanced Networking - Specialty",
            ]
        )
        
        # Password strength indicator
        if password:
            is_valid, msg = validate_password(password)
            if is_valid:
                st.success("✅ Password strength: Strong")
            else:
                st.warning(f"⚠️ {msg}")

        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Create Account")
        with col2:
            if st.form_submit_button("Back to Home"):
                st.session_state.page = "home"
                st.rerun()
        
        if submit:
            # Validate all inputs
            if not all([name, email, password, confirm_password]):
                st.error("❌ Please fill in all fields")
            elif not validate_email(email):
                st.error("❌ Please enter a valid email address")
            elif password != confirm_password:
                st.error("❌ Passwords do not match")
            else:
                # Check password strength
                is_valid, msg = validate_password(password)
                if not is_valid:
                    st.error(f"❌ {msg}")
                else:
                    # Attempt registration
                    try:
                        with st.spinner("Creating your account..."):
                            if register_user(name, email, password, certification, age):
                                logger.info(f"New user registered: {email}")
                                st.success("✅ Account created successfully! Please login.")
                                # Auto-redirect to login after 2 seconds
                                import time
                                time.sleep(2)
                                st.session_state.page = "login"
                                st.rerun()
                    except Exception as e:
                        logger.error(f"Registration error: {e}")
                        st.error("❌ An unexpected error occurred. Please try again.")

    # Password requirements info
    with st.expander("ℹ️ Password Requirements"):
        st.write("""
        Your password must:
        - Be at least 8 characters long
        - Contain at least one uppercase letter
        - Contain at least one lowercase letter
        - Contain at least one number
        - Should include special characters for extra security
        """)

def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'session_timeout' not in st.session_state:
        st.session_state.session_timeout = 3600  # 1 hour
    
    # Session timeout check (if authenticated)
    if st.session_state.authenticated and 'last_activity' in st.session_state:
        import time
        current_time = time.time()
        last_activity = st.session_state.last_activity
        
        if current_time - last_activity > st.session_state.session_timeout:
            logger.info("Session timeout - logging out user")
            st.session_state.authenticated = False
            st.session_state.page = "home"
            st.warning("Your session has expired. Please login again.")
    
    # Update last activity timestamp
    if st.session_state.authenticated:
        import time
        st.session_state.last_activity = time.time()
    
    # Route to appropriate page
    try:
        if st.session_state.page == "home":
            show_home_page()
        elif st.session_state.page == "login":
            show_login_page()
        elif st.session_state.page == "register":
            show_register_page()
        elif st.session_state.page == "dashboard":
            if st.session_state.authenticated:
                show_dashboard()
            else:
                st.warning("Please login to access the dashboard")
                st.session_state.page = "login"
                st.rerun()
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An unexpected error occurred. Please refresh the page.")
        if st.button("Return to Home"):
            st.session_state.page = "home"
            st.rerun()

if __name__ == "__main__":
    main()

