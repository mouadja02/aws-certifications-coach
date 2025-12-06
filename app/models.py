"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    """User model"""
    id: Optional[int] = None
    name: str
    email: EmailStr
    age: Optional[int] = None
    target_certification: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserCreate(BaseModel):
    """User creation model"""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)
    age: Optional[int] = Field(None, ge=18, le=100)
    target_certification: str


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class ChatMessage(BaseModel):
    """Chat message model"""
    user_id: int
    question: str = Field(..., min_length=1, max_length=2000)
    context: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    answer: str
    timestamp: datetime
    user_id: int


class UserStats(BaseModel):
    """User statistics model"""
    user_id: int
    total_study_time: str
    practice_tests_taken: int
    average_score: int
    progress_percentage: int
    last_activity: datetime

