"""
Main FastAPI application entry point
Handles app initialization, middleware, and route registration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, topics, questions, exam, admin, certificate
from app.core.database import engine, Base

# Create database tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quiz System API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://m1v0sc5c-3000.inc1.devtunnels.ms", "https://quiz-frontend-q69i.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(topics.router, prefix="/api/topics", tags=["Topics"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
app.include_router(exam.router, prefix="/api/exam", tags=["Exam"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(certificate.router, prefix="/api/certificate", tags=["Certificate"])

@app.get("/")
def root():
    return {"message": "Quiz System API is running"}

