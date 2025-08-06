from database import Base, db_session
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Enum, CheckConstraint, JSON, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class SexType(str, enum.Enum):
    BOY = 'Boy'
    GIRL = 'Girl'
    OTHER = 'Other'

class AgeGroup(Base):
    __tablename__ = 'age_groups'
    age_group_id = Column(Integer, primary_key=True)
    age_range = Column(String(20), unique=True, nullable=False)
    min_age = Column(Integer, nullable=False)  # in months
    max_age = Column(Integer, nullable=False)  # in months
    display_name = Column(String(100), nullable=False)

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    parent_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    children = relationship("Child", back_populates="parent", cascade="all, delete-orphan")

class Child(Base):
    __tablename__ = 'children'
    child_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    child_name = Column(String(100), nullable=False)
    sex = Column(String(10), CheckConstraint("sex IN ('Boy', 'Girl', 'Other')"))
    birth_date = Column(Date, nullable=False)
    age_group_id = Column(Integer, ForeignKey('age_groups.age_group_id'))
    city = Column(String(100))
    state = Column(String(100))
    created_at = Column(DateTime, server_default=func.current_timestamp())

    parent = relationship("User", back_populates="children")
    age_group = relationship("AgeGroup")
    assessments = relationship("AssessmentResult", back_populates="child", cascade="all, delete-orphan")

    @property
    def current_age_group(self):
        """Calculate current age group based on birth date"""
        if not self.birth_date:
            return None
            
        today = datetime.now()
        age_in_months = (today.year - self.birth_date.year) * 12 + (today.month - self.birth_date.month)
        
        # Query the appropriate age group
        age_group = db_session.query(AgeGroup).filter(
            AgeGroup.min_age <= age_in_months,
            AgeGroup.max_age > age_in_months
        ).first()
        
        return age_group if age_group else None

    def update_age_group(self):
        """Update age group if needed"""
        current = self.current_age_group
        if current and (not self.age_group or self.age_group_id != current.age_group_id):
            old_group = self.age_group
            self.age_group = current
            db_session.commit()
            return True, old_group.age_range if old_group else None, current.age_range
        return False, None, None

class AssessmentResult(Base):
    __tablename__ = 'assessment_results'
    result_id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('children.child_id', ondelete='CASCADE'), nullable=False)
    age_group_id = Column(Integer, ForeignKey('age_groups.age_group_id'))
    assessment_date = Column(DateTime, server_default=func.current_timestamp())
    
    # Store user information at time of assessment
    user_info = Column(JSON)
    
    # Store answers for each category
    answers = Column(JSON)  # Intelligence questions answers
    
    # Store scores for each task type
    scores = Column(JSON)  # {'physical': 0-3, 'linguistic': 0-3, 'intelligence': 0-4}
    
    # Task specific results
    physical_task_result = Column(JSON)  # Store physical task performance details
    linguistic_task_result = Column(JSON)  # Store linguistic task performance details
    
    # Overall assessment score
    total_score = Column(Integer)
    
    # Assessment completion status
    is_complete = Column(String(10), default='incomplete')  # 'incomplete', 'complete'
    
    # Store AI-generated report if available
    ai_report = Column(Text)

    child = relationship("Child", back_populates="assessments")
    age_group = relationship("AgeGroup")

class AssessmentSession(Base):
    """Track assessment sessions for better user experience"""
    __tablename__ = 'assessment_sessions'
    session_id = Column(String(36), primary_key=True)  # UUID
    child_id = Column(Integer, ForeignKey('children.child_id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    
    # Session progress tracking
    current_task = Column(String(20))  # 'info', 'physical', 'linguistic', 'intelligence', 'complete'
    task_results = Column(JSON)  # Store temporary results during session
    
    # Session timestamps
    started_at = Column(DateTime, server_default=func.current_timestamp())
    last_activity = Column(DateTime, server_default=func.current_timestamp())
    completed_at = Column(DateTime)
    
    # Session status
    status = Column(String(20), default='active')  # 'active', 'completed', 'abandoned'

    child = relationship("Child")
    user = relationship("User")


class QuestionResponse(Base):
    """Store detailed responses for each question"""
    __tablename__ = 'question_responses'
    response_id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('assessment_results.result_id', ondelete='CASCADE'), nullable=False)
    child_id = Column(Integer, ForeignKey('children.child_id', ondelete='CASCADE'), nullable=False)
    
    # Question details
    assessment_type = Column(String(20), CheckConstraint("assessment_type IN ('intelligence', 'physical', 'linguistic')"), nullable=False)
    question_id = Column(String(50), nullable=False)
    question_text = Column(Text, nullable=False)
    
    # Answer details
    child_answer = Column(Text)
    correct_answer = Column(Text)
    is_correct = Column(String(10), default='false')  # 'true', 'false', 'partial'
    
    # Performance metrics
    response_time_seconds = Column(Integer)
    difficulty_level = Column(Integer, default=1)
    attempts = Column(Integer, default=1)
    hints_used = Column(Integer, default=0)
    ai_confidence_score = Column(Float)
    
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships
    assessment_result = relationship("AssessmentResult")
    child = relationship("Child")


class AITaskResponse(Base):
    """Store detailed responses for AI tasks (physical/linguistic)"""
    __tablename__ = 'ai_task_responses'
    ai_response_id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('assessment_results.result_id', ondelete='CASCADE'), nullable=False)
    child_id = Column(Integer, ForeignKey('children.child_id', ondelete='CASCADE'), nullable=False)
    
    # Task details
    task_type = Column(String(30), nullable=False)  # 'raise_hands', 'say_mama', etc.
    task_name = Column(String(100), nullable=False)
    
    # Performance metrics
    success_count = Column(Integer, default=0)
    total_attempts = Column(Integer, default=0)
    completion_time_seconds = Column(Integer)
    success_rate = Column(Float)
    
    # AI feedback and results
    ai_feedback = Column(Text)
    was_completed = Column(String(10), default='false')  # 'true', 'false'
    was_skipped = Column(String(10), default='false')   # 'true', 'false'
    
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships
    assessment_result = relationship("AssessmentResult")
    child = relationship("Child")

