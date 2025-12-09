"""
AI Service for AWS Certifications Coach
Handles AI-powered interactions via n8n workflows with Valkey queue management
"""

import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime
import json
import streamlit as st
import logging

logger = logging.getLogger(__name__)

class AIService:
    """AI Service that communicates with n8n workflows"""
    
    def __init__(self):
        # n8n webhook URLs from Streamlit secrets or environment variables
        self.chat_webhook = st.secrets.get("N8N_CHAT_WEBHOOK_URL", os.getenv("N8N_CHAT_WEBHOOK_URL"))
        self.exam_webhook = st.secrets.get("N8N_EXAM_WEBHOOK_URL", os.getenv("N8N_EXAM_WEBHOOK_URL"))
        self.tricks_webhook = st.secrets.get("N8N_TRICKS_WEBHOOK_URL", os.getenv("N8N_TRICKS_WEBHOOK_URL"))
        self.evaluation_webhook = st.secrets.get("N8N_EVALUATION_WEBHOOK_URL", os.getenv("N8N_EVALUATION_WEBHOOK_URL"))
        
        # Fallback mode if no webhooks configured
        self.use_fallback = not self.chat_webhook
    
    def _call_n8n_webhook(self, webhook_url: str, data: Dict[str, Any], async_call: bool = False) -> Any:
        """
        Call n8n webhook
        
        Args:
            webhook_url: The n8n webhook URL
            data: Data to send to the webhook
            async_call: If True, don't wait for response (fire and forget)
        Returns:
            Response from n8n workflow or None if async
        """
        try:
            if async_call:
                # Fire and forget - don't wait for response
                requests.post(
                    webhook_url,
                    json=data,
                    timeout=2,  # Short timeout for async calls
                    headers={"Content-Type": "application/json"}
                )
                return None
            else:
                response = requests.post(
                    webhook_url,
                    json=data,
                    timeout=30,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"n8n webhook error: {response.status_code}")
                    return {"error": f"HTTP {response.status_code}"}
                    
        except requests.exceptions.Timeout:
            if not async_call:
                logger.error("n8n webhook timeout")
                return {"error": "Request timed out"}
            return None
    
    # ============================================
    # CHAT OPERATIONS
    # ============================================
    
    def answer_question(
        self,
        user_id: int,
        question: str,
        context: Optional[str] = None
    ) -> str:
        """Answer a question using n8n chat workflow"""
        if self.use_fallback or not self.chat_webhook:
            return self._get_fallback_response(question)
        
        try:
            data = {
                "user_id": user_id,
                "question": question,
                "context": context or "",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = self._call_n8n_webhook(self.chat_webhook, data)
            
            if isinstance(result, dict):
                # Extract response from various possible keys
                for key in ["output", "text", "answer", "message", "response", "result"]:
                    if key in result:
                        return str(result[key])
                return json.dumps(result, indent=2)
            
            return str(result)
        except Exception as e:
            logger.error(f"Error in chat service: {e}")
            return self._get_fallback_response(question)
    
    # ============================================
    # EXAM OPERATIONS (Queue-based)
    # ============================================
    
    def trigger_exam_generation(
        self,
        session_id: str,
        user_id: int,
        certification: str,
        difficulty: str,
        total_questions: int,
        topic: str
    ) -> bool:
        """
        Trigger background question generation workflow
        The workflow will continuously generate questions and push to Valkey queue
        
        Returns:
            bool: Success status of trigger
        """
        if not self.exam_webhook:
            return False
        
        try:
            data = {
                "action": "generate_questions",
                "session_id": session_id,
                "user_id": user_id,
                "certification": certification,
                "difficulty": difficulty,
                "total_questions": total_questions,
                "topic": topic,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Async call - don't wait for response
            self._call_n8n_webhook(self.exam_webhook, data, async_call=True)
            logger.info(f"✅ Triggered exam generation for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error triggering exam generation: {e}")
            return False
    
    def check_answer(
        self,
        user_answer: Any,
        correct_answer: Any,
        question_text: str,
        explanation: str
    ) -> Dict[str, Any]:
        """
        Check if user's answer is correct (client-side, no API call needed)
        
        Args:
            user_answer: User's selected answer(s) - can be "A) Text" or just "A"
            correct_answer: Correct answer(s) from Valkey - can be "A" or ["A", "C"]
            question_text: The question text
            explanation: Pre-generated explanation
        Returns:
            dict: Result with is_correct and explanation
        """
        # Extract just the letter (A, B, C, D) from answers
        def extract_letter(answer):
            """Extract letter from 'A) Text' or 'A' format"""
            answer_str = str(answer).strip().upper()
            # If format is "A) Something", extract just "A"
            if ')' in answer_str:
                return answer_str.split(')')[0].strip()
            # If already just a letter, return it
            return answer_str[0] if answer_str else ''
        
        def normalize_answer(answer):
            """Normalize answer to list of letters"""
            if isinstance(answer, list):
                return sorted([extract_letter(a) for a in answer])
            return [extract_letter(answer)]
        
        user_normalized = normalize_answer(user_answer)
        correct_normalized = normalize_answer(correct_answer)
        
        is_correct = user_normalized == correct_normalized
        
        # Format correct answer for display
        if isinstance(correct_answer, list):
            display_correct = correct_answer
        else:
            display_correct = correct_answer
        
        return {
            "is_correct": is_correct,
            "correct_answer": display_correct,
            "explanation": explanation,
            "user_answer": user_answer
        }
    
    # ============================================
    # STUDY TRICKS
    # ============================================
    
    def get_study_tricks(
        self,
        user_id: int,
        certification: str,
        topic: str
    ) -> Dict[str, Any]:
        """Get study tricks and tips using n8n workflow"""
        if self.use_fallback or not self.tricks_webhook:
            return self._get_fallback_tricks(topic)
        
        try:
            data = {
                "user_id": user_id,
                "certification": certification,
                "topic": topic,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = self._call_n8n_webhook(self.tricks_webhook, data)
            
            if isinstance(result, dict):
                return result
            
            # Try to parse as JSON
            try:
                return json.loads(str(result))
            except:
                return {"tricks": str(result)}
                
        except Exception as e:
            logger.error(f"Error in tricks service: {e}")
            return self._get_fallback_tricks(topic)
    
    def evaluate_answer(
        self,
        user_id: int,
        question: str,
        user_answer: str,
        certification: str
    ) -> Dict[str, Any]:
        """Evaluate user's written answer using n8n workflow"""
        if self.use_fallback or not self.evaluation_webhook:
            return {"score": 0, "feedback": "Evaluation not configured"}
        
        try:
            data = {
                "user_id": user_id,
                "question": question,
                "user_answer": user_answer,
                "certification": certification,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = self._call_n8n_webhook(self.evaluation_webhook, data)
            
            if isinstance(result, dict):
                return result
            
            # Try to parse as JSON
            try:
                return json.loads(str(result))
            except:
                return {"feedback": str(result)}
                
        except Exception as e:
            logger.error(f"Error in evaluation service: {e}")
            return {"error": str(e)}
    
    # ============================================
    # FALLBACK RESPONSES
    # ============================================
    
    def _get_fallback_response(self, question: str) -> str:
        """Fallback response system when AI APIs are not available"""
        
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
        
        question_lower = question.lower()
        for keyword, answer in knowledge_base.items():
            if keyword in question_lower:
                return f"Based on AWS best practices:\n\n{answer}\n\n💡 Tip: Configure n8n webhook for AI-powered answers!"
        
        return f"Thank you for your question: '{question}'\n\nPlease configure N8N_CHAT_WEBHOOK_URL in Streamlit secrets for AI-powered responses."
    
    def _get_fallback_tricks(self, topic: str) -> Dict[str, Any]:
        """Fallback study tricks when n8n is not configured"""
        return {
            "mnemonic": f"Create a memorable acronym for {topic} concepts",
            "analogy": f"Think of {topic} like everyday objects and processes",
            "visualization": f"Draw diagrams to visualize {topic} architecture",
            "key_points": [
                "Practice with hands-on labs",
                "Review AWS documentation",
                "Take practice exams regularly",
                "Join study groups"
            ]
        }


if __name__ == "__main__":
    # Test the AI service
    service = AIService()
    response = service.answer_question(
        user_id=1,
        question="What is Amazon S3?"
    )
    print(response)
