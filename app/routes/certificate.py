"""
Certificate generation and email delivery
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.dependencies import require_role
from app.models.models import User, UserScore
from app.schemas.schemas import CertificateRequest
from app.services.certificate_service import generate_certificate_pdf
from app.services.email_service import send_certificate_email

router = APIRouter()

@router.post("/publish")
def publish_certificate(
    request: CertificateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """
    Generate and email certificate to user
    Updates certificate_issued flag
    """
    # Get user score record
    user_score = db.query(UserScore).filter(
        UserScore.id == request.user_score_id,
        UserScore.is_active == True
    ).first()
    
    if not user_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score record not found"
        )
    
    if user_score.certificate_issued:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate already issued"
        )
    
    # Get user and topic details
    user = user_score.user
    topic = user_score.topic
    
    # Calculate grade
    # Assuming questions count from topic
    from app.models.models import Question
    total_questions = db.query(Question).filter(
        Question.topic_id == topic.id,
        Question.is_active == True
    ).count()
    
    percentage = (user_score.score / total_questions * 100) if total_questions > 0 else 0
    
    if percentage >= 90:
        grade = "A"
    elif percentage >= 75:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    else:
        grade = "D"
    
    # Generate PDF certificate
    pdf_path = generate_certificate_pdf(
        user_name=user.name,
        topic_name=topic.name,
        score=user_score.score,
        total=total_questions,
        grade=grade
    )
    
    # Send email
    send_certificate_email(
        recipient_email=user.email,
        recipient_name=user.name,
        topic_name=topic.name,
        pdf_path=pdf_path
    )
    
    # Update certificate_issued flag
    user_score.certificate_issued = True
    user_score.updated_by = current_user.id
    db.commit()
    
    return {
        "message": "Certificate generated and sent successfully",
        "user_email": user.email
    }
