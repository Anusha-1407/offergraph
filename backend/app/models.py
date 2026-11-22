import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("ChatbotSession", back_populates="user")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), index=True, nullable=True)
    recruiter_name = Column(String(255), index=True, nullable=True)
    description = Column(Text, nullable=False)
    job_role = Column(String(255), nullable=True)
    risk_score = Column(Float, default=0.0)
    risk_category = Column(String(50), default="Low Risk") # Low Risk, Medium Risk, High Risk
    report_type = Column(String(100), default="Registration fee scam")
    verification_status = Column(String(50), default="Unverified Submission") # Unverified Submission, Community Corroborated, Verified Pattern
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    report_entities = relationship("ReportEntity", back_populates="report", cascade="all, delete-orphan")
    evidence_items = relationship("Evidence", back_populates="report", cascade="all, delete-orphan")

class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), index=True, nullable=False) # company, recruiter, phone, email, domain, upi
    normalized_value = Column(String(255), index=True, nullable=False)
    display_value = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    report_entities = relationship("ReportEntity", back_populates="entity")

    __table_args__ = (
        Index("idx_entity_type_normalized", "entity_type", "normalized_value", unique=True),
    )

class ReportEntity(Base):
    __tablename__ = "report_entities"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)
    relationship_type = Column(String(100), default="CONTAINS") # MENTIONS_COMPANY, USES_PHONE, CONTAINS_EMAIL, DEMANDS_UPI, MENTIONS_DOMAIN, REPRESENTS_RECRUITER

    report = relationship("Report", back_populates="report_entities")
    entity = relationship("Entity", back_populates="report_entities")

    __table_args__ = (
        Index("idx_report_entity_rel", "report_id", "entity_id", "relationship_type", unique=True),
    )

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    extracted_data = Column(Text, nullable=False) # JSON encoded string
    risk_score = Column(Float, default=0.0)
    risk_category = Column(String(50), default="Low Risk")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    evidence_type = Column(String(50), default="text") # pdf, txt, image, text
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    report = relationship("Report", back_populates="evidence_items")

class ChatbotSession(Base):
    __tablename__ = "chatbot_sessions"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatbotMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatbotMessage.created_at")

class ChatbotMessage(Base):
    __tablename__ = "chatbot_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("chatbot_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False) # user, assistant, system, tool
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("ChatbotSession", back_populates="messages")
