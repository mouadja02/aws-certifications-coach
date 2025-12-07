"""
AWS Certifications Coach - Multi-Section Learning Dashboard
Features: AI Chat, Practice Exams, Study Tricks, Answer Evaluation, Q&A Knowledge Base
"""

import streamlit as st
import time
import sys
import os
import json
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from database import get_user_by_email, save_chat_message, get_user_progress, get_activity_log
from ai_service import AIService

def get_user_from_db(email: str):
    """Fetch user data from Snowflake"""
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


def show_ai_chat(user):
    """AI Chat Section - Context-aware conversations"""
    st.header("🤖 AI Study Coach")
    st.markdown(f"Ask me anything about **{user['target_certification']}**!")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"👋 Hi {user['name']}! I'm your AI study coach for {user['target_certification']}. How can I help you today?"
        }]
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your certification!"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking..."):
                ai_service = AIService()
                try:
                    response_text = ai_service.answer_question(
                        user["id"], 
                        prompt,
                        context=user["target_certification"]
                    )
                    save_chat_message(user["id"], prompt, response_text)
                except Exception as e:
                    print(f"Error: {e}")
                    response_text = "Sorry, I'm having trouble processing your question. Please try again."
                
                # Animated response
                full_response = ""
                message_placeholder = st.empty()
                for chunk in response_text.split(" "):
                    full_response += chunk + " "
                    time.sleep(0.02)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Chat tips
    with st.expander("💡 Chat Tips"):
        st.markdown("""
        **Ask me about:**
        - Core AWS services and concepts
        - Exam strategies and tips
        - Best practices and design patterns
        - Real-world scenarios
        - Troubleshooting common issues
        """)


def show_practice_exam(user):
    """Practice Exam Section - Generate and take exams"""
    st.header("📝 Practice Exams")
    st.markdown(f"Practice for **{user['target_certification']}**")
    
    # Exam settings
    col1, col2, col3 = st.columns(3)
    with col1:
        num_questions = st.selectbox("Number of Questions", [5, 10, 15, 20, 30], index=1)
    with col2:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
    with col3:
        topic = st.selectbox("Topic", ["All Topics", "EC2", "S3", "VPC", "IAM", "Lambda", "RDS", "CloudFormation"])
    
    if st.button("🚀 Generate New Exam", use_container_width=True):
        with st.spinner("🔄 Generating your practice exam..."):
            ai_service = AIService()
            try:
                exam_data = ai_service.generate_exam_practice(
                    user["id"],
                    user["target_certification"],
                    difficulty=difficulty.lower(),
                    num_questions=num_questions
                )
                st.session_state.current_exam = exam_data
                st.session_state.exam_answers = {}
                st.session_state.exam_submitted = False
                st.success("✅ Exam generated! Start answering below.")
                st.rerun()
            except Exception as e:
                st.error(f"Error generating exam: {e}")
    
    # Display current exam
    if "current_exam" in st.session_state and st.session_state.current_exam:
        exam = st.session_state.current_exam
        
        if not st.session_state.get("exam_submitted", False):
            # Show questions
            st.write("---")
            for i, question in enumerate(exam.get("questions", []), 1):
                st.subheader(f"Question {i}")
                st.write(question.get("question", ""))
                
                options = question.get("options", [])
                answer = st.radio(
                    f"Select your answer:",
                    options,
                    key=f"q_{i}",
                    index=None
                )
                st.session_state.exam_answers[i] = answer
                st.write("")
            
            # Submit button
            if st.button("📤 Submit Exam", type="primary", use_container_width=True):
                st.session_state.exam_submitted = True
                st.rerun()
        else:
            # Show results
            st.success("🎉 Exam Submitted!")
            questions = exam.get("questions", [])
            correct_count = 0
            
            for i, question in enumerate(questions, 1):
                user_answer = st.session_state.exam_answers.get(i)
                correct_answer = question.get("correct_answer")
                
                is_correct = user_answer == correct_answer
                if is_correct:
                    correct_count += 1
                
                with st.expander(f"Question {i} - {'✅ Correct' if is_correct else '❌ Incorrect'}"):
                    st.write(f"**Question:** {question.get('question')}")
                    st.write(f"**Your Answer:** {user_answer or 'Not answered'}")
                    st.write(f"**Correct Answer:** {correct_answer}")
                    st.write(f"**Explanation:** {question.get('explanation', 'N/A')}")
            
            # Score
            score = (correct_count / len(questions)) * 100
            st.write("---")
            col1, col2, col3 = st.columns(3)
            col1.metric("Score", f"{score:.1f}%")
            col2.metric("Correct", f"{correct_count}/{len(questions)}")
            col3.metric("Pass", "✅ Yes" if score >= 70 else "❌ No")
            
            if st.button("🔄 Take Another Exam", use_container_width=True):
                del st.session_state.current_exam
                del st.session_state.exam_answers
                del st.session_state.exam_submitted
                st.rerun()


