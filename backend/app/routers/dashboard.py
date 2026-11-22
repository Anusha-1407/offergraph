from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, Any, List
import networkx as nx

from ..database import get_db
from ..models import Report, Entity, ReportEntity, User
from ..schemas import DashboardStats
from ..services.graph_service import GraphService
from ..services.extraction_service import mask_phone, mask_email, mask_upi

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_reports = db.query(Report).count()
    high_risk_reports = db.query(Report).filter(Report.risk_category == "High Risk").count()
    med_risk_reports = db.query(Report).filter(Report.risk_category == "Medium Risk").count()
    low_risk_reports = db.query(Report).filter(Report.risk_category == "Low Risk").count()

    connected_entities = db.query(Entity).count()

    # NetworkX cluster detection
    G = GraphService.build_networkx_graph(db)
    clusters = list(nx.connected_components(G))
    cluster_count = len(clusters)

    # Top reported entities by frequency in report_entities
    top_phones = (
        db.query(Entity.display_value, func.count(ReportEntity.id).label("count"))
        .join(ReportEntity, Entity.id == ReportEntity.entity_id)
        .filter(Entity.entity_type == "phone")
        .group_by(Entity.id)
        .order_by(desc("count"))
        .limit(5)
        .all()
    )

    top_emails = (
        db.query(Entity.display_value, func.count(ReportEntity.id).label("count"))
        .join(ReportEntity, Entity.id == ReportEntity.entity_id)
        .filter(Entity.entity_type == "email")
        .group_by(Entity.id)
        .order_by(desc("count"))
        .limit(5)
        .all()
    )

    top_domains = (
        db.query(Entity.display_value, func.count(ReportEntity.id).label("count"))
        .join(ReportEntity, Entity.id == ReportEntity.entity_id)
        .filter(Entity.entity_type == "domain")
        .group_by(Entity.id)
        .order_by(desc("count"))
        .limit(5)
        .all()
    )

    top_upis = (
        db.query(Entity.display_value, func.count(ReportEntity.id).label("count"))
        .join(ReportEntity, Entity.id == ReportEntity.entity_id)
        .filter(Entity.entity_type == "upi")
        .group_by(Entity.id)
        .order_by(desc("count"))
        .limit(5)
        .all()
    )

    return {
        "total_reports": total_reports,
        "total_suspicious_incidents": total_reports,
        "high_risk_reports": high_risk_reports,
        "medium_risk_reports": med_risk_reports,
        "low_risk_reports": low_risk_reports,
        "connected_entities": connected_entities,
        "suspicious_clusters_count": cluster_count,
        "risk_distribution": {
            "Low Risk": low_risk_reports,
            "Medium Risk": med_risk_reports,
            "High Risk": high_risk_reports,
        },
        "top_entities": {
            "phones": [{"value": mask_phone(p[0]), "count": p[1]} for p in top_phones],
            "emails": [{"value": mask_email(e[0]), "count": e[1]} for e in top_emails],
            "domains": [{"value": d[0], "count": d[1]} for d in top_domains],
            "upis": [{"value": mask_upi(u[0]), "count": u[1]} for u in top_upis],
        },
        "is_demo_data": True
    }

@router.get("/recent-reports")
def get_recent_reports(limit: int = 6, db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(desc(Report.created_at)).limit(limit).all()
    results = []
    for r in reports:
        results.append({
            "id": r.id,
            "company_name": r.company_name or "Unspecified Entity",
            "recruiter_name": r.recruiter_name or "Not Specified",
            "risk_score": r.risk_score,
            "risk_category": r.risk_category,
            "report_type": r.report_type,
            "verification_status": r.verification_status,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "N/A",
            "snippet": r.description[:110] + "..." if len(r.description) > 110 else r.description
        })
    return results

@router.post("/reset-demo-data")
def reset_demo_data(db: Session = Depends(get_db)):
    from ..seed import seed_database
    seed_database(db, force_reset=True)
    return {"message": "Database reset to synthetic demonstration data successfully.", "status": "ok"}
