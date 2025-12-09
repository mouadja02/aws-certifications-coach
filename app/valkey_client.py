"""
Valkey Client for AWS Certifications Coach
Handles caching and queue management for exam questions
"""

import json
import streamlit as st
import valkey
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ValkeyClient:
    """Valkey client for queue and cache management"""
    
    def __init__(self):
        """Initialize Valkey connection from Streamlit secrets using URI"""
        try:
            # Get Valkey URI from Streamlit secrets
            valkey_uri = st.secrets.get("VALKEY_URI")
            
            if not valkey_uri:
                raise ValueError("VALKEY_URI not found in Streamlit secrets")
            
            # Connect using URI (supports valkeys:// for SSL)
            self.client = valkey.from_url(
                valkey_uri,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            
            # Test connection
            self.client.ping()
            logger.info("✅ Valkey connection established")
        except Exception as e:
            logger.error(f"❌ Valkey connection failed: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Valkey is connected"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    # ============================================
    # QUEUE OPERATIONS (for exam questions)
    # ============================================
    
    def push_question(self, session_id: str, question_data: Dict[str, Any]) -> bool:
        """
        Push a question to the queue (FIFO)
        
        Args:
            session_id: Exam session ID
            question_data: Question object
        Returns:
            bool: Success status
        """
        if not self.is_connected():
            return False
        
        try:
            queue_key = f"exam_queue:{session_id}"
            self.client.rpush(queue_key, json.dumps(question_data))
            # Set expiry of 2 hours
            self.client.expire(queue_key, 7200)
            return True
        except Exception as e:
            logger.error(f"Error pushing question to queue: {e}")
            return False
    
    def pop_question(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Pop the next question from the queue (FIFO)
        
        Args:
            session_id: Exam session ID
        Returns:
            dict: Question object or None
        """
        if not self.is_connected():
            return None
        
        try:
            queue_key = f"exam_queue:{session_id}"
            question_json = self.client.lpop(queue_key)
            if question_json:
                return json.loads(question_json)
            return None
        except Exception as e:
            logger.error(f"Error popping question from queue: {e}")
            return None
    
    def get_queue_length(self, session_id: str) -> int:
        """Get current queue length"""
        if not self.is_connected():
            return 0
        
        try:
            queue_key = f"exam_queue:{session_id}"
            return self.client.llen(queue_key)
        except:
            return 0
    
    def clear_queue(self, session_id: str) -> bool:
        """Clear the entire queue"""
        if not self.is_connected():
            return False
        
        try:
            queue_key = f"exam_queue:{session_id}"
            self.client.delete(queue_key)
            return True
        except Exception as e:
            logger.error(f"Error clearing queue: {e}")
            return False
    
    # ============================================
    # SESSION MANAGEMENT
    # ============================================
    
    def save_session(self, session_id: str, session_data: Dict[str, Any], ttl: int = 7200) -> bool:
        """Save exam session data"""
        if not self.is_connected():
            return False
        
        try:
            key = f"session:{session_id}"
            self.client.setex(key, ttl, json.dumps(session_data))
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get exam session data"""
        if not self.is_connected():
            return None
        
        try:
            key = f"session:{session_id}"
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update specific session fields"""
        if not self.is_connected():
            return False
        
        try:
            session = self.get_session(session_id)
            if session:
                session.update(updates)
                return self.save_session(session_id, session)
            return False
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session data"""
        if not self.is_connected():
            return False
        
        try:
            key = f"session:{session_id}"
            self.client.delete(key)
            # Also delete the queue
            self.clear_queue(session_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False
    
    # ============================================
    # QUESTION GENERATION STATUS
    # ============================================
    
    def set_generation_status(self, session_id: str, status: str) -> bool:
        """
        Set question generation status
        Status: 'generating', 'completed', 'error'
        """
        if not self.is_connected():
            return False
        
        try:
            key = f"gen_status:{session_id}"
            self.client.setex(key, 7200, status)
            return True
        except Exception as e:
            logger.error(f"Error setting generation status: {e}")
            return False
    
    def get_generation_status(self, session_id: str) -> Optional[str]:
        """Get question generation status"""
        if not self.is_connected():
            return None
        
        try:
            key = f"gen_status:{session_id}"
            return self.client.get(key)
        except:
            return None
    
    # ============================================
    # ANSWER STORAGE (for verification)
    # ============================================
    
    def save_question_answer(self, question_id: str, answer_data: Dict[str, Any], ttl: int = 7200) -> bool:
        """Save correct answer and explanation for a question"""
        if not self.is_connected():
            return False
        
        try:
            key = f"answer:{question_id}"
            self.client.setex(key, ttl, json.dumps(answer_data))
            return True
        except Exception as e:
            logger.error(f"Error saving answer: {e}")
            return False
    
    def get_question_answer(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Get correct answer and explanation for a question"""
        if not self.is_connected():
            return None
        
        try:
            key = f"answer:{question_id}"
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting answer: {e}")
            return None


# Create a singleton instance
@st.cache_resource
def get_valkey_client():
    """Get cached Valkey client instance"""
    return ValkeyClient()