def show_study_tricks(user):
    """Study Tricks Section - Memory techniques and mnemonics"""
    st.header("🧠 Study Tricks & Memory Techniques")
    st.markdown(f"Master **{user['target_certification']}** with proven memory techniques!")
    
    # Topic selection
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("What topic do you want to remember?", placeholder="e.g., S3 Storage Classes")
    with col2:
        st.write("")
        st.write("")
        generate_btn = st.button("✨ Generate Tricks", use_container_width=True)
    
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
    
    # Display tricks
    if "current_tricks" in st.session_state and st.session_state.current_tricks:
        tricks = st.session_state.current_tricks
        
        st.success("✅ Here are your study tricks!")
        
        # Display each trick type
        if tricks.get("mnemonic"):
            with st.container():
                st.subheader("🔤 Mnemonic")
                st.info(tricks["mnemonic"])
        
        if tricks.get("analogy"):
            with st.container():
                st.subheader("🔗 Analogy")
                st.info(tricks["analogy"])
        
        if tricks.get("visualization"):
            with st.container():
                st.subheader("🎨 Visualization")
                st.info(tricks["visualization"])
        
        if tricks.get("key_points"):
            with st.container():
                st.subheader("🎯 Key Points to Remember")
                for point in tricks["key_points"]:
                    st.write(f"- {point}")
    
    # Popular topics
    st.write("---")
    st.subheader("🔥 Popular Topics")
    popular_topics = [
        "S3 Storage Classes",
        "EC2 Instance Types",
        "VPC Components",
        "IAM Policies",
        "Lambda Limits",
        "RDS vs DynamoDB",
        "CloudFormation vs Terraform",
        "Security Best Practices"
    ]
    
    cols = st.columns(4)
    for i, topic in enumerate(popular_topics):
        with cols[i % 4]:
            if st.button(topic, use_container_width=True):
                st.session_state.selected_topic = topic
                st.rerun()


def show_answer_evaluation(user):
    """Answer Evaluation Section - Self-assessment with feedback"""
    st.header("✍️ Answer Evaluation")
    st.markdown("Practice writing answers and get AI-powered feedback!")
    
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
    """Q&A Knowledge Base - Searchable question database"""
    st.header("❓ Q&A Knowledge Base")
    st.markdown(f"Frequently asked questions for **{user['target_certification']}**")
    
    # Search
    search_query = st.text_input("🔍 Search questions:", placeholder="e.g., S3, Lambda, VPC...")
    
    # Categories
    categories = ["All", "Storage", "Compute", "Networking", "Security", "Database", "Monitoring"]
    selected_category = st.selectbox("Filter by category:", categories)
    
    # Sample Q&A (in production, this would come from Snowflake/n8n)
    qa_data = [
        {
            "category": "Storage",
            "question": "What is the difference between S3 and EBS?",
            "answer": "S3 is object storage for files and data, while EBS is block storage attached to EC2 instances.",
            "tags": ["S3", "EBS", "Storage"]
        },
        {
            "category": "Compute",
            "question": "When should I use Lambda vs EC2?",
            "answer": "Use Lambda for event-driven, short-running tasks. Use EC2 for long-running applications and full control.",
            "tags": ["Lambda", "EC2", "Compute"]
        },
        # Add more...
    ]
    
    # Display Q&A
    filtered_qa = qa_data
    if selected_category != "All":
        filtered_qa = [q for q in qa_data if q["category"] == selected_category]
    
    if search_query:
        filtered_qa = [q for q in filtered_qa if search_query.lower() in q["question"].lower() or search_query.lower() in q["answer"].lower()]
    
    st.write(f"**Found {len(filtered_qa)} questions**")
    st.write("---")
    
    for i, qa in enumerate(filtered_qa, 1):
        with st.expander(f"Q{i}: {qa['question']}"):
            st.write(f"**Category:** {qa['category']}")
            st.write(f"**Answer:** {qa['answer']}")
            st.write(f"**Tags:** {', '.join(qa['tags'])}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Helpful", key=f"helpful_{i}"):
                    st.success("Thanks for the feedback!")
            with col2:
                if st.button("👎 Not Helpful", key=f"not_helpful_{i}"):
                    st.info("We'll improve this answer!")

