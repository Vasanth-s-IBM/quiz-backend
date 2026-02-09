"""
Database initialization script
Creates roles and admin user
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.models import Base, Role, User, Topic, Question
from app.core.security import hash_password
import json

def init_database():
    """Initialize database with roles and admin user"""
    # Create tables
    # Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if roles exist
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        user_role = db.query(Role).filter(Role.name == "User").first()
        
        # Create roles if not exist
        if not admin_role:
            admin_role = Role(name="Admin")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("✓ Admin role created")
        
        if not user_role:
            user_role = Role(name="User")
            db.add(user_role)
            db.commit()
            db.refresh(user_role)
            print("✓ User role created")
        
        # Create default admin if not exists
        admin_user = db.query(User).filter(User.email == "admin@quiz.com").first()
        if not admin_user:
            admin_user = User(
                name="Admin User",
                email="admin@quiz.com",
                password=hash_password("admin123"),
                role_id=admin_role.id
            )
            db.add(admin_user)
            db.commit()
            print("✓ Default admin created (email: admin@quiz.com, password: admin123)")
        
        # Create test user if not exists
        test_user = db.query(User).filter(User.email == "user@quiz.com").first()
        if not test_user:
            test_user = User(
                name="Test User",
                email="user@quiz.com",
                password=hash_password("user123"),
                role_id=user_role.id
            )
            db.add(test_user)
            db.commit()
            print("✓ Test user created (email: user@quiz.com, password: user123)")
        
        # Create sample topics
        topics_data = [
            "JavaScript Basics",
            "Python Programming",
            "Database Fundamentals",
            "Web Development",
            "Data Structures"
        ]
        
        for topic_name in topics_data:
            existing = db.query(Topic).filter(Topic.name == topic_name).first()
            if not existing:
                topic = Topic(name=topic_name)
                db.add(topic)
        db.commit()
        print("✓ Sample topics created")
        
        # Create sample questions for JavaScript
        js_topic = db.query(Topic).filter(Topic.name == "JavaScript Basics").first()
        if js_topic:
            existing_questions = db.query(Question).filter(Question.topic_id == js_topic.id).count()
            if existing_questions == 0:
                questions_data = [
                    {
                        "question_text": "What is JavaScript?",
                        "options": ["A programming language", "A coffee brand", "A framework", "A database"],
                        "correct_answer": "A programming language"
                    },
                    {
                        "question_text": "Which keyword is used to declare a variable in JavaScript?",
                        "options": ["var", "int", "string", "variable"],
                        "correct_answer": "var"
                    },
                    {
                        "question_text": "What does DOM stand for?",
                        "options": ["Document Object Model", "Data Object Model", "Digital Object Model", "Document Oriented Model"],
                        "correct_answer": "Document Object Model"
                    },
                    {
                        "question_text": "Which method is used to parse a string to an integer?",
                        "options": ["parseInt()", "parseInteger()", "toInt()", "convertInt()"],
                        "correct_answer": "parseInt()"
                    },
                    {
                        "question_text": "What is the output of: typeof null?",
                        "options": ["object", "null", "undefined", "number"],
                        "correct_answer": "object"
                    },
                    {
                        "question_text": "Which operator is used for strict equality?",
                        "options": ["===", "==", "=", "!="],
                        "correct_answer": "==="
                    },
                    {
                        "question_text": "What is a closure in JavaScript?",
                        "options": ["A function with access to outer scope", "A loop structure", "A data type", "An operator"],
                        "correct_answer": "A function with access to outer scope"
                    },
                    {
                        "question_text": "Which method adds an element to the end of an array?",
                        "options": ["push()", "pop()", "shift()", "unshift()"],
                        "correct_answer": "push()"
                    },
                    {
                        "question_text": "What is the purpose of 'use strict'?",
                        "options": ["Enable strict mode", "Import modules", "Define constants", "Create classes"],
                        "correct_answer": "Enable strict mode"
                    },
                    {
                        "question_text": "Which keyword is used to create a constant?",
                        "options": ["const", "let", "var", "constant"],
                        "correct_answer": "const"
                    }
                ]
                
                for q_data in questions_data:
                    question = Question(
                        question_text=q_data["question_text"],
                        options=json.dumps(q_data["options"]),
                        question_type="multiple_choice",
                        correct_answer=q_data["correct_answer"],
                        topic_id=js_topic.id
                    )
                    db.add(question)
                db.commit()
                print("✓ Sample questions created for JavaScript Basics")
        
        print("\n✓ Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
