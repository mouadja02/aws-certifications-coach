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
from styles import get_custom_css, create_badge

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

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Using Snowflake directly - no backend health check needed

def show_home_page():
    """Display the premium home page with stunning visuals"""
    
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div style="margin-bottom: 2rem;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg" 
                 style="height: 80px; margin-bottom: 1rem;" alt="AWS Logo">
        </div>
        <h1 class="hero-title">AWS Certifications Coach</h1>
        <p class="hero-subtitle">Master AWS Certifications 10x Faster with AI-Powered Learning</p>
        <div style="display: flex; gap: 1rem; justify-content: center; margin: 2rem 0; font-size: 1.1rem; color: #6b7280;">
            <div>⚡ <strong>50,000+</strong> Certified Professionals</div>
            <div>📊 <strong>2M+</strong> Questions Answered</div>
            <div>🏆 <strong>98%</strong> Pass Rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Login/Register Cards
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔐</div>
            <h3 style="margin-bottom: 1rem; color: #232F3E;">Welcome Back!</h3>
            <p style="color: #6b7280; margin-bottom: 1.5rem;">Login to continue your learning journey</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔐 Login to Dashboard", use_container_width=True, type="primary"):
            st.session_state.page = "login"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🚀</div>
            <h3 style="margin-bottom: 1rem; color: #232F3E;">Get Started</h3>
            <p style="color: #6b7280; margin-bottom: 1.5rem;">Create your free account in seconds</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📝 Create Free Account", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()
    
    # Features Section
    st.write("")
    st.markdown('<h2 style="text-align: center; margin: 3rem 0 2rem 0; font-size: 2.5rem;">✨ What You\'ll Get</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center; min-height: 280px;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🤖</div>
            <h3 style="color: #FF9900; margin-bottom: 1rem;">AI Study Coach</h3>
            <p style="color: #6b7280; line-height: 1.6;">
                Get instant answers to your questions with our AI-powered study assistant. 
                Available 24/7 to help you master AWS concepts.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center; min-height: 280px;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📝</div>
            <h3 style="color: #FF9900; margin-bottom: 1rem;">Practice Exams</h3>
            <p style="color: #6b7280; line-height: 1.6;">
                Take unlimited AI-generated practice tests that adapt to your skill level. 
                Real exam simulation with instant feedback.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="glass-card" style="text-align: center; min-height: 280px;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🧠</div>
            <h3 style="color: #FF9900; margin-bottom: 1rem;">Memory Techniques</h3>
            <p style="color: #6b7280; line-height: 1.6;">
                Learn proven memory tricks and mnemonics to retain complex AWS concepts. 
                Study smarter, not harder.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional Features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center; min-height: 280px;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #FF9900; margin-bottom: 1rem;">Progress Tracking</h3>
            <p style="color: #6b7280; line-height: 1.6;">
                Visualize your learning journey with detailed analytics. 
                Track your strengths and focus on weak areas.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center; min-height: 280px;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">✍️</div>
            <h3 style="color: #FF9900; margin-bottom: 1rem;">Answer Evaluation</h3>
            <p style="color: #6b7280; line-height: 1.6;">
                Write detailed answers and get AI-powered feedback. 
                Perfect your exam writing skills.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="glass-card" style="text-align: center; min-height: 280px;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">❓</div>
            <h3 style="color: #FF9900; margin-bottom: 1rem;">Q&A Knowledge Base</h3>
            <p style="color: #6b7280; line-height: 1.6;">
                Access thousands of frequently asked questions. 
                Search and learn from the community.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Testimonials Section
    st.write("")
    st.markdown('<h2 style="text-align: center; margin: 3rem 0 2rem 0; font-size: 2.5rem;">💬 What Learners Say</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <div style="color: #FFD700; font-size: 1.5rem; margin-bottom: 0.5rem;">⭐⭐⭐⭐⭐</div>
            <p style="color: #6b7280; font-style: italic; margin-bottom: 1rem;">
                "Passed my Solutions Architect exam on the first try! The AI coach 
                helped me understand complex concepts easily."
            </p>
            <p style="font-weight: 700; color: #232F3E;">- Sarah K., Cloud Engineer</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card">
            <div style="color: #FFD700; font-size: 1.5rem; margin-bottom: 0.5rem;">⭐⭐⭐⭐⭐</div>
            <p style="color: #6b7280; font-style: italic; margin-bottom: 1rem;">
                "The practice exams are incredibly realistic. I felt completely 
                prepared for the actual test. Highly recommended!"
            </p>
            <p style="font-weight: 700; color: #232F3E;">- Michael T., DevOps Lead</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="glass-card">
            <div style="color: #FFD700; font-size: 1.5rem; margin-bottom: 0.5rem;">⭐⭐⭐⭐⭐</div>
            <p style="color: #6b7280; font-style: italic; margin-bottom: 1rem;">
                "Best investment for my career! Got certified in 3 months and landed 
                my dream job at a Fortune 500 company."
            </p>
            <p style="font-weight: 700; color: #232F3E;">- Jessica L., Solutions Architect</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.write("")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; margin-top: 3rem; border-top: 1px solid rgba(255, 153, 0, 0.2);">
        <p style="color: #6b7280; margin-bottom: 0.5rem;">© 2024 AWS Certifications Coach | Version 2.0.0</p>
        <p style="color: #9ca3af; font-size: 0.875rem;">
            Not affiliated with Amazon Web Services. AWS and the AWS logo are trademarks of Amazon.com, Inc.
        </p>
    </div>
    """, unsafe_allow_html=True)

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
    """Display the premium login page with glassmorphic design"""
    
    # Header
    st.markdown("""
    <div class="hero-container" style="padding: 2rem;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg" 
             style="height: 60px; margin-bottom: 1rem;" alt="AWS Logo">
        <h1 class="hero-title" style="font-size: 2.5rem;">Welcome Back!</h1>
        <p class="hero-subtitle" style="font-size: 1.2rem;">Login to continue your AWS certification journey</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login Form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown('<h3 style="text-align: center; color: #232F3E; margin-bottom: 1.5rem;">🔐 Sign In</h3>', unsafe_allow_html=True)
            
            email = st.text_input("📧 Email Address", placeholder="your.email@example.com", label_visibility="visible")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", label_visibility="visible")
            
            st.write("")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
            with col_b:
                back = st.form_submit_button("← Back", use_container_width=True)
            
            if back:
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
                        with st.spinner("🔄 Logging you in..."):
                            if login_user(email, password):
                                logger.info(f"Successful login: {email}")
                                st.success("✅ Login successful! Redirecting...")
                                st.session_state.page = "dashboard"
                                st.session_state.last_activity = st.session_state.get('last_activity', None)
                                import time
                                time.sleep(1)
                                st.rerun()
                            else:
                                logger.warning(f"Failed login attempt: {email}")
                                st.error("❌ Invalid email or password. Please try again.")
                    except Exception as e:
                        logger.error(f"Login error: {e}")
                        st.error("❌ An unexpected error occurred. Please try again.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("")
        st.markdown("""
        <div style="text-align: center; margin-top: 1.5rem;">
            <p style="color: #6b7280;">Don't have an account? 
            <span style="color: #FF9900; font-weight: 700; cursor: pointer;">Create one now!</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Create New Account", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

def show_register_page():
    """Display the premium registration page with enhanced validation"""
    
    # Header
    st.markdown("""
    <div class="hero-container" style="padding: 2rem;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg" 
             style="height: 60px; margin-bottom: 1rem;" alt="AWS Logo">
        <h1 class="hero-title" style="font-size: 2.5rem;">Start Your Journey</h1>
        <p class="hero-subtitle" style="font-size: 1.2rem;">Create your free account and master AWS certifications</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Registration Form
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    
    with col2:
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        
        with st.form("register_form"):
            st.markdown('<h3 style="text-align: center; color: #232F3E; margin-bottom: 1.5rem;">🚀 Create Account</h3>', unsafe_allow_html=True)
            
            name = st.text_input("👤 Full Name", placeholder="John Doe", label_visibility="visible")
            email = st.text_input("📧 Email Address", placeholder="john.doe@example.com", label_visibility="visible")
            
            col_pass1, col_pass2 = st.columns(2)
            with col_pass1:
                password = st.text_input("🔒 Password", type="password", placeholder="Min 8 characters", label_visibility="visible")
            with col_pass2:
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password", label_visibility="visible")
            
            # Password strength indicator
            if password:
                is_valid, msg = validate_password(password)
                if is_valid:
                    st.success("✅ Password strength: Strong")
                else:
                    st.warning(f"⚠️ {msg}")
            
            age = st.number_input("🎂 Age", min_value=18, max_value=100, value=25, label_visibility="visible")

            certification = st.selectbox(
                "🎓 Target AWS Certification",
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
                ],
                label_visibility="visible"
            )
            
            st.write("")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("✨ Create Account", use_container_width=True, type="primary")
            with col_b:
                back = st.form_submit_button("← Back", use_container_width=True)
            
            if back:
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
                            with st.spinner("🔄 Creating your account..."):
                                if register_user(name, email, password, certification, age):
                                    logger.info(f"New user registered: {email}")
                                    st.success("🎉 Account created successfully! Redirecting to login...")
                                    # Auto-redirect to login after 2 seconds
                                    import time
                                    time.sleep(2)
                                    st.session_state.page = "login"
                                    st.rerun()
                        except Exception as e:
                            logger.error(f"Registration error: {e}")
                            st.error("❌ An unexpected error occurred. Please try again.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Password requirements info
        with st.expander("ℹ️ Password Requirements"):
            st.markdown("""
            <div style="padding: 0.5rem;">
                <p style="font-weight: 600; color: #232F3E; margin-bottom: 0.5rem;">Your password must:</p>
                <ul style="color: #6b7280; line-height: 1.8;">
                    <li>Be at least 8 characters long</li>
                    <li>Contain at least one uppercase letter (A-Z)</li>
                    <li>Contain at least one lowercase letter (a-z)</li>
                    <li>Contain at least one number (0-9)</li>
                    <li>Special characters recommended for extra security</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        st.markdown("""
        <div style="text-align: center; margin-top: 1.5rem;">
            <p style="color: #6b7280;">Already have an account? 
            <span style="color: #FF9900; font-weight: 700; cursor: pointer;">Login now!</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔐 Login to Dashboard", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

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
        
        # Check if last_activity is not None before comparing
        if last_activity is not None and current_time - last_activity > st.session_state.session_timeout:
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

