"""
SQLAlchemy ORM models matching the exact database schema
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import json

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)
    
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)
    role_id = Column(Integer, ForeignKey("roles.id"))
    
    role = relationship("Role", back_populates="users")
    scores = relationship("UserScore", back_populates="user")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)
    
    questions = relationship("Question", back_populates="topic")
    scores = relationship("UserScore", back_populates="topic")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # Store as JSON string
    question_type = Column(String(50), nullable=False)
    correct_answer = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    
    @property
    def options_list(self):
        """Convert JSON string to list"""
        return json.loads(self.options) if self.options else []
    
    @options_list.setter
    def options_list(self, value):
        """Convert list to JSON string"""
        self.options = json.dumps(value)
    
    topic = relationship("Topic", back_populates="questions")

class UserScore(Base):
    __tablename__ = "user_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), nullable=False)
    score = Column(Integer, nullable=False)
    certificate_issued = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    
    user = relationship("User", back_populates="scores")
    topic = relationship("Topic", back_populates="scores")
