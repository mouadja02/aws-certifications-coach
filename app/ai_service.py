"""
AI Service for AWS Certifications Coach
Handles AI-powered interactions via n8n workflows
"""

import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime
import json
import streamlit as st

class AIService:
    """
    AI Service that communicates with n8n workflows
    Supports different workflow endpoints for various features
    """
    
    def __init__(self):
        # n8n webhook URLs from Streamlit secrets or environment variables
        self.chat_webhook = st.secrets.get("N8N_CHAT_WEBHOOK_URL", os.getenv("N8N_CHAT_WEBHOOK_URL"))
        self.exam_webhook = st.secrets.get("N8N_EXAM_WEBHOOK_URL", os.getenv("N8N_EXAM_WEBHOOK_URL"))
        self.tricks_webhook = st.secrets.get("N8N_TRICKS_WEBHOOK_URL", os.getenv("N8N_TRICKS_WEBHOOK_URL"))
        self.evaluation_webhook = st.secrets.get("N8N_EVALUATION_WEBHOOK_URL", os.getenv("N8N_EVALUATION_WEBHOOK_URL"))
        
        # Fallback mode if no webhooks configured
        self.use_fallback = not self.chat_webhook
    
    def _call_n8n_webhook(self, webhook_url: str, data: Dict[str, Any]) -> str:
        """
        Call n8n webhook and return response
        
        Args:
            webhook_url: The n8n webhook URL
            data: Data to send to the webhook
            
        Returns:
            str: Response from n8n workflow
        """
        try:
            response = requests.post(
                webhook_url,
                json=data,
                timeout=600,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats from n8n
                if isinstance(result, list) and len(result) > 0:
                    result = result[0]
                
                if isinstance(result, dict):
                    # Look for common response keys
                    for key in ["output", "text", "answer", "message", "response", "result"]:
                        if key in result:
                            return str(result[key])
                    # Return JSON string if no standard key found
                    return json.dumps(result, indent=2)
                
                return str(result)
            else:
                print(f"❌ n8n webhook error: {response.status_code}")
                return self._get_fallback_response("Error calling AI service")
                
        except requests.exceptions.Timeout:
            print("❌ n8n webhook timeout")
            return "I apologize, but the request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            print(f"❌ n8n webhook request failed: {e}")
            return self._get_fallback_response("Connection error")
    
    def answer_question(
        self,
        user_id: int,
        question: str,
        context: Optional[str] = None
    ) -> str:
        """
        Answer a question using n8n chat workflow
        
        Args:
            user_id: User ID for context
            question: User's question
            context: Additional context (certification type, etc.)
            
        Returns:
            str: Answer from n8n workflow
        """
        if self.use_fallback or not self.chat_webhook:
            return self._get_fallback_response(question)
        
        try:
            data = {
                "user_id": user_id,
                "question": question,
                "context": context or "",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return self._call_n8n_webhook(self.chat_webhook, data)
        except Exception as e:
            print(f"❌ Error in chat service: {e}")
            return self._get_fallback_response(question)
    
    def start_exam_session(
        self,
        user_id: int,
        certification: str,
        difficulty: str = "medium",
        total_questions: int = 10,
        topic: str = "All Topics"
    ) -> Dict[str, Any]:
        """
        Start a new exam session and get the first question
        
        Args:
            user_id: User ID
            certification: Target certification
            difficulty: Question difficulty (easy, medium, hard)
            total_questions: Total number of questions for this session
            topic: Specific topic or "All Topics"
            
        Returns:
            dict: Session data with first question
        """
        if self.use_fallback or not self.exam_webhook:
            return self._get_fallback_exam_question(1, total_questions)
        
        try:
            data = {
                "action": "start_session",
                "user_id": user_id,
                "certification": certification,
                "difficulty": difficulty,
                "total_questions": total_questions,
                "topic": topic,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self._call_n8n_webhook(self.exam_webhook, data)
            
            # Try to parse as JSON if possible
            try:
                return json.loads(response)
            except:
                return {"error": "Invalid response format", "raw": response}
        except Exception as e:
            print(f"❌ Error in exam service: {e}")
            return {"error": str(e)}
    
    def check_exam_answer(
        self,
        user_id: int,
        session_id: str,
        question_id: str,
        user_answer: Any,
        question_text: str
    ) -> Dict[str, Any]:
        """
        Check user's answer and get explanation
        
        Args:
            user_id: User ID
            session_id: Exam session ID
            question_id: Current question ID
            user_answer: User's selected answer(s)
            question_text: The question text (for context)
            
        Returns:
            dict: Evaluation with correct answer and explanation
        """
        if self.use_fallback or not self.exam_webhook:
            return self._get_fallback_answer_check(user_answer)
        
        try:
            data = {
                "action": "check_answer",
                "user_id": user_id,
                "session_id": session_id,
                "question_id": question_id,
                "user_answer": user_answer,
                "question_text": question_text,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self._call_n8n_webhook(self.exam_webhook, data)
            
            # Try to parse as JSON if possible
            try:
                return json.loads(response)
            except:
                return {"error": "Invalid response format", "raw": response}
        except Exception as e:
            print(f"❌ Error checking answer: {e}")
            return {"error": str(e)}
    
    def get_next_exam_question(
        self,
        user_id: int,
        session_id: str,
        current_question_number: int
    ) -> Dict[str, Any]:
        """
        Get the next question in the exam session
        
        Args:
            user_id: User ID
            session_id: Exam session ID
            current_question_number: Current question number
            
        Returns:
            dict: Next question data
        """
        if self.use_fallback or not self.exam_webhook:
            return self._get_fallback_exam_question(current_question_number + 1, 10)
        
        try:
            data = {
                "action": "next_question",
                "user_id": user_id,
                "session_id": session_id,
                "current_question_number": current_question_number,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self._call_n8n_webhook(self.exam_webhook, data)
            
            # Try to parse as JSON if possible
            try:
                return json.loads(response)
            except:
                return {"error": "Invalid response format", "raw": response}
        except Exception as e:
            print(f"❌ Error getting next question: {e}")
            return {"error": str(e)}
    
    def end_exam_session(
        self,
        user_id: int,
        session_id: str
    ) -> Dict[str, Any]:
        """
        End exam session and get final results
        
        Args:
            user_id: User ID
            session_id: Exam session ID
            
        Returns:
            dict: Final exam results and statistics
        """
        if self.use_fallback or not self.exam_webhook:
            return {"message": "Exam session ended"}
        
        try:
            data = {
                "action": "end_session",
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self._call_n8n_webhook(self.exam_webhook, data)
            
            # Try to parse as JSON if possible
            try:
                return json.loads(response)
            except:
                return {"message": response}
        except Exception as e:
            print(f"❌ Error ending session: {e}")
            return {"error": str(e)}
    
    def get_study_tricks(
        self,
        user_id: int,
        certification: str,
        topic: Optional[str] = None
    ) -> str:
        """
        Get study tricks and tips using n8n workflow
        
        Args:
            user_id: User ID
            certification: Target certification
            topic: Specific topic (optional)
            
        Returns:
            str: Study tricks and tips
        """
        if self.use_fallback or not self.tricks_webhook:
            return self._get_fallback_tricks(topic)
        
        try:
            data = {
                "user_id": user_id,
                "certification": certification,
                "topic": topic or "",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return self._call_n8n_webhook(self.tricks_webhook, data)
        except Exception as e:
            print(f"❌ Error in tricks service: {e}")
            return self._get_fallback_tricks(topic)
    
    def evaluate_answer(
        self,
        user_id: int,
        question: str,
        user_answer: str,
        correct_answer: str
    ) -> Dict[str, Any]:
        """
        Evaluate user's answer using n8n workflow
        
        Args:
            user_id: User ID
            question: The question
            user_answer: User's answer
            correct_answer: Correct answer
            
        Returns:
            dict: Evaluation results with feedback
        """
        if self.use_fallback or not self.evaluation_webhook:
            return {"score": 0, "feedback": "Evaluation not configured"}
        
        try:
            data = {
                "user_id": user_id,
                "question": question,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self._call_n8n_webhook(self.evaluation_webhook, data)
            
            # Try to parse as JSON if possible
            try:
                return json.loads(response)
            except:
                return {"feedback": response}
        except Exception as e:
            print(f"❌ Error in evaluation service: {e}")
            return {"error": str(e)}
    
    def _get_fallback_response(self, question: str) -> str:
        """
        Fallback response system when AI APIs are not available
        Provides helpful AWS certification information
        """
        
        # Knowledge base for common AWS certification questions
        knowledge_base = {
            "s3": """Amazon S3 (Simple Storage Service) is an object storage service offering:
            - Scalability: Store unlimited data
            - Durability: 99.999999999% (11 9's) durability
            - Storage Classes: Standard, Intelligent-Tiering, Glacier, etc.
            - Security: Encryption, access control, versioning
            - Use Cases: Backup, data lakes, web hosting, content distribution""",
            
            "ec2": """Amazon EC2 (Elastic Compute Cloud) provides scalable computing capacity:
            - Instance Types: General purpose, compute optimized, memory optimized
            - Pricing: On-Demand, Reserved, Spot, Savings Plans
            - Features: Auto Scaling, Elastic Load Balancing, Amazon EBS
            - Use Cases: Web applications, batch processing, gaming servers""",
            
            "vpc": """Amazon VPC (Virtual Private Cloud) provides isolated network resources:
            - Subnets: Public and private subnets for resource organization
            - Security: Security groups and Network ACLs
            - Connectivity: Internet Gateway, NAT Gateway, VPN
            - Best Practice: Use multiple availability zones for high availability""",
            
            "iam": """AWS IAM (Identity and Access Management) controls access:
            - Users: Individual identities with credentials
            - Groups: Collections of users with shared permissions
            - Roles: Temporary credentials for services and applications
            - Policies: JSON documents defining permissions
            - Best Practice: Follow principle of least privilege""",
            
            "lambda": """AWS Lambda is a serverless compute service:
            - Event-driven: Runs code in response to triggers
            - Pricing: Pay only for compute time used
            - Scalability: Automatically scales based on demand
            - Languages: Python, Node.js, Java, Go, Ruby, .NET
            - Use Cases: APIs, data processing, automation"""
        }
        
        # Search for relevant knowledge
        question_lower = question.lower()
        for keyword, answer in knowledge_base.items():
            if keyword in question_lower:
                return f"""Based on AWS best practices and certification materials:\n\n{answer}
                
                \n\nFor more detailed information, I recommend:
                1. AWS Official Documentation
                2. AWS Certified Solutions Architect Study Guide
                3. AWS Hands-on Labs and Tutorials
                
                \n\n💡 Tip: Practice with AWS Free Tier to gain hands-on experience!
                
                \n\nNote: This is a basic response. For AI-powered detailed answers, configure an AI API key (OpenAI or Anthropic)."""
        
        # Generic response if no specific match
        return f"""Thank you for your question: "{question}"
        
        I'm currently running in fallback mode. For detailed AI-powered responses, 
        please configure an AI API key (OpenAI or Anthropic) in your environment variables.
        
        Here are some general AWS certification tips:
        
        1. **Understand the Fundamentals**: Focus on core services (EC2, S3, VPC, IAM)
        2. **Hands-on Practice**: Use AWS Free Tier for practical experience
        3. **Study Resources**: 
           - AWS Documentation (https://docs.aws.amazon.com/)
           - AWS Training and Certification (https://aws.amazon.com/training/)
           - Practice exams and whitepapers
        4. **Key Areas**: 
           - Compute (EC2, Lambda)
           - Storage (S3, EBS, EFS)
           - Networking (VPC, Route 53, CloudFront)
           - Security (IAM, KMS, CloudTrail)
           - Databases (RDS, DynamoDB)
        
        Good luck with your certification preparation! 🚀"""
    
    def _get_fallback_tricks(self, topic: Optional[str]) -> str:
        """Fallback study tricks when n8n is not configured"""
        tricks = f"""
        📚 Study Tricks and Tips{f' for {topic}' if topic else ''}:
        
        1. **Active Recall**: Test yourself regularly instead of just re-reading
        2. **Spaced Repetition**: Review material at increasing intervals
        3. **Hands-On Practice**: Use AWS Free Tier to gain practical experience
        4. **Mind Maps**: Create visual connections between AWS services
        5. **Study Groups**: Explain concepts to others to reinforce learning
        6. **Official Documentation**: AWS docs are the most reliable source
        7. **Practice Exams**: Take mock tests to identify weak areas
        8. **Real-World Scenarios**: Think about how services solve actual problems
        
        💡 Pro Tip: Focus on understanding WHY services work, not just HOW.
        
        Note: Configure n8n webhooks for personalized study recommendations!
        """
        return tricks
    
    def _get_fallback_exam_question(self, question_number: int, total_questions: int) -> Dict[str, Any]:
        """Fallback exam question when n8n is not configured"""
        sample_questions = [
            {
                "question": "Which AWS service provides object storage?",
                "options": ["A) Amazon EBS", "B) Amazon S3", "C) Amazon EFS", "D) Amazon RDS"],
                "correct_answer": "B) Amazon S3",
                "type": "single"
            },
            {
                "question": "What is the maximum size of an S3 object?",
                "options": ["A) 5 GB", "B) 5 TB", "C) 500 GB", "D) 50 TB"],
                "correct_answer": "B) 5 TB",
                "type": "single"
            },
            {
                "question": "Which services can be used for serverless computing? (Select TWO)",
                "options": ["A) AWS Lambda", "B) Amazon EC2", "C) AWS Fargate", "D) Amazon RDS"],
                "correct_answer": ["A) AWS Lambda", "C) AWS Fargate"],
                "type": "multiple"
            }
        ]
        
        # Cycle through sample questions
        idx = (question_number - 1) % len(sample_questions)
        question = sample_questions[idx]
        
        return {
            "session_id": "fallback_session",
            "question_id": f"q_{question_number}",
            "question_number": question_number,
            "total_questions": total_questions,
            "question": question["question"],
            "options": question["options"],
            "type": question["type"],
            "message": "Using fallback mode. Configure n8n webhook for AI-generated questions."
        }
    
    def _get_fallback_answer_check(self, user_answer: Any) -> Dict[str, Any]:
        """Fallback answer check when n8n is not configured"""
        return {
            "is_correct": False,
            "correct_answer": "B) Amazon S3",
            "explanation": "Amazon S3 (Simple Storage Service) is AWS's object storage service. It provides scalable, durable, and highly available storage for objects (files). EBS is block storage, EFS is file storage, and RDS is a database service.",
            "reference": "https://docs.aws.amazon.com/s3/",
            "message": "Using fallback mode. Configure n8n webhook for AI-powered answer checking."
        }


if __name__ == "__main__":
    # Test the AI service
    import asyncio
    
    def test():
        service = AIService()
        response = service.answer_question(
            user_id=1,
            question="What is Amazon S3 and what are its main features?"
        )
        print(response)
    
    asyncio.run(test())

