"""
Utility functions for frontend operations
"""

import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

def register_user(name: str, email: str, password: str, target_certification: str, age: int = None):
    """Register a new user by calling the backend API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/register",
            json={
                "name": name,
                "email": email,
                "password": password,
                "target_certification": target_certification,
                "age": age,
            }
        )
        if response.status_code == 200:
            st.success("✅ User created successfully!")
            st.balloons()
            user_data = response.json()
            st.session_state.authenticated = True
            st.session_state.user_email = user_data['email']
            st.session_state.user_name = user_data['name']
            st.session_state.target_certification = user_data['target_certification']
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error(f"❌ {response.json().get('detail', 'Registration failed')}")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error connecting to the backend: {e}")


def login_user(email: str, password: str) -> bool:
    """Login user by calling the backend API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            user_data = response.json()['user']
            st.session_state.authenticated = True
            st.session_state.user_email = user_data['email']
            st.session_state.page = "dashboard"
            st.rerun()
            return True
        else:
            st.error(f"❌ {response.json().get('detail', 'Login failed')}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error connecting to the backend: {e}")
        return False