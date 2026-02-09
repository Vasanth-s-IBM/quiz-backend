"""
Exam flow routes: start exam, submit answers
Handles malpractice detection and score calculation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
import json
from app.core.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.models.models import User, Topic, Question, UserScore
from app.schemas.schemas import (
    ExamStartRequest, ExamStartResponse, ExamSubmitRequest, 
    ExamSubmitResponse, QuestionResponse
)
from app.config import settings

router = APIRouter()

# In-memory store for active exam sessions (use Redis in production)
active_exams = {}

@router.post("/start", response_model=ExamStartResponse)
def start_exam(
    request: ExamStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["User"]))
):
    """
    Start exam for a topic
    - Checks if user already completed this topic
    - Fetches all active questions
    - Creates exam session
    """
    # Check if user already took this exam
    existing_score = db.query(UserScore).filter(
        UserScore.user_id == current_user.id,
        UserScore.topic_id == request.topic_id,
        UserScore.is_active == True
    ).first()
    
    if existing_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already completed this exam"
        )
    
    # Get topic
    topic = db.query(Topic).filter(
        Topic.id == request.topic_id,
        Topic.is_active == True
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Get all questions for this topic
    questions = db.query(Question).filter(
        Question.topic_id == request.topic_id,
        Question.is_active == True
    ).all()
    
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No questions available for this topic"
        )
    
    # Create exam session
    exam_session_id = str(uuid.uuid4())
    active_exams[exam_session_id] = {
        "user_id": current_user.id,
        "topic_id": request.topic_id,
        "questions": {q.id: q.correct_answer for q in questions}
    }
    
    # Return questions without correct answers
    question_responses = [
        QuestionResponse(
            id=q.id,
            uuid=q.uuid,
            question_text=q.question_text,
            options=json.loads(q.options) if isinstance(q.options, str) else q.options,
            question_type=q.question_type
        ) for q in questions
    ]
    
    return ExamStartResponse(
        exam_session_id=exam_session_id,
        questions=question_responses,
        duration_minutes=settings.EXAM_DURATION_MINUTES,
        total_questions=len(questions)
    )

@router.post("/submit", response_model=ExamSubmitResponse)
def submit_exam(
    request: ExamSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["User"]))
):
    """
    Submit exam answers
    - Validates answers
    - Detects malpractice (tab switches)
    - Calculates score
    - Saves to database
    """
    # Check malpractice
    malpractice_detected = request.tab_switch_count >= settings.MAX_TAB_SWITCHES
    
    # Get questions for this topic
    questions = db.query(Question).filter(
        Question.topic_id == request.topic_id,
        Question.is_active == True
    ).all()
    
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No questions found for this topic"
        )
    
    # Calculate score
    correct_answers = {q.id: q.correct_answer for q in questions}
    score = 0
    
    for answer in request.answers:
        if answer.question_id in correct_answers:
            if answer.selected_answer == correct_answers[answer.question_id]:
                score += 1
    
    # Save score to database
    user_score = UserScore(
        user_id=current_user.id,
        topic_id=request.topic_id,
        score=score,
        created_by=current_user.id
    )
    db.add(user_score)
    db.commit()
    
    total_questions = len(questions)
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    message = "Quiz completed. Certificate will be emailed shortly."
    if malpractice_detected:
        message = "Exam auto-submitted due to malpractice detection. Certificate will be emailed shortly."
    
    return ExamSubmitResponse(
        score=score,
        total_questions=total_questions,
        percentage=round(percentage, 2),
        malpractice_detected=malpractice_detected,
        message=message
    )
