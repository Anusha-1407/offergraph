from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List, Dict, Any

from ..database import get_db
from ..models import Entity, ReportEntity
from ..services.graph_service import GraphService
from ..services.extraction_service import mask_phone, mask_email, mask_upi

router = APIRouter(prefix="/api/entities", tags=["Entities"])

@router.get("")
def list_entities(
    entity_type: Optional[str] = Query(None),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Entity)
    if entity_type and entity_type != "all":
        query = query.filter(Entity.entity_type == entity_type)

    entities = query.limit(limit).all()
    results = []
    for e in entities:
        cnt = db.query(ReportEntity).filter(ReportEntity.entity_id == e.id).count()
        masked = e.display_value
        if e.entity_type == "phone":
            masked = mask_phone(e.display_value)
        elif e.entity_type == "email":
            masked = mask_email(e.display_value)
        elif e.entity_type == "upi":
            masked = mask_upi(e.display_value)

        results.append({
            "id": e.id,
            "entity_type": e.entity_type,
            "display_value": masked,
            "reports_count": cnt,
            "created_at": e.created_at.strftime("%Y-%m-%d") if e.created_at else "N/A"
        })
    return results

@router.get("/search")
def search_entities(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    clean = q.strip().lower()
    entities = db.query(Entity).filter(
        or_(
            Entity.normalized_value.ilike(f"%{clean}%"),
            Entity.display_value.ilike(f"%{clean}%")
        )
    ).limit(20).all()

    results = []
    for e in entities:
        cnt = db.query(ReportEntity).filter(ReportEntity.entity_id == e.id).count()
        masked = e.display_value
        if e.entity_type == "phone":
            masked = mask_phone(e.display_value)
        elif e.entity_type == "email":
            masked = mask_email(e.display_value)
        elif e.entity_type == "upi":
            masked = mask_upi(e.display_value)

        results.append({
            "id": e.id,
            "entity_type": e.entity_type,
            "display_value": masked,
            "reports_count": cnt
        })
    return results

@router.get("/{entity_id}/connections")
def get_entity_connections(entity_id: int, db: Session = Depends(get_db)):
    details = GraphService.get_entity_investigation_details(db, entity_id)
    if "error" in details:
        raise HTTPException(status_code=404, detail="Entity not found")
    return details
