"""
User profile routes — own results and certificate download
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.auth.dependencies import require_role
from app.models.models import User, UserScore, Question, CERT_APPROVED
from app.schemas.schemas import UserScoreResponse
from app.services.grade_calculator import calculate_grade, calculate_percentage
from app.services.certificate_service import generate_certificate_pdf
import os

router = APIRouter()


def _build_score_response(score, total_marks):
    return UserScoreResponse(
        id=score.id,
        score=score.score,
        total_marks=total_marks,
        percentage=calculate_percentage(score.score, total_marks),
        grade=calculate_grade(score.score, total_marks),
        certificate_issued=score.certificate_issued,
        certificate_status=score.certificate_status,
        created_at=score.created_at,
        user_id=score.user_id,
        topic_id=score.topic_id,
        user_name=score.user.name,
        topic_name=score.topic.name
    )


@router.get("/profile", response_model=List[UserScoreResponse])
def get_my_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["User"]))
):
    """Return all exam results for the logged-in user."""
    scores = db.query(UserScore).filter(
        UserScore.user_id == current_user.id,
        UserScore.is_active == True
    ).order_by(UserScore.created_at.desc()).all()

    response = []
    for score in scores:
        total_marks = db.query(Question).filter(
            Question.topic_id == score.topic_id,
            Question.is_active == True
        ).count()
        response.append(_build_score_response(score, total_marks))
    return response


@router.get("/certificate/download/{score_id}")
def download_certificate(
    score_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["User"]))
):
    """Download certificate PDF — only allowed when status is approved."""
    score = db.query(UserScore).filter(
        UserScore.id == score_id,
        UserScore.user_id == current_user.id,
        UserScore.is_active == True
    ).first()

    if not score:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")

    if score.certificate_status != CERT_APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Certificate is not approved yet"
        )

    total_marks = db.query(Question).filter(
        Question.topic_id == score.topic_id,
        Question.is_active == True
    ).count()

    grade = calculate_grade(score.score, total_marks)

    pdf_path = generate_certificate_pdf(
        user_name=score.user.name,
        topic_name=score.topic.name,
        score=score.score,
        total=total_marks,
        grade=grade
    )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"certificate_{score.topic.name.replace(' ', '_')}.pdf"
    )
