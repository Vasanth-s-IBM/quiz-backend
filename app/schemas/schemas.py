"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    name: str

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role_id: int

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    id: int
    uuid: UUID
    is_active: bool
    role_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Topic Schemas
class TopicBase(BaseModel):
    name: str

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int
    uuid: UUID
    is_active: bool
    question_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

# Question Schemas
class QuestionBase(BaseModel):
    question_text: str
    options: List[str]
    question_type: str
    correct_answer: str
    topic_id: int

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(BaseModel):
    id: int
    uuid: UUID
    question_text: str
    options: List[str]
    question_type: str
    # Note: correct_answer excluded for user view
    
    class Config:
        from_attributes = True

class QuestionAdmin(QuestionResponse):
    correct_answer: str
    topic_id: int
    is_active: bool

# Exam Schemas
class ExamStartRequest(BaseModel):
    topic_id: int

class ExamStartResponse(BaseModel):
    exam_session_id: str
    questions: List[QuestionResponse]
    duration_minutes: int
    total_questions: int

class AnswerSubmission(BaseModel):
    question_id: int
    selected_answer: str

class ExamSubmitRequest(BaseModel):
    topic_id: int
    answers: List[AnswerSubmission]
    tab_switch_count: int

class ExamSubmitResponse(BaseModel):
    score: int
    total_questions: int
    percentage: float
    malpractice_detected: bool
    message: str

# Score Schemas
class UserScoreResponse(BaseModel):
    id: int
    score: int
    certificate_issued: bool
    created_at: datetime
    user_id: int
    topic_id: int
    user_name: str
    topic_name: str
    
    class Config:
        from_attributes = True

# Admin Dashboard
class DashboardStats(BaseModel):
    total_users: int
    total_admins: int
    total_topics: int
    total_exams_taken: int

# Certificate
class CertificateRequest(BaseModel):
    user_score_id: int
