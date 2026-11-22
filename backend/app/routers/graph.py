from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..services.graph_service import GraphService

router = APIRouter(prefix="/api/graph", tags=["Graph"])

@router.get("")
def get_graph(
    report_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    return GraphService.get_cytoscape_elements(db, filter_report_id=report_id)

@router.get("/report/{report_id}")
def get_report_graph(
    report_id: int,
    db: Session = Depends(get_db)
):
    return GraphService.get_cytoscape_elements(db, filter_report_id=report_id)