def show_progress_dashboard(user):
    """Progress Dashboard - Analytics and tracking"""
    progress_data = get_user_progress(user["id"])
    activity_data = get_activity_log(user["id"])

    if progress_data:
        study_time_minutes = progress_data["STUDY_TIME_MINUTES"]/60
        practice_tests_taken = progress_data["PRACTICE_TESTS_TAKEN"]
        average_score = progress_data["AVERAGE_SCORE"]
        storage_topic_progress = progress_data["STORAGE_TOPIC_PROGRESS"]
        compute_topic_progress = progress_data["COMPUTE_TOPIC_PROGRESS"]
        networking_topic_progress = progress_data["NETWORKING_TOPIC_PROGRESS"]
        security_topic_progress = progress_data["SECURITY_TOPIC_PROGRESS"]
        database_topic_progress = progress_data["DATABASE_TOPIC_PROGRESS"]
        last_activity = progress_data["LAST_ACTIVITY"]
        streak = progress_data["STREAK"]
        longest_streak = progress_data["LONGEST_STREAK"]
        xp = progress_data["XP"]
        accuracy_percentage = progress_data["ACCURACY_PERCENTAGE"]
        
        st.header("📊 Progress Dashboard")
        st.markdown(f"Track your progress for **{user['target_certification']}**")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Study Time", f"{study_time_minutes} minutes")
        col2.metric("Practice Exams", practice_tests_taken)
        col3.metric("Avg Score", f"{average_score}%")
        col4.metric("Correct Answers Percentage", f"{accuracy_percentage}%")
        
        st.write("---")
        
        # Progress bars
        st.subheader("📈 Topic Progress")
        topics = [
            ("Storage (S3, EBS, EFS)", storage_topic_progress),
            ("Compute (EC2, Lambda)", compute_topic_progress),
            ("Networking (VPC, Route53)", networking_topic_progress),
            ("Security (IAM, KMS)", security_topic_progress),
            ("Database (RDS, DynamoDB)", database_topic_progress),
        ]
        
        for topic, progress in topics:
            st.write(f"**{topic}**")
            st.progress(progress / 100)
            st.caption(f"{progress}% complete")
            st.write("")
        
        st.write("---")
        
        # Study streak
        st.subheader("🔥 Study Streak")
        col1 = st.columns(1)
        with col1:
            st.metric("Current Streak", f"{streak} days")
            st.metric("Longest Streak", f"{longest_streak} days")
            st.metric("Total XP", f"{xp}")
    else:
        st.info("No progress data found")

    if activity_data:
        # Get last 3 activities and descriptions
        last_activities = activity_data[-3:]["activity"]
        last_descriptions = activity_data[-3:]["description"]
    else:
        last_activities = None
        last_descriptions = None

    # Recent activity
    st.write("---")
    st.subheader("📝 Recent Activity")
    
    if last_activities and last_descriptions:
        activities = [
            {"type": last_activities[0], "desc": last_descriptions[0], "time": "2 hours ago"},
            {"type": last_activities[1], "desc": last_descriptions[1], "time": "5 hours ago"},
            {"type": last_activities[2], "desc": last_descriptions[2], "time": "1 day ago"},
        ]
        
        for activity in activities:
            icon = {"exam": "📝", "chat": "💬", "tricks": "🧠"}.get(activity["type"], "📌")
            st.write(f"{icon} **{activity['desc']}**")
            st.caption(f"{activity['time']}")
            st.write("")
    else:
        st.info("No recent activity found")

def show_dashboard():
    """Main Dashboard with Multi-Section Navigation"""
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            color: #FF9900;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .stButton>button {
            background-color: #FF9900;
            color: white;
            font-weight: bold;
            border-radius: 5px;
        }
        .stButton>button:hover {
            background-color: #EC7211;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Get user data
    user = get_user_from_db(st.session_state.user_email)
    if not user:
        st.error("Could not load user profile. Please try logging in again.")
        st.stop()
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg", width=150)
        st.title("AWS Coach")
        st.write(f"👤 **{user['name']}**")
        st.caption(f"🎯 {user['target_certification']}")
        st.write("---")
        
        # Horizental Navigation menu
        section = st.tabs(
            ["🏠 Progress Dashboard", "🤖 AI Study Coach", "📝 Practice Exams", "🧠 Study Tricks", "✍️ Answer Evaluation", "❓ Q&A Knowledge Base"],
            key="navigation"
        )
        
        st.write("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.page = "home"
            st.rerun()
    
    # Display selected section
    if "Progress Dashboard" in section:
        show_progress_dashboard(user)
    elif "AI Study Coach" in section:
        show_ai_chat(user)
    elif "Practice Exams" in section:
        show_practice_exam(user)
    elif "Study Tricks" in section:
        show_study_tricks(user)
    elif "Answer Evaluation" in section:
        show_answer_evaluation(user)
    elif "Q&A Knowledge Base" in section:
        show_qna_knowledge_base(user)
