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
from streamlit_option_menu import option_menu
sys.path.insert(0, os.path.dirname(__file__))

from database import get_user_by_email, save_chat_message, get_user_progress, get_activity_log
from ai_service import AIService
from valkey_client import get_valkey_client

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
    """Practice Exam Section - Fast queue-based exam with AI-generated questions"""
    st.header("📝 Practice Exams")
    st.markdown(f"Practice for **{user['target_certification']}** - AWS Official Exam Style")
    
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
    
    # Get Valkey client
    valkey = get_valkey_client()
    ai_service = AIService()
    
    # If no exam session is active, show exam setup
    if st.session_state.exam_session_id is None:
        st.info("👇 Configure your practice exam settings and click 'Start Exam' to begin")
    
    # Exam settings
    col1, col2, col3 = st.columns(3)
    with col1:
            num_questions = st.selectbox("Number of Questions", [5, 10, 15, 20, 30], index=1, key="num_q")
    with col2:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="diff")
    with col3:
            topic = st.selectbox("Topic", ["All Topics", "EC2", "S3", "VPC", "IAM", "Lambda", "RDS", "CloudFormation", "CloudWatch"], key="topic")
        
    st.write("---")

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
    else:
        session_id = st.session_state.exam_session_id
        
        # Progress bar
        progress = st.session_state.question_number / st.session_state.total_questions
        st.progress(progress)
        
        # Show queue status
        queue_length = valkey.get_queue_length(session_id)
        st.caption(f"Question {st.session_state.question_number} of {st.session_state.total_questions} | Queue: {queue_length} questions ready")
        
        st.write("---")
        
        # Display current question
        if st.session_state.current_question:
            question_data = st.session_state.current_question
            
            # Question text
            st.subheader(f"Question {st.session_state.question_number}")
            st.write(question_data.get("question", ""))
            st.write("")
            
            # Determine if multiple choice or single choice
            question_type = question_data.get("type", "single")
            options = question_data.get("options", [])
            
            # If not showing explanation, show answer options
            if not st.session_state.show_explanation:
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
                
                if result:
                    # Show if correct or incorrect
                    if result.get("is_correct", False):
                        st.success("✅ Correct! Well done!")
                    else:
                        st.error("❌ Incorrect")
                    
                    st.write("---")
                    
                    # Show explanation
                    st.subheader("📚 Explanation")
                    st.write(result.get("explanation", "No explanation available"))
                    
                    st.write("---")
                    
                    # Show correct answer
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Your Answer:**")
                        user_ans = st.session_state.exam_results[-1].get("user_answer")
                        if isinstance(user_ans, list):
                            for ans in user_ans:
                                st.write(f"- {ans}")
                        else:
                            st.write(user_ans)
                    
                    with col2:
                        st.write("**Correct Answer:**")
                        correct_ans = result.get("correct_answer")
                        if isinstance(correct_ans, list):
                            for ans in correct_ans:
                                st.write(f"- {ans}")
                        else:
                            st.write(correct_ans)
                    
                    # Show reference link if available
                    if question_data.get("reference"):
                        st.info(f"📖 Reference: {question_data.get('reference')}")
                    
                    st.write("---")
                    
                    # Next question or finish
                    if st.session_state.question_number < st.session_state.total_questions:
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
                        if st.button("🏁 Finish Exam", type="primary", use_container_width=True):
                            # Show final results
                            st.balloons()
                            st.success("🎉 Exam Complete!")
                            
                            # Calculate final score
                            score_percentage = (st.session_state.exam_score / st.session_state.total_questions) * 100
                            
                            # Save to database (save session results)
                            try:
                                from database import execute_update
                                query = f"""
                                INSERT INTO exam_sessions (
                                    session_id, user_id, certification, difficulty, topic,
                                    total_questions, correct_answers, incorrect_answers,
                                    percentage, passed, started_at, completed_at, duration_minutes
                                ) VALUES (
                                    '{session_id}',
                                    {user['id']},
                                    '{user['target_certification']}',
                                    '{valkey.get_session(session_id).get('difficulty', 'medium')}',
                                    '{valkey.get_session(session_id).get('topic', 'All Topics')}',
                                    {st.session_state.total_questions},
                                    {st.session_state.exam_score},
                                    {st.session_state.total_questions - st.session_state.exam_score},
                                    {score_percentage},
                                    {str(score_percentage >= 70).upper()},
                                    '{valkey.get_session(session_id).get('started_at')}',
                                    '{datetime.now().isoformat()}',
                                    {int((datetime.now() - datetime.fromisoformat(valkey.get_session(session_id).get('started_at'))).seconds / 60)}
                                )
                                """
                                execute_update(query)
                            except Exception as e:
                                st.warning(f"Could not save results to database: {e}")
                            
                            # Clean up Valkey
                            valkey.delete_session(session_id)
                            
                            st.write("---")
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Final Score", f"{score_percentage:.1f}%")
                            col2.metric("Correct", f"{st.session_state.exam_score}/{st.session_state.total_questions}")
                            col3.metric("Pass", "✅ Yes" if score_percentage >= 70 else "❌ No")
            
                            st.write("---")
                            st.subheader("📊 Question Review")
                            
                            for i, result in enumerate(st.session_state.exam_results, 1):
                                status = "✅" if result["is_correct"] else "❌"
                                with st.expander(f"{status} Question {i} - {result['question'][:60]}..."):
                                    st.write(f"**Question:** {result['question']}")
                                    st.write(f"**Your Answer:** {result['user_answer']}")
                                    st.write(f"**Correct Answer:** {result['correct_answer']}")
                                    st.write(f"**Explanation:** {result['explanation']}")
                            
                            st.write("---")
                            if st.button("🔄 Take Another Exam", use_container_width=True):
                                # Reset all exam session state
                                st.session_state.exam_session_id = None
                                st.session_state.current_question = None
                                st.session_state.question_number = 0
                                st.session_state.exam_score = 0
                                st.session_state.exam_results = []
                                st.session_state.show_explanation = False
                                st.session_state.current_answer_result = None
                                st.rerun()
        
        # Option to quit exam early
        st.write("")
        if st.button("❌ Quit Exam", use_container_width=True):
            # Clean up
            data = {
                "action": "quit_session",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            ai_service._call_n8n_webhook(session_id,data,async_call=True)
            valkey.delete_session(session_id)
            st.session_state.exam_session_id = None
            st.session_state.current_question = None
            st.session_state.question_number = 0
            st.session_state.exam_score = 0
            st.session_state.exam_results = []
            st.session_state.show_explanation = False
            st.session_state.current_answer_result = None
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
        study_time_minutes = progress_data.get("STUDY_TIME_MINUTES", 0) / 60
        practice_tests_taken = progress_data.get("PRACTICE_TESTS_TAKEN", 0)
        average_score = progress_data.get("AVERAGE_SCORE", 0)
        storage_topic_progress = progress_data.get("STORAGE_TOPIC_PROGRESS", 0)
        compute_topic_progress = progress_data.get("COMPUTE_TOPIC_PROGRESS", 0)
        networking_topic_progress = progress_data.get("NETWORKING_TOPIC_PROGRESS", 0)
        security_topic_progress = progress_data.get("SECURITY_TOPIC_PROGRESS", 0)
        database_topic_progress = progress_data.get("DATABASE_TOPIC_PROGRESS", 0)
        streak = progress_data.get("STREAK", 0)
        longest_streak = progress_data.get("LONGEST_STREAK", 0)
        xp = progress_data.get("XP", 0)
        accuracy_percentage = progress_data.get("ACCURACY_PERCENTAGE", 0)
        
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
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Streak", f"{streak} days")
        col2.metric("Longest Streak", f"{longest_streak} days")
        col3.metric("Total XP", f"{xp}")
    else:
        st.info("No progress data found")

    if activity_data:
        # Get last 3 activities and descriptions
        last_activities = [row['ACTIVITY'] for row in activity_data]
        last_descriptions = [row['DESCRIPTION'] for row in activity_data]
    else:
        last_activities = []
        last_descriptions = []

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
        section = option_menu(
            menu_title=None,
            options=["Progress Dashboard", "AI Study Coach", "Practice Exams", "Study Tricks", "Answer Evaluation", "Q&A Knowledge Base"],
            icons=["house", "robot", "pencil-square", "lightbulb", "check2-square", "question-circle"],
            orientation="horizontal"
        )
        
        st.write("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.page = "home"
            st.rerun()
    
    # Display selected section
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
