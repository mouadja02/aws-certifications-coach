# User Dashboard (after successful login)

import streamlit as st
import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import get_user_by_email, save_chat_message
from ai_service import AIService

def get_user_from_db(email: str):
    """Fetch user data from Snowflake"""
    try:
        user = get_user_by_email(email)
        if user:
            # Convert Snowflake column names to lowercase for compatibility
            return {
                'id': user['ID'],
                'name': user['NAME'],
                'email': user['EMAIL'],
                'age': user['AGE'],
                'target_certification': user['TARGET_CERTIFICATION']
            }
    except Exception as e:
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
    
    user = get_user_from_db(st.session_state.user_email)
    
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
                # Generate AI response with certification context
                ai_service = AIService()
                try:
                    response_text = ai_service.answer_question(
                        user["id"], 
                        prompt,
                        context=user["target_certification"]
                    )
                    # Save to Snowflake
                    save_chat_message(user["id"], prompt, response_text)
                except Exception as e:
                    print(f"Error generating response: {e}")
                    response_text = "Sorry, I'm having trouble processing your question. Please try again later."

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
        