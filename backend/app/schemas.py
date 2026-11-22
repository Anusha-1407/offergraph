from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import datetime

# Entity schemas
class EntityBase(BaseModel):
    entity_type: str
    normalized_value: str
    display_value: str

class EntityResponse(EntityBase):
    id: int
    created_at: datetime.datetime
    report_count: Optional[int] = 0

    class Config:
        from_attributes = True

# Report schemas
class ReportCreate(BaseModel):
    company_name: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    phone_number: Optional[str] = None
    website: Optional[str] = None
    upi_id: Optional[str] = None
    job_role: Optional[str] = None
    description: str
    report_type: str = "Registration fee scam"
    evidence_text: Optional[str] = None

class ReportResponse(BaseModel):
    id: int
    company_name: Optional[str] = None
    recruiter_name: Optional[str] = None
    description: str
    job_role: Optional[str] = None
    risk_score: float
    risk_category: str
    report_type: str
    verification_status: str
    created_at: datetime.datetime
    connected_entities: Optional[List[Dict[str, Any]]] = []

    class Config:
        from_attributes = True

# Analysis schemas
class AnalysisRequest(BaseModel):
    text: Optional[str] = None

class ExtractedEntities(BaseModel):
    company_name: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_emails: List[str] = []
    phone_numbers: List[str] = []
    website_urls: List[str] = []
    domains: List[str] = []
    upi_ids: List[str] = []
    payment_requests: List[Dict[str, Any]] = []
    salary_claims: List[str] = []
    job_role: Optional[str] = None
    internship_duration: Optional[str] = None
    location: Optional[str] = None

class RiskIndicator(BaseModel):
    code: str
    title: str
    points: int
    description: str
    evidence_snippet: Optional[str] = None

class AnalysisResponse(BaseModel):
    analysis_id: Optional[int] = None
    risk_score: float
    risk_category: str
    company_name: Optional[str] = None
    extracted_entities: ExtractedEntities
    suspicious_indicators: List[RiskIndicator]
    matched_previous_reports: List[Dict[str, Any]] = []
    connected_suspicious_entities: List[Dict[str, Any]] = []
    ai_explanation: str
    ai_mode: str # 'live' or 'demo'
    recommended_verification_steps: List[str]

# Graph schemas
class GraphNode(BaseModel):
    id: str
    label: str
    type: str # company, recruiter, phone, email, domain, upi, report
    risk_score: Optional[float] = None
    risk_category: Optional[str] = None
    report_count: Optional[int] = 1
    raw_data: Optional[Dict[str, Any]] = None

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str
    relationship_type: str

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    stats: Dict[str, Any]

# Chat schemas
class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    session_id: str
    role: str
    message: str
    ai_mode: str
    tool_calls_executed: List[str] = []
    evidence_references: List[Dict[str, Any]] = []
    suggested_actions: List[str] = []

# Dashboard stats schema
class DashboardStats(BaseModel):
    total_reports: int
    total_suspicious_incidents: int
    high_risk_reports: int
    connected_entities: int
    suspicious_clusters_count: int
    risk_distribution: Dict[str, int]
    top_entities: Dict[str, List[Dict[str, Any]]]
    is_demo_data: bool
