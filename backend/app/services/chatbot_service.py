import json
import re
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from ..models import Report, Entity, ReportEntity, ChatbotSession, ChatbotMessage
from .extraction_service import (
    ExtractionService, normalize_phone, mask_phone, normalize_email,
    mask_email, normalize_upi, mask_upi, normalize_domain
)
from .risk_engine import RiskEngine
from .ai_service import AIService, OPENAI_API_KEY, OPENAI_MODEL

class ChatbotTools:
    @staticmethod
    def search_entity(db: Session, identifier: str) -> Dict[str, Any]:
        """Searches for an entity by phone, email, UPI, domain, or name."""
        clean = identifier.strip().lower()
        norm_p = normalize_phone(clean)
        norm_e = normalize_email(clean)
        norm_u = normalize_upi(clean)
        norm_d = normalize_domain(clean)

        entities = db.query(Entity).filter(
            or_(
                Entity.normalized_value.in_([clean, norm_p, norm_e, norm_u, norm_d]),
                Entity.display_value.ilike(f"%{clean}%")
            )
        ).all()

        results = []
        for e in entities:
            # count reports
            cnt = db.query(ReportEntity).filter(ReportEntity.entity_id == e.id).count()
            # mask
            masked = e.display_value
            if e.entity_type == "phone":
                masked = mask_phone(e.display_value)
            elif e.entity_type == "email":
                masked = mask_email(e.display_value)
            elif e.entity_type == "upi":
                masked = mask_upi(e.display_value)

            results.append({
                "entity_id": e.id,
                "entity_type": e.entity_type,
                "masked_value": masked,
                "connected_reports_count": cnt
            })

        return {
            "query": identifier,
            "total_matches": len(results),
            "entities": results
        }

    @staticmethod
    def get_connected_reports(db: Session, identifier: str) -> Dict[str, Any]:
        """Finds all incident reports linked to a phone, email, or UPI identifier."""
        search_res = ChatbotTools.search_entity(db, identifier)
        if not search_res["entities"]:
            return {
                "identifier": identifier,
                "found": False,
                "reports": [],
                "message": f"No previous incident reports found linking to '{identifier}' in the database."
            }

        entity_ids = [e["entity_id"] for e in search_res["entities"]]
        report_links = db.query(ReportEntity).filter(ReportEntity.entity_id.in_(entity_ids)).all()
        report_ids = list(set([rl.report_id for rl in report_links]))

        reports = db.query(Report).filter(Report.id.in_(report_ids)).all()
        rep_list = []
        for r in reports:
            rep_list.append({
                "report_id": r.id,
                "company_name": r.company_name,
                "recruiter_name": r.recruiter_name,
                "risk_score": r.risk_score,
                "risk_category": r.risk_category,
                "report_type": r.report_type,
                "date": r.created_at.strftime("%Y-%m-%d") if r.created_at else "N/A",
                "summary": r.description[:140] + "..." if len(r.description) > 140 else r.description
            })

        return {
            "identifier": identifier,
            "found": True,
            "reports_count": len(rep_list),
            "reports": rep_list
        }

    @staticmethod
    def get_report_details(db: Session, report_id: int) -> Dict[str, Any]:
        """Fetches full details of a specific report and all attached entities."""
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return {"error": f"Report #{report_id} does not exist in the database."}

        links = db.query(ReportEntity).filter(ReportEntity.report_id == report_id).all()
        connected = []
        for l in links:
            e = db.query(Entity).filter(Entity.id == l.entity_id).first()
            if e:
                masked = e.display_value
                if e.entity_type == "phone":
                    masked = mask_phone(e.display_value)
                elif e.entity_type == "email":
                    masked = mask_email(e.display_value)
                elif e.entity_type == "upi":
                    masked = mask_upi(e.display_value)
                connected.append({
                    "entity_type": e.entity_type,
                    "masked_value": masked,
                    "relationship": l.relationship_type
                })

        return {
            "report_id": report.id,
            "company_name": report.company_name,
            "recruiter_name": report.recruiter_name,
            "job_role": report.job_role,
            "risk_score": report.risk_score,
            "risk_category": report.risk_category,
            "report_type": report.report_type,
            "verification_status": report.verification_status,
            "description": report.description,
            "created_at": report.created_at.strftime("%Y-%m-%d %H:%M") if report.created_at else "N/A",
            "connected_entities": connected
        }

    @staticmethod
    def search_company(db: Session, company_name: str) -> Dict[str, Any]:
        """Queries reports and entities associated with a company name."""
        comp_clean = company_name.strip()
        reports = db.query(Report).filter(Report.company_name.ilike(f"%{comp_clean}%")).all()
        rep_data = []
        for r in reports:
            rep_data.append({
                "report_id": r.id,
                "company_name": r.company_name,
                "risk_score": r.risk_score,
                "risk_category": r.risk_category,
                "report_type": r.report_type,
                "date": r.created_at.strftime("%Y-%m-%d") if r.created_at else "N/A"
            })

        return {
            "company_query": company_name,
            "matched_reports_count": len(rep_data),
            "reports": rep_data
        }

    @staticmethod
    def get_network_connections(db: Session, report_id: int) -> Dict[str, Any]:
        """Finds other reports that share any entity with the specified report."""
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return {"error": f"Report #{report_id} not found"}

        entity_ids = [l.entity_id for l in db.query(ReportEntity).filter(ReportEntity.report_id == report_id).all()]
        if not entity_ids:
            return {"report_id": report_id, "shared_reports": []}

        # Find other reports sharing these entity IDs
        shared_links = db.query(ReportEntity).filter(
            ReportEntity.entity_id.in_(entity_ids),
            ReportEntity.report_id != report_id
        ).all()

        shared_by_report: Dict[int, List[Dict[str, Any]]] = {}
        for link in shared_links:
            e = db.query(Entity).filter(Entity.id == link.entity_id).first()
            if link.report_id not in shared_by_report:
                shared_by_report[link.report_id] = []
            if e:
                masked = e.display_value
                if e.entity_type == "phone":
                    masked = mask_phone(e.display_value)
                elif e.entity_type == "email":
                    masked = mask_email(e.display_value)
                elif e.entity_type == "upi":
                    masked = mask_upi(e.display_value)
                shared_by_report[link.report_id].append({
                    "entity_type": e.entity_type,
                    "masked_identifier": masked
                })

        connections = []
        for other_id, shared_ents in shared_by_report.items():
            other_rep = db.query(Report).filter(Report.id == other_id).first()
            if other_rep:
                connections.append({
                    "connected_report_id": other_rep.id,
                    "company_name": other_rep.company_name,
                    "risk_score": other_rep.risk_score,
                    "shared_entities": shared_ents
                })

        return {
            "source_report_id": report_id,
            "total_connected_reports": len(connections),
            "connected_reports": connections
        }

    @staticmethod
    def analyse_offer_text(text: str) -> Dict[str, Any]:
        """Runs the complete extraction and risk engine on arbitrary text."""
        extracted = ExtractionService.extract_all(text)
        score, cat, indicators = RiskEngine.evaluate(text, extracted)
        return {
            "extracted": extracted,
            "risk_score": score,
            "risk_category": cat,
            "indicators": [ind.dict() for ind in indicators]
        }

