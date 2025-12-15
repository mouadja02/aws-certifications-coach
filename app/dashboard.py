"""
AWS Certifications Coach - Multi-Section Learning Dashboard
Features: AI Chat, Practice Exams, Study Tricks, Answer Evaluation, Q&A Knowledge Base
"""

import streamlit as st
import time
import sys
import os
import json
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import logging
import traceback

# Configure logging with detailed format including line numbers and traceback
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(__file__))

from database import get_user_by_email, save_chat_message, get_user_progress, get_activity_log, get_qa_data, increment_user_streak, log_activity
from ai_service import AIService
from valkey_client import get_valkey_client
from styles import get_custom_css, create_metric_card, create_progress_ring, create_badge, get_confetti_animation
from components import show_confetti, show_toast, show_loading_skeleton

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_user_from_db(email: str):
    """Fetch user data from Snowflake with caching"""
    try:
        user = get_user_by_email(email)
        if user:
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

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_cached_user_progress(user_id: int):
    """Get user progress with caching"""
    return get_user_progress(user_id)

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_cached_activity_log(user_id: int):
    """Get activity log with caching"""
    return get_activity_log(user_id)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_qa_data(category: str, difficulty: str, certification: str):
    """Get Q&A data with caching"""
    return get_qa_data(category, difficulty, certification)


def show_ai_chat(user):
    """Premium AI Chat Interface with stunning visuals"""
    
    # Header
    st.markdown(f'''
    <div class="glass-container" style="text-align: center; padding: 2rem;">
        <div style="font-size: 4rem; margin-bottom: 0.5rem;">🤖</div>
        <h1 style="margin-bottom: 0.5rem;">AI Study Coach</h1>
        <p style="color: #6b7280; font-size: 1.1rem;">
            Your personal AI assistant for <strong style="color: #FF9900;">{user['target_certification']}</strong>
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.write("")
    
    # Quick prompts
    st.markdown('<h3 style="margin: 1rem 0;">💡 Quick Questions</h3>', unsafe_allow_html=True)
    
    quick_prompts = [
        "What are the key services I need to know?",
        "Give me a study plan for this week",
        "Explain the Well-Architected Framework",
        "What are common exam traps to avoid?"
    ]
    
    col1, col2 = st.columns(2)
    for i, prompt in enumerate(quick_prompts):
        with col1 if i % 2 == 0 else col2:
            if st.button(f"💬 {prompt}", key=f"quick_{i}", use_container_width=True):
                # Simulate clicking the prompt
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()
    
    st.write("")
    st.markdown("---")
    st.write("")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"👋 Hi {user['name']}! I'm your AI study coach for {user['target_certification']}. How can I help you today?"
        }]
    
    # Chat container
    st.markdown('<div style="max-height: 600px; overflow-y: auto; padding: 1rem 0;">', unsafe_allow_html=True)
    
    # Display chat history with premium styling
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'''
            <div class="glass-card" style="
                margin-left: 20%;
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                border-left: 4px solid #667eea;
            ">
                <div style="display: flex; align-items: start; gap: 1rem;">
                    <div style="
                        width: 40px;
                        height: 40px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.2rem;
                        flex-shrink: 0;
                    ">
                        👤
                    </div>
                    <div style="flex: 1; padding-top: 0.5rem;">
                        <div style="font-weight: 700; color: #232F3E; margin-bottom: 0.5rem;">You</div>
                        <div style="color: #4b5563; line-height: 1.6;">{message["content"]}</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="glass-card" style="
                margin-right: 20%;
                background: linear-gradient(135deg, rgba(255, 153, 0, 0.05) 0%, rgba(236, 114, 17, 0.05) 100%);
                border-left: 4px solid #FF9900;
            ">
                <div style="display: flex; align-items: start; gap: 1rem;">
                    <div style="
                        width: 40px;
                        height: 40px;
                        background: linear-gradient(135deg, #FF9900 0%, #EC7211 100%);
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.2rem;
                        flex-shrink: 0;
                    ">
                        🤖
                    </div>
                    <div style="flex: 1; padding-top: 0.5rem;">
                        <div style="font-weight: 700; color: #FF9900; margin-bottom: 0.5rem;">AI Coach</div>
                        <div style="color: #4b5563; line-height: 1.6;">{message["content"]}</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        st.write("")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.write("")
    prompt = st.chat_input("💬 Ask me anything about your certification...")
    
    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate AI response
        ai_service = AIService()
        try:
            with st.spinner("🧠 AI is thinking..."):
                response_text = ai_service.answer_question(
                    user["id"],
                    prompt,
                    context=user["target_certification"]
                )
                save_chat_message(user["id"], prompt, response_text)

                # Log activity
                log_activity(user["id"], 'chat', f"Asked: {prompt[:50]}...")

                # Clear cache to update recent activity
                st.cache_data.clear()
        except Exception as e:
            print(f"Error: {e}")
            response_text = "Sorry, I'm having trouble processing your question. Please try again."

        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()
    
    # Chat tips
    st.write("")
    with st.expander("💡 Tips for Better Answers"):
        st.markdown('''
        <div class="glass-card">
            <h4 style="color: #FF9900; margin-bottom: 1rem;">Get the most out of your AI coach:</h4>
            <ul style="color: #6b7280; line-height: 2;">
                <li><strong>Be specific:</strong> Ask about particular services or concepts</li>
                <li><strong>Request examples:</strong> "Give me an example of when to use..."</li>
                <li><strong>Compare services:</strong> "What's the difference between X and Y?"</li>
                <li><strong>Ask for strategies:</strong> "What's the best way to remember..."</li>
                <li><strong>Clarify doubts:</strong> "I don't understand how X works, explain it simply"</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)


def show_practice_exam(user):
    """Premium Practice Exam Interface with immersive experience"""
    
    # Header
    st.markdown(f'''
    <div class="glass-container" style="text-align: center; padding: 2rem;">
        <div style="font-size: 4rem; margin-bottom: 0.5rem;">📝</div>
        <h1 style="margin-bottom: 0.5rem;">Practice Exams</h1>
        <p style="color: #6b7280; font-size: 1.1rem;">
            Prepare for <strong style="color: #FF9900;">{user["target_certification"]}</strong> with AI-generated questions
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.write("")
    
    # Initialize session state variables
    if "exam_session_id" not in st.session_state:
        st.session_state.exam_session_id = None
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "question_number" not in st.session_state:
        st.session_state.question_number = 0
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 10
    if "exam_score" not in st.session_state:
        st.session_state.exam_score = 0
    if "exam_results" not in st.session_state:
        st.session_state.exam_results = []
    if "show_explanation" not in st.session_state:
        st.session_state.show_explanation = False
    if "current_answer_result" not in st.session_state:
        st.session_state.current_answer_result = None
    if "exam_finished" not in st.session_state:
        st.session_state.exam_finished = False
    
    # Get Valkey client
    valkey = get_valkey_client()
    ai_service = AIService()
    
    # Initialize done flag for cleanup logic
    done = False
    
    # If no exam session is active, show exam setup
    if st.session_state.exam_session_id is None:
        done = False
        st.markdown('''
        <div class="glass-card" style="text-align: center; padding: 2rem; margin-bottom: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚙️</div>
            <h3 style="color: #232F3E; margin-bottom: 1rem;">Configure Your Exam</h3>
            <p style="color: #6b7280;">Customize your practice exam to match your study goals</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Exam settings with premium cards
        col1, col2, col3 = st.columns(3, gap="large")
        
        with col1:
            st.markdown('''
            <div class="glass-card" style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔢</div>
                <div style="font-weight: 700; color: #232F3E; margin-bottom: 0.5rem;">Questions</div>
            </div>
            ''', unsafe_allow_html=True)
            num_questions = st.selectbox("Number of Questions", [2, 5, 10, 15, 20, 30, 40, 50], index=1, key="num_q", label_visibility="collapsed")
        
        with col2:
            st.markdown('''
            <div class="glass-card" style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
                <div style="font-weight: 700; color: #232F3E; margin-bottom: 0.5rem;">Difficulty</div>
            </div>
            ''', unsafe_allow_html=True)
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=1, key="diff", label_visibility="collapsed")
        
        with col3:
            st.markdown('''
            <div class="glass-card" style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📚</div>
                <div style="font-weight: 700; color: #232F3E; margin-bottom: 0.5rem;">Topic</div>
            </div>
            ''', unsafe_allow_html=True)
            topic = st.selectbox("Exam Topic", [
                "All Topics",
                "Storage Services",
                "Compute Services", 
                "Networking & Content Delivery",
                "Database Services",
                "Security, Identity & Compliance",
                "Management & Governance",
                "Application Integration",
                "Analytics & Big Data",
                "Machine Learning & AI",
                "Developer Tools & DevOps",
                "Migration & Transfer",
                "Cost Management",
                "Serverless Computing",
                "Containers",
                "High Availability & Fault Tolerance",
                "Well-Architected Framework",
                "Hybrid Cloud & Edge"
            ], key="topic", label_visibility="collapsed")
        
        st.write("")
        
        # Estimated time
        estimated_time = num_questions * 1.5
        st.markdown(f'''
        <div class="glass-card" style="text-align: center; padding: 1.5rem;">
            <div style="display: flex; justify-content: center; align-items: center; gap: 2rem;">
                <div>
                    <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 0.25rem;">Estimated Time</div>
                    <div style="color: #FF9900; font-size: 1.5rem; font-weight: 800;">~{int(estimated_time)} min</div>
                </div>
                <div>
                    <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 0.25rem;">Total Questions</div>
                    <div style="color: #FF9900; font-size: 1.5rem; font-weight: 800;">{num_questions}</div>
                </div>
                <div>
                    <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 0.25rem;">Difficulty</div>
                    <div style="color: #FF9900; font-size: 1.5rem; font-weight: 800;">{difficulty}</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.write("")
        
        # Start Exam button (only show when no exam is active)
        if st.button("🚀 Start Exam", type="primary", use_container_width=True):
            # Generate unique session ID
            session_id = f"exam_{user['id']}_{int(datetime.now().timestamp())}"
            
            # Clear any existing queue
            valkey.clear_queue(session_id)
            
            # Create session data
            session_data = {
                "session_id": session_id,
                "user_id": user["id"],
                "certification": user["target_certification"],
                "difficulty": difficulty.lower(),
                "topic": topic,
                "total_questions": num_questions,
                "score": 0,
                "answers": [],
                "started_at": datetime.now().isoformat()
            }
            
            # Save session to Valkey
            if valkey.save_session(session_id, session_data):
                # Trigger background question generation
                success = ai_service.trigger_exam_generation(
                    session_id=session_id,
                    user_id=user["id"],
                    certification=user["target_certification"],
                    difficulty=difficulty.lower(),
                    total_questions=num_questions,
                    topic=topic
                )
                
                if success:
                    st.info("⏳ Generating first question...")
                    
                    # Wait for first question (with timeout)
                    max_wait = 30  # 30 seconds max
                    wait_interval = 1  # Check every 1 second
                    waited = 0
                    
                    question_data = None
                    while waited < max_wait:
                        question_data = valkey.pop_question(session_id)
                        if question_data:
                            break
                        time.sleep(wait_interval)
                        waited += wait_interval
                    
                    if question_data:
                        # Success! Start exam
                        st.session_state.exam_session_id = session_id
                        st.session_state.current_question = question_data
                        st.session_state.question_number = 1
                        st.session_state.total_questions = num_questions
                        st.session_state.exam_score = 0
                        st.session_state.exam_results = []
                        st.session_state.show_explanation = False
                        st.session_state.current_answer_result = None
                        st.success("✅ Exam started!")
                        st.rerun()
                    else:
                        st.error("❌ Timeout waiting for first question. Please try again.")
                        valkey.delete_session(session_id)
                else:
                    st.error("❌ Could not start exam. Check n8n webhook configuration.")
                    valkey.delete_session(session_id)
            else:
                st.error("❌ Could not connect to Valkey. Check configuration.")
    
    # If exam session is active, show current question
    elif st.session_state.exam_session_id is not None:
        session_id = st.session_state.exam_session_id
        
        # Exam header with progress
        progress = st.session_state.question_number / st.session_state.total_questions
        queue_length = valkey.get_queue_length(session_id)
        
        st.markdown(f'''
        <div class="glass-card" style="padding: 1.5rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div>
                    <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.25rem;">Progress</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; font-weight: 800; color: #FF9900;">
                        Question {st.session_state.question_number} / {st.session_state.total_questions}
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
                
        # Animated progress bar
        st.progress(progress)
        
        st.write("")
        
        # Display current question with premium styling
        if st.session_state.current_question and not done:
            question_data = st.session_state.current_question
            
            # Question card
            st.markdown(f'''
            <div class="glass-card" style="padding: 2rem; border-left: 4px solid #FF9900;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="
                        width: 50px;
                        height: 50px;
                        background: linear-gradient(135deg, #FF9900 0%, #EC7211 100%);
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.5rem;
                        font-weight: 800;
                        color: white;
                        flex-shrink: 0;
                    ">
                        {st.session_state.question_number}
                    </div>
                    <div style="flex: 1;">
                        <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.25rem;">Question</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #232F3E; line-height: 1.6;">
                            {question_data.get("question", "")}
                        </div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            st.write("")
            
            # Determine if multiple choice or single choice
            question_type = question_data.get("type", "single")
            options = question_data.get("options", [])
            
            # If not showing explanation, show answer options
            if not st.session_state.show_explanation and not done:
                if question_type == "multiple":
                    st.info("ℹ️ Select ALL that apply (multiple correct answers)")
                    user_answers = []
                    for option in options:
                        if st.checkbox(option, key=f"option_{option}"):
                            user_answers.append(option)
                    
                    st.write("")
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button("✅ Check Answer", type="primary", use_container_width=True, disabled=len(user_answers) == 0):
                            # Check answer locally (instant)
                            result = ai_service.check_answer(
                                user_answer=user_answers,
                                correct_answer=question_data.get("correct_answer"),
                                question_text=question_data.get("question"),
                                explanation=question_data.get("explanation", "No explanation available")
                            )
                            
                            st.session_state.current_answer_result = result
                            st.session_state.show_explanation = True
                            
                            # Update score
                            if result.get("is_correct", False):
                                st.session_state.exam_score += 1
                            
                            # Save result
                            st.session_state.exam_results.append({
                                "question": question_data.get("question"),
                                "user_answer": user_answers,
                                "correct_answer": result.get("correct_answer"),
                                "is_correct": result.get("is_correct", False),
                                "explanation": result.get("explanation", "")
                            })
                            
                            # Update session in Valkey
                            valkey.update_session(session_id, {
                                "score": st.session_state.exam_score,
                                "last_question": st.session_state.question_number
                            })
                            
                            st.rerun()
                else:
                    # Single choice question
                    user_answer = st.radio(
                        "Select your answer:",
                        options,
                        key="single_answer",
                        index=None
                    )
                    
                    st.write("")
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button("✅ Check Answer", type="primary", use_container_width=True, disabled=user_answer is None):
                            # Check answer locally (instant)
                            result = ai_service.check_answer(
                                user_answer=user_answer,
                                correct_answer=question_data.get("correct_answer"),
                                question_text=question_data.get("question"),
                                explanation=question_data.get("explanation", "No explanation available")
                            )
                            
                            st.session_state.current_answer_result = result
                            st.session_state.show_explanation = True
                            
                            # Update score
                            if result.get("is_correct", False):
                                st.session_state.exam_score += 1
                            
                            # Save result
                            st.session_state.exam_results.append({
                                "question": question_data.get("question"),
                                "user_answer": user_answer,
                                "correct_answer": result.get("correct_answer"),
                                "is_correct": result.get("is_correct", False),
                                "explanation": result.get("explanation", "")
                            })
                            
                            # Update session in Valkey
                            valkey.update_session(session_id, {
                                "score": st.session_state.exam_score,
                                "last_question": st.session_state.question_number
                            })
                            
                            st.rerun()
        
            # Show explanation after answer is checked
            else:
                result = st.session_state.current_answer_result
                
                if result and not done:
                    # Overall result header
                    if result.get("is_correct", False):
                        st.success("✅ **Correct!** Well done!")
                    else:
                        st.error("❌ **Incorrect** - Review the correct answer below")
                    
                    st.write("")
                    
                    # Helper function to extract letter from option
                    def extract_letter(text):
                        """Extract letter (A, B, C, D) from option text"""
                        text_str = str(text).strip().upper()
                        if ')' in text_str:
                            return text_str.split(')')[0].strip()
                        return text_str[0] if text_str else ''
                    
                    # Get user's answer and correct answer
                    user_answer = st.session_state.exam_results[-1].get("user_answer")
                    correct_answer = result.get("correct_answer")
                    
                    # Convert to lists for uniform processing
                    if not isinstance(user_answer, list):
                        user_answer = [user_answer]
                    if not isinstance(correct_answer, list):
                        correct_answer = [correct_answer]
                    
                    # Extract letters from answers for comparison
                    user_letters = [extract_letter(ans) for ans in user_answer]
                    correct_letters = [extract_letter(ans) for ans in correct_answer]
                    
                    # Display all options with visual feedback
                    st.markdown("**Answer Review:**")
                    for option in options:
                        option_letter = extract_letter(option)
                        is_correct_option = option_letter in correct_letters
                        is_user_selection = option_letter in user_letters
                        
                        if is_correct_option and is_user_selection:
                            # User selected correct answer
                            st.markdown(f'''
                            <div style="
                                background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%);
                                border-left: 4px solid #10b981;
                                padding: 1rem;
                                margin-bottom: 0.5rem;
                                border-radius: 0.5rem;
                                display: flex;
                                align-items: center;
                                gap: 0.5rem;
                            ">
                                <span style="font-size: 1.5rem;">✅</span>
                                <span style="color: #059669; font-weight: 600;">{option}</span>
                                <span style="color: #059669; margin-left: auto; font-size: 0.875rem;">(Your answer - Correct!)</span>
                            </div>
                            ''', unsafe_allow_html=True)
                        elif is_correct_option and not is_user_selection:
                            # Correct answer but user didn't select it
                            st.markdown(f'''
                            <div style="
                                background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.03) 100%);
                                border-left: 4px solid #10b981;
                                padding: 1rem;
                                margin-bottom: 0.5rem;
                                border-radius: 0.5rem;
                                display: flex;
                                align-items: center;
                                gap: 0.5rem;
                            ">
                                <span style="font-size: 1.5rem;">✅</span>
                                <span style="color: #059669; font-weight: 600;">{option}</span>
                                <span style="color: #6b7280; margin-left: auto; font-size: 0.875rem;">(Correct answer)</span>
                            </div>
                            ''', unsafe_allow_html=True)
                        elif not is_correct_option and is_user_selection:
                            # User selected wrong answer
                            st.markdown(f'''
                            <div style="
                                background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%);
                                border-left: 4px solid #ef4444;
                                padding: 1rem;
                                margin-bottom: 0.5rem;
                                border-radius: 0.5rem;
                                display: flex;
                                align-items: center;
                                gap: 0.5rem;
                            ">
                                <span style="font-size: 1.5rem;">❌</span>
                                <span style="color: #dc2626; font-weight: 600;">{option}</span>
                                <span style="color: #dc2626; margin-left: auto; font-size: 0.875rem;">(Your answer - Incorrect)</span>
                            </div>
                            ''', unsafe_allow_html=True)
                        else:
                            # Not selected and not correct
                            st.markdown(f'''
                            <div style="
                                background: #f9fafb;
                                border-left: 4px solid #e5e7eb;
                                padding: 1rem;
                                margin-bottom: 0.5rem;
                                border-radius: 0.5rem;
                                display: flex;
                                align-items: center;
                                gap: 0.5rem;
                            ">
                                <span style="font-size: 1.5rem; opacity: 0.3;">⚪</span>
                                <span style="color: #6b7280;">{option}</span>
                            </div>
                            ''', unsafe_allow_html=True)
                    
                    st.write("")
                    
                    # Show explanation in a nice card
                    st.markdown("**💡 Explanation:**")
                    st.markdown(f'''
                    <div style="
                        background: linear-gradient(135deg, rgba(255, 153, 0, 0.1) 0%, rgba(255, 153, 0, 0.03) 100%);
                        border-left: 4px solid #FF9900;
                        padding: 1.5rem;
                        border-radius: 0.5rem;
                        color: #4b5563;
                        line-height: 1.7;
                        margin-bottom: 1rem;
                    ">
                        {result.get("explanation", "No explanation available")}
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Show reference link if available
                    if question_data.get("reference"):
                        st.info(f"📖 **Reference:** {question_data.get('reference')}")
                    
                    st.write("---")
                    
                    # Next question or finish
                    if st.session_state.question_number < st.session_state.total_questions and not done:
                        if st.button("➡️ Next Question", type="primary", use_container_width=True):
                            # Get next question from queue (instant!)
                            next_question = valkey.pop_question(session_id)
                            
                            if next_question:
                                st.session_state.current_question = next_question
                                st.session_state.question_number += 1
                                st.session_state.show_explanation = False
                                st.session_state.current_answer_result = None
                                st.rerun()
                            else:
                                st.warning("⏳ Waiting for next question... (generating in background)")
                                time.sleep(2)
                                st.rerun()
                    else:
                        # Last question - show finish button if not already finished
                        if not st.session_state.exam_finished:
                            if st.button("🏁 Finish Exam", type="primary", use_container_width=True):
                                # Calculate final score
                                score_percentage = (st.session_state.exam_score / st.session_state.total_questions) * 100

                                # Save to database BEFORE clearing anything
                                try:
                                    from database import execute_update, update_user_progress
                                    session_data = valkey.get_session(session_id)
                                    if session_data:
                                        query = f"""
                                        INSERT INTO exam_sessions (
                                            session_id, user_id, certification, difficulty, topic,
                                            total_questions, correct_answers, incorrect_answers,
                                            percentage, passed, started_at, completed_at, duration_minutes
                                        ) VALUES (
                                            '{session_id}',
                                            {user['id']},
                                            '{user['target_certification']}',
                                            '{session_data.get('difficulty', 'medium')}',
                                            '{session_data.get('topic', 'All Topics')}',
                                            {st.session_state.total_questions},
                                            {st.session_state.exam_score},
                                            {st.session_state.total_questions - st.session_state.exam_score},
                                            {score_percentage},
                                            {str(score_percentage >= 70).upper()},
                                            '{session_data.get('started_at')}',
                                            '{datetime.now().isoformat()}',
                                            {int((datetime.now() - datetime.fromisoformat(session_data.get('started_at'))).seconds / 60)}
                                        )
                                        """
                                        execute_update(query)

                                        # Update user progress and streak
                                        increment_user_streak(user['id'])

                                        # Log activity
                                        log_activity(
                                            user['id'],
                                            'exam',
                                            f"Completed {session_data.get('topic', 'All Topics')} exam with {score_percentage:.0f}% score"
                                        )

                                        # Update practice tests count and average score
                                        current_progress = get_user_progress(user['id'])
                                        if current_progress:
                                            tests_taken = current_progress.get('PRACTICE_TESTS_TAKEN', 0) + 1
                                            current_avg = current_progress.get('AVERAGE_SCORE', 0)
                                            new_avg = ((current_avg * (tests_taken - 1)) + score_percentage) / tests_taken

                                            update_user_progress(user['id'], {
                                                'practice_tests_taken': tests_taken,
                                                'average_score': int(new_avg),
                                                'total_questions_answered': current_progress.get('TOTAL_QUESTIONS_ANSWERED', 0) + st.session_state.total_questions,
                                                'correct_answers': current_progress.get('CORRECT_ANSWERS', 0) + st.session_state.exam_score
                                            })

                                        # Clear cache to show updated stats
                                        st.cache_data.clear()
                                except Exception as e:
                                    print(f"Could not save results to database: {e}")
                                    
                                # Clean up Valkey
                                try:
                                    valkey.delete_session(session_id)
                                except Exception as e:
                                    print(f"Could not delete Valkey session: {e}")
                                
                                # Mark as finished
                                st.session_state.exam_finished = True
                                st.rerun()
        
        # Show exam results if finished
        if st.session_state.exam_finished:
            # Calculate final score for celebration message
            score_percentage_display = (st.session_state.exam_score / st.session_state.total_questions) * 100

            # Show confetti celebration
            show_confetti()

            # Show personalized message based on score
            if score_percentage_display >= 90:
                congrats_msg = "Outstanding! You're exam-ready! 🌟"
                color = "#10b981"
            elif score_percentage_display >= 70:
                congrats_msg = "Great job! You passed! Keep it up! 👍"
                color = "#10b981"
            elif score_percentage_display >= 50:
                congrats_msg = "Good effort! Keep practicing! 💪"
                color = "#f59e0b"
            else:
                congrats_msg = "Keep learning! You'll get there! 📚"
                color = "#ef4444"

            st.markdown(f'''
            <div class="glass-card" style="text-align: center; padding: 3rem; background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(255, 153, 0, 0.1) 100%);">
                <div style="font-size: 5rem; margin-bottom: 1rem; animation: bounce 1s infinite;">🎉</div>
                <h1 style="color: {color}; margin-bottom: 0.5rem;">Exam Complete!</h1>
                <p style="color: #6b7280; font-size: 1.2rem;">{congrats_msg}</p>
            </div>
            ''', unsafe_allow_html=True)
            st.write("")
            
            # Calculate final score
            score_percentage = (st.session_state.exam_score / st.session_state.total_questions) * 100
            
            # Score display with premium styling
            pass_status = score_percentage >= 70
            status_color = "#10b981" if pass_status else "#ef4444"
            status_text = "PASSED ✅" if pass_status else "NEEDS IMPROVEMENT 📈"
            
            st.markdown(f'''
            <div class="glass-card" style="text-align: center; padding: 2rem; border: 3px solid {status_color};">
                <div style="font-size: 1rem; color: #6b7280; margin-bottom: 0.5rem;">FINAL SCORE</div>
                <div style="font-size: 5rem; font-weight: 800; color: {status_color};">{score_percentage:.0f}%</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {status_color}; margin-top: 1rem;">{status_text}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            st.write("")
            
            # Detailed stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(create_metric_card("✅", "Correct", f"{st.session_state.exam_score}", None), unsafe_allow_html=True)
            with col2:
                st.markdown(create_metric_card("❌", "Incorrect", f"{st.session_state.total_questions - st.session_state.exam_score}", None), unsafe_allow_html=True)
            with col3:
                st.markdown(create_metric_card("📊", "Total", f"{st.session_state.total_questions}", None), unsafe_allow_html=True)
            
            st.write("")
            st.markdown('<h2 style="margin: 2rem 0 1rem 0;">📊 Detailed Review</h2>', unsafe_allow_html=True)
            
            for i, result in enumerate(st.session_state.exam_results, 1):
                status_icon = "✅" if result["is_correct"] else "❌"
                status_color = "#10b981" if result["is_correct"] else "#ef4444"
                status_text = "CORRECT" if result["is_correct"] else "INCORRECT"
                
                with st.expander(f"{status_icon} Question {i} - {result['question'][:60]}..."):
                    # Status badge
                    st.markdown(f'''
                    <div style="display: inline-block; background: {status_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; margin-bottom: 1rem;">
                        {status_text}
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Question
                    st.markdown("**Question:**")
                    st.write(result['question'])
                    st.write("")
                    
                    # Answers side by side
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Your Answer:**")
                        user_ans = result['user_answer']
                        if isinstance(user_ans, list):
                            for ans in user_ans:
                                st.write(f"- {ans}")
                        else:
                            st.write(user_ans)
                    
                    with col2:
                        st.markdown("**Correct Answer:**")
                        correct_ans = result['correct_answer']
                        if isinstance(correct_ans, list):
                            for ans in correct_ans:
                                st.write(f"- {ans}")
                        else:
                            st.write(correct_ans)
                    
                    st.write("")
                    st.markdown("**💡 Explanation:**")
                    st.info(result['explanation'])
            
            st.write("---")
            if st.button("🔄 Take Another Exam", use_container_width=True):
                # Reset all exam session state 
                print("Taking another exam")
                done = True
        
        # Show Quit Exam button only during active exam (not when results are shown)
        elif st.session_state.exam_session_id and not st.session_state.exam_finished:
            st.write("")
            if st.button("❌ Quit Exam", use_container_width=True):
                print("Quitting exam early")
                done = True
        
        # Cleanup logic (executes when done flag is set)
        if done:
            # Clean up - notify n8n to stop generating questions
            try:
                data = {
                    "action": "quit_session",
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
                result = ai_service._call_n8n_webhook(ai_service.exam_webhook, data, async_call=False)
                if result and result.get("error"):
                    print(f"Warning: Could not notify n8n: {result.get('error')}")
            except Exception as e:
                print(f"Warning: Failed to notify n8n about session cleanup: {e}")
            
            # Clean up Valkey session
            try:
                valkey.delete_session(session_id)
            except Exception as e:
                print(f"Warning: Could not delete Valkey session: {e}")
            
            # Reset all session state
            st.session_state.exam_session_id = None
            st.session_state.current_question = None
            st.session_state.question_number = 0
            st.session_state.exam_score = 0
            st.session_state.exam_results = []
            st.session_state.show_explanation = False
            st.session_state.current_answer_result = None
            st.session_state.exam_finished = False
            st.rerun()


def show_study_tricks(user):
    """Premium Study Tricks Section with interactive cards"""
    
    # Header
    st.markdown(f'''
    <div class="glass-container" style="text-align: center; padding: 2rem;">
        <div style="font-size: 4rem; margin-bottom: 0.5rem;">🧠</div>
        <h1 style="margin-bottom: 0.5rem;">Study Tricks & Memory Techniques</h1>
        <p style="color: #6b7280; font-size: 1.1rem;">
            Master <strong style="color: #FF9900;">{user["target_certification"]}</strong> with proven memory techniques
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.write("")
    
    # Topic selection with premium styling
    st.markdown('''
    <div class="glass-card" style="padding: 1.5rem;">
        <h3 style="color: #232F3E; margin-bottom: 1rem;">🎯 What would you like to remember?</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("", placeholder="e.g., S3 Storage Classes, EC2 Instance Types, VPC Components...", label_visibility="collapsed")
    with col2:
        generate_btn = st.button("✨ Generate Tricks", use_container_width=True, type="primary")
    
    if generate_btn and topic:
        with st.spinner("🔍 Creating memory techniques..."):
            ai_service = AIService()
            try:
                tricks = ai_service.get_study_tricks(
                    user["id"],
                    user["target_certification"],
                    topic
                )
                st.session_state.current_tricks = tricks
                st.rerun()
            except Exception as e:
                st.error(f"Error generating tricks: {e}")
    
    # Display tricks with premium cards
    if "current_tricks" in st.session_state and st.session_state.current_tricks:
        tricks = st.session_state.current_tricks
        
        st.markdown('''
        <div class="glass-card" style="text-align: center; padding: 1.5rem; margin: 1.5rem 0;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #10b981;">Memory Tricks Generated!</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Display each trick type in premium cards
        if tricks.get("mnemonic"):
            st.markdown(f'''
            <div class="glass-card" style="border-left: 4px solid #667eea; padding: 2rem;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="font-size: 3rem;">🔤</div>
                    <h3 style="color: #232F3E; margin: 0;">Mnemonic Device</h3>
                </div>
                <div style="background: rgba(102, 126, 234, 0.1); padding: 1.5rem; border-radius: 0.75rem; color: #4b5563; line-height: 1.8; font-size: 1.05rem;">
                    {tricks["mnemonic"]}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            st.write("")
        
        if tricks.get("analogy"):
            st.markdown(f'''
            <div class="glass-card" style="border-left: 4px solid #10b981; padding: 2rem;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="font-size: 3rem;">🔗</div>
                    <h3 style="color: #232F3E; margin: 0;">Real-World Analogy</h3>
                </div>
                <div style="background: rgba(16, 185, 129, 0.1); padding: 1.5rem; border-radius: 0.75rem; color: #4b5563; line-height: 1.8; font-size: 1.05rem;">
                    {tricks["analogy"]}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            st.write("")
        
        if tricks.get("visualization"):
            st.markdown(f'''
            <div class="glass-card" style="border-left: 4px solid #f59e0b; padding: 2rem;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="font-size: 3rem;">🎨</div>
                    <h3 style="color: #232F3E; margin: 0;">Visualization Technique</h3>
                </div>
                <div style="background: rgba(245, 158, 11, 0.1); padding: 1.5rem; border-radius: 0.75rem; color: #4b5563; line-height: 1.8; font-size: 1.05rem;">
                    {tricks["visualization"]}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            st.write("")
        
        if tricks.get("key_points"):
            st.markdown('''
            <div class="glass-card" style="border-left: 4px solid #FF9900; padding: 2rem;">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="font-size: 3rem;">🎯</div>
                    <h3 style="color: #232F3E; margin: 0;">Key Points to Remember</h3>
                </div>
                <div style="background: rgba(255, 153, 0, 0.1); padding: 1.5rem; border-radius: 0.75rem;">
            ''', unsafe_allow_html=True)
            for point in tricks["key_points"]:
                st.markdown(f'''
                <div style="display: flex; align-items: start; gap: 1rem; margin-bottom: 1rem;">
                    <div style="color: #FF9900; font-size: 1.5rem; line-height: 1;">✓</div>
                    <div style="color: #4b5563; line-height: 1.8; font-size: 1.05rem;">{point}</div>
                </div>
                ''', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Popular topics with premium grid
    st.write("")
    st.markdown('<h2 style="margin: 2rem 0 1rem 0;">🔥 Popular Topics</h2>', unsafe_allow_html=True)
    
    popular_topics = [
        ("S3 Storage Classes", "🗄️"),
        ("EC2 Instance Types", "💻"),
        ("VPC Components", "🌐"),
        ("IAM Policies", "🔐"),
        ("Lambda Limits", "⚡"),
        ("RDS vs DynamoDB", "🗃️"),
        ("CloudFormation vs Terraform", "🏗️"),
        ("Security Best Practices", "🛡️")
    ]
    
    cols = st.columns(4)
    for i, (topic, icon) in enumerate(popular_topics):
        with cols[i % 4]:
            st.markdown(f'''
            <div class="glass-card" style="text-align: center; padding: 1rem; cursor: pointer; transition: all 0.3s ease;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-size: 0.9rem; font-weight: 600; color: #232F3E;">{topic}</div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button(f"Learn {topic}", key=f"pop_{i}", use_container_width=True):
                st.session_state.selected_topic = topic
                st.rerun()


def show_answer_evaluation(user):
    """Premium Answer Evaluation with detailed feedback"""
    
    # Header
    st.markdown('''
    <div class="glass-container" style="text-align: center; padding: 2rem;">
        <div style="font-size: 4rem; margin-bottom: 0.5rem;">✍️</div>
        <h1 style="margin-bottom: 0.5rem;">Answer Evaluation</h1>
        <p style="color: #6b7280; font-size: 1.1rem;">
            Practice writing answers and get <strong style="color: #FF9900;">AI-powered feedback</strong>
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.write("")
    
    # Question input
    st.subheader("📋 Practice Question")
    question = st.text_area(
        "Enter a practice question or select from examples:",
        height=100,
        placeholder="e.g., Explain the difference between S3 and EBS"
    )
    
    # Example questions
    with st.expander("📚 Example Questions"):
        examples = [
            "Explain the difference between S3 and EBS",
            "What are the benefits of using AWS Lambda?",
            "Describe the shared responsibility model in AWS",
            "How does Auto Scaling work in AWS?",
            "What is the difference between Security Groups and NACLs?"
        ]
        for ex in examples:
            if st.button(f"Use: {ex}", key=f"ex_{ex}"):
                question = ex
                st.rerun()
    
    # Answer input
    st.subheader("✍️ Your Answer")
    user_answer = st.text_area(
        "Write your answer here:",
        height=200,
        placeholder="Write your answer in detail..."
    )
    
    # Evaluation criteria
    col1, col2 = st.columns(2)
    with col1:
        check_accuracy = st.checkbox("Check Technical Accuracy", value=True)
        check_completeness = st.checkbox("Check Completeness", value=True)
    with col2:
        check_clarity = st.checkbox("Check Clarity", value=True)
        check_examples = st.checkbox("Check for Examples", value=True)
    
    # Submit for evaluation
    if st.button("🔍 Evaluate My Answer", type="primary", use_container_width=True):
        if not question or not user_answer:
            st.warning("Please provide both a question and your answer!")
        else:
            with st.spinner("🤔 Evaluating your answer..."):
                ai_service = AIService()
                try:
                    evaluation = ai_service.evaluate_answer(
                        user["id"],
                        question,
                        user_answer,
                        user["target_certification"]
                    )
                    st.session_state.current_evaluation = evaluation
                    st.rerun()
                except Exception as e:
                    st.error(f"Error evaluating answer: {e}")
    
    # Display evaluation
    if "current_evaluation" in st.session_state and st.session_state.current_evaluation:
        eval_data = st.session_state.current_evaluation
        
        st.write("---")
        st.success("✅ Evaluation Complete!")
        
        # Score
        score = eval_data.get("score", 0)
        col1, col2, col3 = st.columns(3)
        col1.metric("Overall Score", f"{score}/100")
        col2.metric("Grade", eval_data.get("grade", "N/A"))
        col3.metric("Pass", "✅ Yes" if score >= 70 else "❌ No")
        
        # Detailed feedback
        st.subheader("📊 Detailed Feedback")
        
        if eval_data.get("strengths"):
            st.write("**✅ Strengths:**")
            for strength in eval_data["strengths"]:
                st.success(f"• {strength}")
        
        if eval_data.get("weaknesses"):
            st.write("**⚠️ Areas for Improvement:**")
            for weakness in eval_data["weaknesses"]:
                st.warning(f"• {weakness}")
        
        if eval_data.get("suggestions"):
            st.write("**💡 Suggestions:**")
            for suggestion in eval_data["suggestions"]:
                st.info(f"• {suggestion}")
        
        if eval_data.get("model_answer"):
            with st.expander("📝 Model Answer"):
                st.write(eval_data["model_answer"])


def show_qna_knowledge_base(user):
    """Premium Q&A Knowledge Base with search"""
    
    # Header
    st.markdown(f'''
    <div class="glass-container" style="text-align: center; padding: 2rem;">
        <div style="font-size: 4rem; margin-bottom: 0.5rem;">❓</div>
        <h1 style="margin-bottom: 0.5rem;">Q&A Knowledge Base</h1>
        <p style="color: #6b7280; font-size: 1.1rem;">
            Explore frequently asked questions for <strong style="color: #FF9900;">{user["target_certification"]}</strong>
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.write("")
    
    # Search
    
    # Categories
    categories = ["All", "Storage", "Compute", "Networking", "Security", "Database", "Monitoring"]
    difficulty = ["All", "Easy", "Medium", "Hard"]
    selected_category = st.selectbox("Select a category:", categories)
    selected_difficulty = st.selectbox("Select a difficulty:", difficulty)
    
    """
    SNOWFLAKE TABLE 
    aws_scenarios (
    scenario_id VARCHAR(255) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    title VARCHAR(500) NOT NULL,
    target_certification VARCHAR(500) NOT NULL,
    scenario_text TEXT NOT NULL,
    challenge_question TEXT NOT NULL,
    solution_answer TEXT NOT NULL,
    best_practices TEXT,
    aws_services_used VARIANT,
    architecture_considerations TEXT,
    cost_optimization_tips TEXT,
    security_considerations TEXT,
    reference_links VARIANT,
    tags VARIANT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    """
    # Use cached Q&A data for better performance
    qa_data = get_cached_qa_data(selected_category, selected_difficulty, user['target_certification'].split(" - ")[0])

    # Display Q&A
    if "qa_current_question" not in st.session_state:
        st.session_state.qa_current_question = 0
    
    # Display current question if we have data
    if qa_data and len(qa_data) > 0:
        current_question = st.session_state.qa_current_question
        
        if current_question < len(qa_data):
            st.write(f"**Scenario:** {qa_data[current_question].SCENARIO_TEXT}")
            st.write(f"**Challenge Question:** {qa_data[current_question].CHALLENGE_QUESTION}")

            # Fold this 
            with st.expander(f"Check the answer"):
                st.write(f"**Solution Answer:** {qa_data[current_question].SOLUTION_ANSWER}")
                st.write(f"**Best Practices:** {qa_data[current_question].BEST_PRACTICES}")
                st.write(f"**AWS Services Used:** {qa_data[current_question].AWS_SERVICES_USED}")
                st.write(f"**Architecture Considerations:** {qa_data[current_question].ARCHITECTURE_CONSIDERATIONS}")
                st.write(f"**Cost Optimization Tips:** {qa_data[current_question].COST_OPTIMIZATION_TIPS}")
                st.write(f"**Security Considerations:** {qa_data[current_question].SECURITY_CONSIDERATIONS}")

            # Navigation buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                if current_question > 0 and st.button("⬅️ Previous", key="qa_previous"):
                    st.session_state.qa_current_question -= 1
                    st.rerun()
            with col2:
                if current_question < len(qa_data) - 1 and st.button("Next ➡️", key="qa_next"):
                    st.session_state.qa_current_question += 1
                    st.rerun()
            
            # Show question counter
            st.info(f"Question {current_question + 1} of {len(qa_data)}")

def show_progress_dashboard(user):
    """Premium Progress Dashboard with stunning visuals and animations"""

    # Add refresh button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    progress_data = get_cached_user_progress(user["id"])
    activity_data = get_cached_activity_log(user["id"])

    # Welcome Banner with Time-based Greeting
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
        emoji = "🌅"
    elif current_hour < 18:
        greeting = "Good Afternoon"
        emoji = "☀️"
    else:
        greeting = "Good Evening"
        emoji = "🌙"
    
    st.markdown(f'''
    <div class="hero-container" style="padding: 2rem; text-align: left;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">{emoji} {greeting}, {user['name']}!</h1>
        <p style="font-size: 1.2rem; color: #6b7280; margin-bottom: 0;">
            Keep up the great work on <strong style="color: #FF9900;">{user['target_certification']}</strong>
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.write("")

    if progress_data:
        study_time_minutes = int(progress_data.get("STUDY_TIME_MINUTES", 0))
        practice_tests_taken = progress_data.get("PRACTICE_TESTS_TAKEN", 0)
        average_score = int(progress_data.get("AVERAGE_SCORE", 0))
        storage_topic_progress = int(progress_data.get("STORAGE_TOPIC_PROGRESS", 0))
        compute_topic_progress = int(progress_data.get("COMPUTE_TOPIC_PROGRESS", 0))
        networking_topic_progress = int(progress_data.get("NETWORKING_TOPIC_PROGRESS", 0))
        security_topic_progress = int(progress_data.get("SECURITY_TOPIC_PROGRESS", 0))
        database_topic_progress = int(progress_data.get("DATABASE_TOPIC_PROGRESS", 0))
        streak = progress_data.get("STREAK", 0)
        longest_streak = progress_data.get("LONGEST_STREAK", 0)
        xp = progress_data.get("XP", 0)
        accuracy_percentage = int(progress_data.get("ACCURACY_PERCENTAGE", 0))
        
        # Animated Metric Cards with tooltips
        col1, col2, col3, col4 = st.columns(4, gap="medium")

        with col1:
            st.markdown(create_metric_card("⏱️", "Study Time", f"{study_time_minutes}m", delta=None), unsafe_allow_html=True)
            st.caption("Total time spent studying and practicing")

        with col2:
            st.markdown(create_metric_card("📝", "Practice Exams", f"{practice_tests_taken}", delta=None), unsafe_allow_html=True)
            st.caption("Number of practice exams completed")

        with col3:
            st.markdown(create_metric_card("⭐", "Average Score", f"{average_score}%", delta=5 if average_score > 70 else -5), unsafe_allow_html=True)
            st.caption("Your average score across all exams")

        with col4:
            st.markdown(create_metric_card("🎯", "Accuracy", f"{accuracy_percentage}%", delta=3 if accuracy_percentage > 75 else -3), unsafe_allow_html=True)
            st.caption("Percentage of correct answers overall")
        
        st.write("")
        
        # Streak & XP Section
        st.markdown('<h2 style="margin: 2rem 0 1rem 0;">🔥 Your Learning Streak</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3, gap="large")
        
        with col1:
            st.markdown(f'''
            <div class="glass-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 0.5rem; animation: bounce 2s infinite;">🔥</div>
                <div style="font-size: 3rem; font-weight: 800; color: #FF9900;">{streak}</div>
                <div style="color: #6b7280; font-weight: 600; text-transform: uppercase;">Days Streak</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="glass-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 0.5rem;">🏆</div>
                <div style="font-size: 3rem; font-weight: 800; color: #FF9900;">{longest_streak}</div>
                <div style="color: #6b7280; font-weight: 600; text-transform: uppercase;">Best Streak</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'''
            <div class="glass-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 0.5rem;">⚡</div>
                <div style="font-size: 3rem; font-weight: 800; color: #FF9900;">{xp}</div>
                <div style="color: #6b7280; font-weight: 600; text-transform: uppercase;">Total XP</div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.write("")
        
        # Topic Mastery with Circular Progress
        st.markdown('<h2 style="margin: 2rem 0 1rem 0;">📈 Topic Mastery</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        topics = [
            ("Storage", storage_topic_progress, "🗄️"),
            ("Compute", compute_topic_progress, "💻"),
            ("Networking", networking_topic_progress, "🌐"),
            ("Security", security_topic_progress, "🔒"),
            ("Database", database_topic_progress, "🗃️"),
        ]
        
        for i, (topic, progress, icon) in enumerate(topics):
            with [col1, col2, col3, col4, col5][i]:
                st.markdown(f'''
                <div class="glass-card" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                    {create_progress_ring(progress, topic, 100)}
                </div>
                ''', unsafe_allow_html=True)
        
        st.write("")
        
        # Detailed Topic Progress Bars
        st.markdown('<h3 style="margin: 2rem 0 1rem 0;">Detailed Progress</h3>', unsafe_allow_html=True)
        
        for topic, progress, icon in topics:
            st.markdown(f'''
            <div class="glass-card" style="padding: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="font-weight: 700; color: #232F3E;">
                        {icon} {topic}
                    </div>
                    <div style="font-weight: 800; color: #FF9900; font-size: 1.2rem;">
                        {progress}%
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            st.progress(progress / 100)
            st.write("")
    else:
        st.markdown('''
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #6b7280;">No Progress Data Yet</h3>
            <p style="color: #9ca3af;">Start taking practice exams to see your progress here!</p>
        </div>
        ''', unsafe_allow_html=True)

    # Recent Activity
    st.write("")
    st.markdown('<h2 style="margin: 2rem 0 1rem 0;">📝 Recent Activity</h2>', unsafe_allow_html=True)

    if activity_data and len(activity_data) > 0:
        def get_relative_time(timestamp):
            """Convert timestamp to relative time string"""
            if not timestamp:
                return "Unknown time"

            now = datetime.now()
            diff = now - timestamp

            if diff.days > 0:
                if diff.days == 1:
                    return "1 day ago"
                elif diff.days < 7:
                    return f"{diff.days} days ago"
                elif diff.days < 30:
                    weeks = diff.days // 7
                    return f"{weeks} week{'s' if weeks > 1 else ''} ago"
                else:
                    months = diff.days // 30
                    return f"{months} month{'s' if months > 1 else ''} ago"
            elif diff.seconds >= 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif diff.seconds >= 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"

        for activity in activity_data:
            activity_type = activity.get('ACTIVITY', 'activity')
            description = activity.get('DESCRIPTION', 'No description')
            created_at = activity.get('CREATED_AT')

            icon_map = {"exam": "📝", "chat": "💬", "tricks": "🧠", "login": "🔐"}
            icon = icon_map.get(activity_type, "📌")

            relative_time = get_relative_time(created_at)

            st.markdown(f'''
            <div class="glass-card" style="padding: 1rem;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 2rem;">{icon}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 700; color: #232F3E; margin-bottom: 0.25rem;">
                            {description}
                        </div>
                        <div style="color: #9ca3af; font-size: 0.875rem;">
                            {relative_time}
                        </div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            st.write("")
    else:
        st.markdown('''
        <div class="glass-card" style="text-align: center; padding: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
            <p style="color: #6b7280;">No recent activity. Start your learning journey now!</p>
        </div>
        ''', unsafe_allow_html=True)

def show_dashboard():
    """Premium Dashboard with World-Class Navigation"""

    # Apply custom CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # Get user data with loading indicator
    with st.spinner("Loading your dashboard..."):
        user = get_user_from_db(st.session_state.user_email)
        if not user:
            st.error("Could not load user profile. Please try logging in again.")
            st.stop()
    
    # Get user progress for sidebar stats (cached)
    progress_data = get_cached_user_progress(user["id"])
    streak = progress_data.get("STREAK", 0) if progress_data else 0
    xp = progress_data.get("XP", 0) if progress_data else 0
    
    # Premium Sidebar
    with st.sidebar:
        # Logo and branding
        st.markdown('''
        <div style="text-align: center; margin-bottom: 2rem;">
            <img src="https://dev-artifacts-002.s3.us-east-1.amazonaws.com/aws-color.png" 
                 style="width: 120px; margin-bottom: 1rem;" alt="AWS Logo">
            <h2 style="color: white; margin: 0; font-size: 1.5rem;">AWS Coach</h2>
        </div>
        ''', unsafe_allow_html=True)
        
        # User Profile Card - Fixed version without code snippet
        user_name_display = user['name'] if len(user['name']) <= 20 else user['name'][:20] + "..."
        cert_display = user['target_certification'] if len(user['target_certification']) <= 35 else user['target_certification'][:35] + "..."
        
        st.markdown(f'''
        <div style="
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        ">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #FF9900 0%, #EC7211 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 2rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                ">
                    👤
                </div>
                <div style="flex: 1;">
                    <div style="color: white; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.25rem;">
                        {user_name_display}
                    </div>
                    <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.875rem;">
                        Level {int(xp / 100) + 1}
                    </div>
                    <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.875rem; margin-bottom: 0.5rem;">
                    🎯 Target Certification
                    </div>
                    <div style="color: white; font-weight: 600; font-size: 0.9rem; line-height: 1.3;">
                        {cert_display}
                    </div>
                        <div style="flex: 1; text-align: center;">
                        <div style="font-size: 1.5rem;">🔥</div>
                        <div style="color: #FF9900; font-weight: 800; font-size: 1.2rem;">{streak}</div>
                        <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.75rem;">Day Streak</div>
                    </div>
                    <div style="flex: 1; text-align: center;">
                        <div style="font-size: 1.5rem;">⚡</div>
                        <div style="color: #FF9900; font-weight: 800; font-size: 1.2rem;">{xp}</div>
                        <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.75rem;">Total XP</div>
                    </div>
                </div>
                </div>
            </div>      
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation Menu
        st.markdown('''<div style="color: rgba(255, 255, 255, 0.5); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;">Navigation</div>''', unsafe_allow_html=True)
        
        section = option_menu(
            menu_title=None,
            options=["Progress Dashboard", "AI Study Coach", "Practice Exams", "Study Tricks", "Answer Evaluation", "Q&A Knowledge Base"],
            icons=["speedometer2", "robot", "pencil-square", "lightbulb-fill", "check2-square", "question-circle-fill"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0", "background-color": "transparent"},
                "icon": {"color": "#FF9900", "font-size": "1.2rem"}, 
                "icon-selected": {"color": "white"},
                "nav-link": {
                    "color": "#000000",
                    "font-size": "0.95rem",
                    "font-weight": "700",
                    "text-align": "left",
                    "margin": "0.25rem 0",
                    "padding": "0.75rem 1rem",
                    "border-radius": "0.5rem",
                    "transition": "all 0.3s ease",
                    "background-color": "rgba(255, 255, 255, 0.05)",
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #222222 0%, #DB6100 100%)",
                    "color": "white",
                    "font-weight": "700",
                    "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.2)",
                    "icon-color": "white",
                },
            }
        )
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown('''<div style="color: rgba(255, 255, 255, 0.5); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;">Quick Actions</div>''', unsafe_allow_html=True)
        
        if st.button("⚙️ Settings", use_container_width=True):
            st.info("Settings coming soon!")
        
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.authenticated = False
            st.session_state.page = "home"
            st.rerun()
        
        # Footer
        st.markdown('''
        <div style="
            position: fixed;
            bottom: 1rem;
            left: 1rem;
            right: 1rem;
            text-align: center;
            color: rgba(255, 255, 255, 0.4);
            font-size: 0.75rem;
        ">
            AWS Coach v2.0
        </div>
        ''', unsafe_allow_html=True)
    
    # Display selected section
    try:
        if section == "Progress Dashboard":
            show_progress_dashboard(user)
        elif section == "AI Study Coach":
            show_ai_chat(user)
        elif section == "Practice Exams":
            show_practice_exam(user)
        elif section == "Study Tricks":
            show_study_tricks(user)
        elif section == "Answer Evaluation":
            show_answer_evaluation(user)
        elif section == "Q&A Knowledge Base":
            show_qna_knowledge_base(user)
    except Exception as e:
        logger.error(f"Error displaying section '{section}': {str(e)}", exc_info=True)
        st.error(f"❌ An error occurred: {str(e)}\n\nCheck logs for detailed traceback.")
        st.write("**Debug Info:** Check application logs for full traceback with line numbers.")
