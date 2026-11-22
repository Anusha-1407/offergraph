import networkx as nx
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Report, Entity, ReportEntity
from .extraction_service import mask_phone, mask_email, mask_upi

class GraphService:
    @staticmethod
    def build_networkx_graph(db: Session) -> nx.Graph:
        """
        Builds a NetworkX undirected graph from reports and entities stored in DB.
        """
        G = nx.Graph()

        # Add report nodes
        reports = db.query(Report).all()
        for r in reports:
            G.add_node(
                f"report_{r.id}",
                node_type="report",
                label=f"Report #{r.id}: {r.company_name or 'Unspecified'}",
                risk_score=r.risk_score,
                risk_category=r.risk_category,
                db_id=r.id,
                created_at=r.created_at.isoformat() if r.created_at else "",
                description=r.description[:100] + "..." if len(r.description) > 100 else r.description,
                report_type=r.report_type
            )

        # Add entity nodes
        entities = db.query(Entity).all()
        for e in entities:
            # Mask sensitive display values
            masked = e.display_value
            if e.entity_type == "phone":
                masked = mask_phone(e.display_value)
            elif e.entity_type == "email":
                masked = mask_email(e.display_value)
            elif e.entity_type == "upi":
                masked = mask_upi(e.display_value)

            G.add_node(
                f"entity_{e.id}",
                node_type=e.entity_type,
                label=masked,
                raw_value=e.normalized_value,
                display_value=masked,
                db_id=e.id,
                created_at=e.created_at.isoformat() if e.created_at else ""
            )

        # Add relationships
        report_entities = db.query(ReportEntity).all()
        for re_item in report_entities:
            report_node = f"report_{re_item.report_id}"
            entity_node = f"entity_{re_item.entity_id}"
            if report_node in G and entity_node in G:
                G.add_edge(
                    report_node,
                    entity_node,
                    id=f"edge_r{re_item.report_id}_e{re_item.entity_id}",
                    relationship=re_item.relationship_type,
                    label=re_item.relationship_type.replace("_", " ")
                )

        return G

    @staticmethod
    def get_cytoscape_elements(db: Session, filter_report_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Exports graph data in Cytoscape.js compatible JSON format.
        """
        G = GraphService.build_networkx_graph(db)

        if filter_report_id:
            # Filter graph to subgraph of nodes connected to this report
            target = f"report_{filter_report_id}"
            if target in G:
                neighbors = set(nx.single_source_shortest_path_length(G, target, cutoff=2).keys())
                G = G.subgraph(neighbors).copy()
            else:
                G = nx.Graph()

        # Count connected components
        clusters = list(nx.connected_components(G))
        cluster_count = len(clusters)

        nodes = []
        edges = []

        # Color mapping for frontend
        type_colors = {
            "report": "#ef4444",      # High risk / report
            "company": "#38bdf8",     # Cyan/blue
            "recruiter": "#a855f7",   # Purple
            "phone": "#f59e0b",       # Amber
            "email": "#10b981",       # Emerald
            "domain": "#ec4899",      # Pink
            "upi": "#e11d48",         # Crimson
        }

        for node_id, data in G.nodes(data=True):
            node_type = data.get("node_type", "entity")
            degree = G.degree(node_id)
            nodes.append({
                "data": {
                    "id": node_id,
                    "label": data.get("label", node_id),
                    "type": node_type,
                    "color": type_colors.get(node_type, "#94a3b8"),
                    "risk_score": data.get("risk_score", 0),
                    "risk_category": data.get("risk_category", "N/A"),
                    "db_id": data.get("db_id"),
                    "degree": degree,
                    "created_at": data.get("created_at", ""),
                    "description": data.get("description", ""),
                    "display_value": data.get("display_value", data.get("label", ""))
                }
            })

        for u, v, edge_data in G.edges(data=True):
            edges.append({
                "data": {
                    "id": edge_data.get("id", f"edge_{u}_{v}"),
                    "source": u,
                    "target": v,
                    "label": edge_data.get("label", "CONNECTED_TO"),
                    "relationship_type": edge_data.get("relationship", "CONNECTED")
                }
            })

        return {
            "elements": {
                "nodes": nodes,
                "edges": edges
            },
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "clusters_count": cluster_count
            }
        }

    @staticmethod
    def get_entity_investigation_details(db: Session, entity_id: int) -> Dict[str, Any]:
        """
        Returns deep investigation details when a user clicks an entity node.
        """
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if not entity:
            return {"error": "Entity not found"}

        # Find all linked reports
        links = db.query(ReportEntity).filter(ReportEntity.entity_id == entity_id).all()
        report_ids = [l.report_id for l in links]

        reports = db.query(Report).filter(Report.id.in_(report_ids)).all() if report_ids else []

        connected_companies = set()
        connected_recruiters = set()
        dates = []

        for r in reports:
            if r.company_name:
                connected_companies.add(r.company_name)
            if r.recruiter_name:
                connected_recruiters.add(r.recruiter_name)
            if r.created_at:
                dates.append(r.created_at)

        # Mask display value
        masked = entity.display_value
        if entity.entity_type == "phone":
            masked = mask_phone(entity.display_value)
        elif entity.entity_type == "email":
            masked = mask_email(entity.display_value)
        elif entity.entity_type == "upi":
            masked = mask_upi(entity.display_value)

        return {
            "entity_id": entity.id,
            "entity_type": entity.entity_type,
            "masked_identifier": masked,
            "linked_reports_count": len(reports),
            "connected_companies": list(connected_companies),
            "related_recruiters": list(connected_recruiters),
            "first_reported_date": min(dates).strftime("%Y-%m-%d %H:%M") if dates else "N/A",
            "last_reported_date": max(dates).strftime("%Y-%m-%d %H:%M") if dates else "N/A",
            "supporting_reports": [
                {
                    "report_id": r.id,
                    "company_name": r.company_name,
                    "risk_score": r.risk_score,
                    "risk_category": r.risk_category,
                    "created_at": r.created_at.strftime("%Y-%m-%d") if r.created_at else "N/A",
                    "report_type": r.report_type
                }
                for r in reports
            ]
        }
