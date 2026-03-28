"""
Admin management routes
Dashboard stats, user management, results viewing
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.auth.dependencies import require_role
from app.core.security import hash_password
from app.models.models import User, Role, Topic, UserScore, Question
from app.schemas.schemas import (
    DashboardStats, UserCreate, UserResponse,
    UserUpdate, UserScoreResponse, CertificateStatusUpdate, ProctoringConfig
)
from app.services.grade_calculator import calculate_grade, calculate_percentage
from app.models.models import CERT_APPROVED, CERT_REJECTED, CERT_IN_REVIEW
from app.services.proctor_config import load_config, save_config

router = APIRouter()

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """
    Get dashboard statistics
    - Total users
    - Total admins
    - Total topics
    - Total exams taken
    """
    # Get role IDs
    user_role = db.query(Role).filter(Role.name == "User").first()
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    
    total_users = db.query(User).filter(
        User.role_id == user_role.id,
        User.is_active == True
    ).count() if user_role else 0
    
    total_admins = db.query(User).filter(
        User.role_id == admin_role.id,
        User.is_active == True
    ).count() if admin_role else 0
    
    total_topics = db.query(Topic).filter(Topic.is_active == True).count()
    total_exams = db.query(UserScore).filter(UserScore.is_active == True).count()
    
    return DashboardStats(
        total_users=total_users,
        total_admins=total_admins,
        total_topics=total_topics,
        total_exams_taken=total_exams
    )

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """
    Get all users (Admin only)
    """
    users = db.query(User).filter(User.is_active == True).all()
    return users

@router.post("/users", response_model=UserResponse)
def create_user(
    request: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """
    Create new user or admin (Admin only)
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        name=request.name,
        email=request.email,
        password=hash_password(request.password),
        role_id=request.role_id,
        created_by=current_user.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    request: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """
    Update user details (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if request.name:
        user.name = request.name
    if request.email:
        # Check email uniqueness
        existing = db.query(User).filter(
            User.email == request.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = request.email
    
    user.updated_by = current_user.id
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """
    Deactivate user (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    user.updated_by = current_user.id
    db.commit()
    return {"message": "User deactivated successfully"}

@router.get("/proctor-config", response_model=ProctoringConfig)
def get_proctor_config(
    current_user: User = Depends(require_role(["Admin"]))
):
    """Get current proctoring configuration."""
    return load_config()


@router.put("/proctor-config", response_model=ProctoringConfig)
def update_proctor_config(
    request: ProctoringConfig,
    current_user: User = Depends(require_role(["Admin"]))
):
    """Update proctoring configuration."""
    return save_config(request.model_dump())


def _build_score_response(score, total_marks):
    return UserScoreResponse(
        id=score.id,
        score=score.score,
        total_marks=total_marks,
        percentage=calculate_percentage(score.score, total_marks),
        grade=calculate_grade(score.score, total_marks),
        certificate_issued=score.certificate_issued,
        certificate_status=score.certificate_status,
        malpractice_detected=score.malpractice_detected or False,
        tab_switch_count=score.tab_switch_count or 0,
        face_violation_count=score.face_violation_count or 0,
        created_at=score.created_at,
        user_id=score.user_id,
        topic_id=score.topic_id,
        user_name=score.user.name,
        topic_name=score.topic.name
    )


@router.get("/results", response_model=List[UserScoreResponse])
def get_all_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Get all exam results with user and topic details"""
    results = db.query(UserScore).filter(UserScore.is_active == True).all()
    response = []
    for score in results:
        total_marks = db.query(Question).filter(
            Question.topic_id == score.topic_id, Question.is_active == True
        ).count()
        response.append(_build_score_response(score, total_marks))
    return response

@router.get("/results/user/{user_id}", response_model=List[UserScoreResponse])
def get_user_results(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Get exam results for specific user"""
    results = db.query(UserScore).filter(
        UserScore.user_id == user_id, UserScore.is_active == True
    ).all()
    response = []
    for score in results:
        total_marks = db.query(Question).filter(
            Question.topic_id == score.topic_id, Question.is_active == True
        ).count()
        response.append(_build_score_response(score, total_marks))
    return response

@router.put("/results/{score_id}/status", response_model=UserScoreResponse)
def update_certificate_status(
    score_id: int,
    request: CertificateStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Approve or reject a certificate (Admin only)"""
    if request.status not in (CERT_APPROVED, CERT_REJECTED, CERT_IN_REVIEW):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'approved', 'rejected', or 'in_review'"
        )
    score = db.query(UserScore).filter(
        UserScore.id == score_id, UserScore.is_active == True
    ).first()
    if not score:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")

    score.certificate_status = request.status
    score.certificate_issued = (request.status == CERT_APPROVED)
    score.updated_by = current_user.id
    db.commit()
    db.refresh(score)

    total_marks = db.query(Question).filter(
        Question.topic_id == score.topic_id, Question.is_active == True
    ).count()
    return _build_score_response(score, total_marks)