class ChatbotService:
    @staticmethod
    def process_chat(
        db: Session,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Ensure session exists
        if not session_id:
            session_id = str(uuid.uuid4())

        session_record = db.query(ChatbotSession).filter(ChatbotSession.id == session_id).first()
        if not session_record:
            session_record = ChatbotSession(id=session_id)
            db.add(session_record)
            db.commit()

        # Save user message
        user_msg = ChatbotMessage(session_id=session_id, role="user", message=message)
        db.add(user_msg)
        db.commit()

        # Check if live OpenAI is available
        if AIService.is_live_available():
            try:
                response_data = ChatbotService._process_with_openai(db, message, session_id, context)
            except Exception as e:
                response_data = ChatbotService._process_with_deterministic_engine(db, message, context)
                response_data["message"] = f"*[Note: Live OpenAI call error ({str(e)[:40]}). Switched to OfferGraph Investigator Demo Mode]*\n\n" + response_data["message"]
        else:
            response_data = ChatbotService._process_with_deterministic_engine(db, message, context)

        # Save assistant message
        assistant_msg = ChatbotMessage(
            session_id=session_id,
            role="assistant",
            message=response_data["message"]
        )
        db.add(assistant_msg)
        db.commit()

        response_data["session_id"] = session_id
        return response_data

    @staticmethod
    def _process_with_deterministic_engine(
        db: Session,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        High-fidelity deterministic investigation engine.
        Parses intent, queries DB tools, extracts entities, and creates evidence-backed citations.
        """
        msg_lower = message.lower().strip()
        tools_executed = []
        evidence_references = []
        suggested_actions = [
            "Check another company in database",
            "Analyse full offer letter",
            "View connected fraud graph"
        ]

        # 1. Check for specific Report ID queries (e.g. "report 1", "report #2", "details of report 3")
        report_match = re.search(r'report\s*(?:#|id|number)?\s*([0-9]+)', msg_lower)
        if report_match:
            rep_id = int(report_match.group(1))
            tools_executed.append(f"get_report_details({rep_id})")
            details = ChatbotTools.get_report_details(db, rep_id)
            if "error" not in details:
                tools_executed.append(f"get_network_connections({rep_id})")
                net_conn = ChatbotTools.get_network_connections(db, rep_id)

                evidence_references.append({
                    "type": "Report Record",
                    "id": f"Report #{rep_id}",
                    "company": details["company_name"],
                    "risk_score": details["risk_score"]
                })

                shared_txt = ""
                if net_conn.get("total_connected_reports", 0) > 0:
                    shared_txt = f"\n\n**Connected Fraud Ring:** This report shares identifiers with **{net_conn['total_connected_reports']} other incident report(s)**:"
                    for conn in net_conn["connected_reports"]:
                        shared_ents_str = ", ".join([f"{e['entity_type']} ({e['masked_identifier']})" for e in conn["shared_entities"]])
                        shared_txt += f"\n- **Report #{conn['connected_report_id']}** ({conn['company_name']}, Risk: {int(conn['risk_score'])}/100) via {shared_ents_str}"

                reply = (
                    f"### Investigation Dossier: Report #{rep_id}\n\n"
                    f"- **Target Entity / Company:** {details['company_name'] or 'Unknown'}\n"
                    f"- **Claimed Recruiter:** {details['recruiter_name'] or 'Not provided'}\n"
                    f"- **Job Role:** {details['job_role'] or 'Internship'}\n"
                    f"- **Risk Assessment:** **{int(details['risk_score'])}/100** ({details['risk_category']})\n"
                    f"- **Classification:** {details['report_type']}\n"
                    f"- **Verification Status:** {details['verification_status']}\n"
                    f"- **Filed Date:** {details['created_at']}\n\n"
                    f"**Allegation Summary:**\n\"{details['description']}\"\n"
                    f"{shared_txt}\n\n"
                    f"**Analyst Note:** Treat these linked identifiers as investigative intelligence. Independently corroborate company registration via the MCA (Ministry of Corporate Affairs) portal before engaging."
                )
                return {
                    "role": "assistant",
                    "message": reply,
                    "ai_mode": "demo",
                    "tool_calls_executed": tools_executed,
                    "evidence_references": evidence_references,
                    "suggested_actions": ["Show connected graph for this report", "Search another recruiter", "File new incident report"]
                }

        # 2. Extract phone / email / UPI / company from query
        extracted = ExtractionService.extract_all(message)
        found_id = None
        if extracted["phone_numbers"]:
            found_id = extracted["phone_numbers"][0]
        elif extracted["upi_ids"]:
            found_id = extracted["upi_ids"][0]
        elif extracted["recruiter_emails"]:
            found_id = extracted["recruiter_emails"][0]

        if found_id:
            tools_executed.append(f"get_connected_reports('{found_id}')")
            conn_res = ChatbotTools.get_connected_reports(db, found_id)
            if conn_res["found"]:
                reps = conn_res["reports"]
                rep_bullets = []
                for r in reps:
                    rep_bullets.append(f"- **Report #{r['report_id']}** ({r['company_name']}): Risk Score **{int(r['risk_score'])}/100** — *{r['summary']}*")
                    evidence_references.append({
                        "type": "Incident Match",
                        "id": f"Report #{r['report_id']}",
                        "company": r["company_name"]
                    })

                reply = (
                    f"### Intelligence Match Found for Identifier: `{found_id}`\n\n"
                    f"OfferGraph records indicate that this identifier has appeared in **{len(reps)} suspicious recruitment incident(s)**:\n\n"
                    + "\n".join(rep_bullets) +
                    f"\n\n**Investigative Implication:** Multiple distinct job postings sharing the exact same contact/payment identifier is a classic signature of syndicates reusing fraudulent infrastructure across different fictitious company fronts.\n\n"
                    f"**Safety Recommendation:** Cease further communication and do not authorize any payment."
                )
                return {
                    "role": "assistant",
                    "message": reply,
                    "ai_mode": "demo",
                    "tool_calls_executed": tools_executed,
                    "evidence_references": evidence_references,
                    "suggested_actions": ["View in Fraud Network Graph", "How to block & report recruiter", "Check another phone or UPI"]
                }
            else:
                return {
                    "role": "assistant",
                    "message": (
                        f"### Identifier Search Results: `{found_id}`\n\n"
                        f"No prior incident reports currently associate `{found_id}` with flagged fraudulent activity in the OfferGraph repository.\n\n"
                        f"**Cautionary Note:** The absence of prior reports does NOT guarantee that the recruiter is legitimate, as fraudulent actors frequently rotate phone numbers and virtual payment accounts (VPAs). Please examine whether they are requesting any upfront fees or communicating from personal webmail."
                    ),
                    "ai_mode": "demo",
                    "tool_calls_executed": tools_executed,
                    "evidence_references": [],
                    "suggested_actions": ["Analyse offer letter text", "How to verify recruiter identity", "Search company name"]
                }

        # 3. Check for Company search (e.g. "Apex Technologies", "CloudTech", "Global Data")
        for comp in ["apex", "cloudtech", "nexis", "zenith", "global data", "techflow", "infosys", "tcs", "google"]:
            if comp in msg_lower:
                tools_executed.append(f"search_company('{comp}')")
                comp_res = ChatbotTools.search_company(db, comp)
                if comp_res["matched_reports_count"] > 0:
                    rep_list = comp_res["reports"]
                    bullet_pts = [f"- **Report #{r['report_id']}**: {r['company_name']} (Risk: {int(r['risk_score'])}/100, Type: {r['report_type']})" for r in rep_list]
                    for r in rep_list:
                        evidence_references.append({
                            "type": "Company Intelligence",
                            "id": f"Report #{r['report_id']}",
                            "company": r["company_name"]
                        })

                    reply = (
                        f"### Intelligence for Company: **{comp.title()}**\n\n"
                        f"Found **{len(rep_list)} incident report(s)** mentioning entities associated with **{comp.title()}**:\n\n"
                        + "\n".join(bullet_pts) +
                        f"\n\n**Key Finding:** Review the incident descriptions to see if impersonators are claiming to represent this organization. Scammers frequently usurp brand names while routing payments to personal UPI accounts."
                    )
                    return {
                        "role": "assistant",
                        "message": reply,
                        "ai_mode": "demo",
                        "tool_calls_executed": tools_executed,
                        "evidence_references": evidence_references,
                        "suggested_actions": ["Check recruiter phone number", "View shared connections", "Verify official domain"]
                    }

        # 4. Direct offer analysis intent
        if any(w in msg_lower for w in ["analyse", "analyze", "offer", "internship", "stipend", "pay ₹", "selected", "registration fee"]):
            tools_executed.append("analyse_offer(text)")
            analysis = ChatbotTools.analyse_offer_text(message)
            indicators = analysis["indicators"]
            score = analysis["risk_score"]
            cat = analysis["risk_category"]

            flag_bullets = [f"- **{ind['title']}** (+{ind['points']} pts): {ind['description']}" for ind in indicators]

            reply = (
                f"### Offer Risk Evaluation\n\n"
                f"- **Calculated Risk Score:** **{int(score)}/100** ({cat})\n"
                f"- **Detected Entities:** Company: `{analysis['extracted']['company_name'] or 'Unspecified'}`, Role: `{analysis['extracted']['job_role']}`\n\n"
                + (f"**Identified Risk Indicators:**\n" + "\n".join(flag_bullets) + "\n\n" if flag_bullets else "**No critical overt scam indicators** detected in this excerpt.\n\n") +
                f"**Strategic Advice:** Genuine corporate internships do not require upfront deposits or test fees. Always verify the sender's email domain directly on the official careers page."
            )
            return {
                "role": "assistant",
                "message": reply,
                "ai_mode": "demo",
                "tool_calls_executed": tools_executed,
                "evidence_references": [],
                "suggested_actions": ["Submit formal incident report", "Ask about 1930 helpline", "How to verify company domain"]
            }

        # 5. Safety Guidance Queries
        if any(w in msg_lower for w in ["registration fee", "pay money", "transfer money", "security deposit"]):
            reply = (
                "### Official Safety Rule: Never Pay Recruitment Fees\n\n"
                "**1. The Universal Golden Rule:** Legitimate employers, multinational corporations, and genuine startups **NEVER** demand registration fees, laptop security deposits, onboarding charges, or gate-pass payments from prospective interns or employees.\n\n"
                "**2. The Fraud Pattern:** Scammers often claim the fee is '100% refundable with the first month's stipend'. Once paid via UPI or net banking, they either vanish or demand further 'document processing fees'.\n\n"
                "**3. Legal Standing in India:** Demanding money in exchange for employment violates the Emigration Act and sections 419/420 & 66D of the Information Technology Act."
            )
            return {
                "role": "assistant",
                "message": reply,
                "ai_mode": "demo",
                "tool_calls_executed": ["get_safety_guidance('recruitment_fees')"],
                "evidence_references": [],
                "suggested_actions": ["What to do if already transferred money?", "How to verify a recruiter?", "National cybercrime helpline 1930"]
            }

        if any(w in msg_lower for w in ["already paid", "transferred money", "scammed", "lost money", "help me"]):
            reply = (
                "### Immediate Emergency Actions If You Transferred Money\n\n"
                "1. **Act Within the 'Golden Hour':**\n"
                "   - Immediately call the **National Cybercrime Helpline at `1930`** (India) to request a transaction freeze before the scammer withdraws the funds.\n"
                "   - File an official complaint online at **[cybercrime.gov.in](https://cybercrime.gov.in)**.\n\n"
                "2. **Contact Your Bank / UPI App:**\n"
                "   - Report the transaction as an unauthorized / fraudulent transfer. Provide the recipient UPI ID, transaction UTR number, and timestamp.\n\n"
                "3. **Preserve Digital Evidence:**\n"
                "   - Take screenshots of WhatsApp/Telegram chats, offer letters, email headers, and payment receipts.\n\n"
                "4. **Log Incident on OfferGraph:**\n"
                "   - Submit the scammer's phone number and UPI ID on OfferGraph to protect other students from the same syndicate."
            )
            return {
                "role": "assistant",
                "message": reply,
                "ai_mode": "demo",
                "tool_calls_executed": ["get_emergency_protocol()"],
                "evidence_references": [],
                "suggested_actions": ["Submit this incident to OfferGraph", "Open Cybercrime Portal", "Check if UPI is in graph"]
            }

        # Default fallback guidance
        reply = (
            "### OfferGraph AI Investigator — Ready to Assist\n\n"
            "I can investigate suspicious recruitment activities using our live intelligence graph and fraud pattern analysis.\n\n"
            "**Here are ways I can help you right now:**\n"
            "- **Evaluate an Offer:** Paste an excerpt or offer letter to detect red flags and calculate an explainable risk score.\n"
            "- **Investigate Identifiers:** Ask e.g., *'Has 9876543210 appeared in previous reports?'* or *'Are there incidents linked to apexjobs@upi?'*\n"
            "- **Query Companies:** Ask *'Show reports connected to Apex Technologies'*.\n"
            "- **Inspect Reports:** Ask *'Show details of Report #1'* to view connected syndicates.\n"
            "- **Emergency Protocols:** Ask *'What should I do if I already paid a fee?'*"
        )
        return {
            "role": "assistant",
            "message": reply,
            "ai_mode": "demo",
            "tool_calls_executed": [],
            "evidence_references": [],
            "suggested_actions": ["Check Apex Technologies reports", "Is 9876543210 suspicious?", "Should I pay a ₹999 registration fee?"]
        }

    @staticmethod
    def _process_with_openai(
        db: Session,
        message: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Uses OpenAI with Function Calling tools for full agentic investigation.
        """
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_entity",
                    "description": "Searches for an entity by phone, email, UPI, domain, or company name in OfferGraph DB",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "identifier": {"type": "string", "description": "The phone, email, UPI ID, or name"}
                        },
                        "required": ["identifier"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_connected_reports",
                    "description": "Finds all incident reports linked to a phone, email, or UPI identifier",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "identifier": {"type": "string", "description": "The phone number, email, or UPI ID"}
                        },
                        "required": ["identifier"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_report_details",
                    "description": "Gets full details of an incident report by ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report_id": {"type": "integer", "description": "The report ID"}
                        },
                        "required": ["report_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_company",
                    "description": "Queries incident reports associated with a company name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "company_name": {"type": "string", "description": "The name of the company"}
                        },
                        "required": ["company_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_network_connections",
                    "description": "Finds other incident reports that share entities with a given report",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report_id": {"type": "integer", "description": "The report ID"}
                        },
                        "required": ["report_id"]
                    }
                }
            }
        ]

        system_prompt = (
            "You are OfferGraph AI Investigator, an expert cyber fraud intelligence agent specializing in recruitment scams, "
            "fake internships, and impersonation fraud. You have direct access to the OfferGraph database via tools.\n"
            "Rules:\n"
            "1. NEVER invent database results or fake reports. If no reports exist, state so honestly.\n"
            "2. Always invoke tools when a user asks about identifiers (phone, email, UPI, company, report #).\n"
            "3. Mask sensitive personal identifiers in final text (+91 98****3210, a***x@gmail.com).\n"
            "4. Provide evidence citations referencing exact Report IDs.\n"
            "5. Never guarantee legal outcomes; provide actionable safety guidance."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        tools_executed = []
        evidence_references = []

        if tool_calls:
            messages.append(response_message)
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                tools_executed.append(f"{func_name}({json.dumps(func_args)})")

                tool_result = {}
                if func_name == "search_entity":
                    tool_result = ChatbotTools.search_entity(db, func_args.get("identifier", ""))
                elif func_name == "get_connected_reports":
                    tool_result = ChatbotTools.get_connected_reports(db, func_args.get("identifier", ""))
                    for r in tool_result.get("reports", []):
                        evidence_references.append({"type": "Incident Match", "id": f"Report #{r['report_id']}", "company": r.get("company_name")})
                elif func_name == "get_report_details":
                    tool_result = ChatbotTools.get_report_details(db, func_args.get("report_id", 0))
                    if "error" not in tool_result:
                        evidence_references.append({"type": "Report Record", "id": f"Report #{tool_result['report_id']}", "company": tool_result.get("company_name")})
                elif func_name == "search_company":
                    tool_result = ChatbotTools.search_company(db, func_args.get("company_name", ""))
                elif func_name == "get_network_connections":
                    tool_result = ChatbotTools.get_network_connections(db, func_args.get("report_id", 0))

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

            second_response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.2
            )
            final_content = second_response.choices[0].message.content or ""
        else:
            final_content = response_message.content or ""

        return {
            "role": "assistant",
            "message": final_content,
            "ai_mode": "live",
            "tool_calls_executed": tools_executed,
            "evidence_references": evidence_references,
            "suggested_actions": ["Check another entity", "Analyse offer letter", "View network graph"]
        }
