"""
Topic management routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.models.models import User, Topic, Question
from app.schemas.schemas import TopicResponse, TopicCreate

router = APIRouter()

@router.get("/", response_model=List[TopicResponse])
def get_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active topics with question count
    Available to all authenticated users
    """
    topics = db.query(
        Topic,
        func.count(Question.id).label("question_count")
    ).outerjoin(
        Question, (Question.topic_id == Topic.id) & (Question.is_active == True)
    ).filter(
        Topic.is_active == True
    ).group_by(Topic.id).all()
    
    result = []
    for topic, count in topics:
        topic_dict = TopicResponse.from_orm(topic).dict()
        topic_dict["question_count"] = count
        result.append(topic_dict)
    
    return result

@router.post("/", response_model=TopicResponse)
def create_topic(
    request: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """
    Create new topic (Admin only)
    """
    topic = Topic(name=request.name, created_by=current_user.id)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic
