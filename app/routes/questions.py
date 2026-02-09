"""
Question management routes (Admin only)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.auth.dependencies import require_role
from app.models.models import User, Question
from app.schemas.schemas import QuestionCreate, QuestionAdmin

router = APIRouter()

@router.post("/", response_model=QuestionAdmin)
def create_question(
    request: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """
    Create new question (Admin only)
    """
    import json
    question = Question(
        question_text=request.question_text,
        options = "{" + ",".join(f'"{o}"' for o in request.options) + "}",  # Convert list to JSON string
        question_type=request.question_type,
        correct_answer=request.correct_answer,
        topic_id=request.topic_id,
        created_by=current_user.id
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

@router.get("/topic/{topic_id}", response_model=List[QuestionAdmin])
def get_questions_by_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """
    Get all questions for a topic (Admin only)
    """
    questions = db.query(Question).filter(
        Question.topic_id == topic_id,
        Question.is_active == True
    ).all()
    return questions
