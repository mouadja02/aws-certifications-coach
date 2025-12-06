# User Dashboard (after successful login)

import streamlit as st
import sys
import os
import requests
import time
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

def get_user_from_api(email: str):
    """Fetch user data from the backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/user/{email}")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching user data: {e}")
    return None


def show_dashboard():
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
        .st-emotion-cache-1r6slb0 {
            flex-direction: column;
            height: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    # --- Main Content ---
    st.markdown('<h1 class="main-header">Dashboard</h1>', unsafe_allow_html=True)
    
    user = get_user_from_api(st.session_state.user_email)
    
    if not user:
        st.error("Could not load user profile. Please try logging in again.")
        st.stop()

    st.write(f"### Welcome back, {user['name']}! 👋")
    st.write(
        f"You are targeting the **{user['target_certification']}** certification."
    )

    st.write("---")

    # --- Progress Metrics ---
    st.write("## 📊 Your Progress")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Study Time", "12h 45m", "2h 15m")
    col2.metric("Practice Tests Taken", "8", "1")
    col3.metric("Average Score", "85%", "5%")

    st.progress(75, text="Overall Progress")

    st.write("---")

    # --- Learning Resources ---
    st.write("## 📚 Learning Resources")
    st.info(
        "Here are some recommended resources for your certification:",
        icon="ℹ️",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.video("https://www.youtube.com/watch?v=ulprqHHWlng")
        st.markdown(
            '[AWS Certified SAA | A Practical Guide](https://www.youtube.com/watch?v=ulprqHHWlng)'
        )

    with col2:
        st.video("https://www.youtube.com/watch?v=Ia-UEYYR44s")
        st.markdown(
            '[AWS Certified SAA | Full Course](https://www.youtube.com/watch?v=Ia-UEYYR44s)'
        )

    st.write("---")

    # --- AI Chatbot ---
    st.write("## 🤖 AI Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything about your certification!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking..."):
                # Call backend API
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/chat",
                        json={
                            "user_id": user["id"],
                            "question": prompt,
                            "context": user.get("target_certification", "")
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        response_text = data.get("answer", "Sorry, I couldn't generate a response.")
                    else:
                        response_text = "Sorry, there was an error processing your question. Please try again."
                except requests.exceptions.RequestException as e:
                    print(f"Error calling backend: {e}")
                    response_text = "Sorry, I'm having trouble connecting to the AI service. Please try again later."

                full_response = ""
                message_placeholder = st.empty()
                # Use splitlines to preserve paragraph breaks
                for line in response_text.splitlines(keepends=True):
                    for chunk in line.split(" "):
                        full_response += chunk + " "
                        time.sleep(0.01)
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
        