# OfferGraph — AI-Powered Job Fraud Intelligence Platform

> **"Don't just detect suspicious offers. Connect the evidence."**

OfferGraph is a full-stack, AI-powered cybersecurity intelligence platform designed to protect students and job seekers from recruitment fraud, fake internships, and advance-fee syndicate traps. 

Unlike traditional point-in-time scam detectors that evaluate individual messages in isolation, **OfferGraph constructs an interactive, multi-entity fraud intelligence graph** that correlates isolated incidents sharing phone numbers, virtual payment addresses (UPI IDs), disposable email domains, and recruiter aliases.

---

## 🏆 Hackathon Judging Criteria Alignment

| Parameter | Implementation & Architectural Evidence |
| :--- | :--- |
| **1. Code Quality** | • Modular domain-driven architecture (`services/`, `routers/`, `models/`, `schemas/`).<br>• Fully typed Pydantic v2 validation models with `ConfigDict(from_attributes=True)`.<br>• React 18 SPA with centralized API layer, custom hooks, and `<ErrorBoundary>` protection preventing client-side crashes. |
| **2. Security** | • **HTTP Security Headers**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`, `Strict-Transport-Security`, `Referrer-Policy`.<br>• **Rate Limiting**: Sliding-window rate limiter (120 req/min per IP) on all `/api/` endpoints.<br>• **Upload Guardrails**: 5MB strict limit, PDF magic-header validation, rejection of executable binaries.<br>• **Sanitization & PII Masking**: Input sanitization against stored XSS; masking of phone (`+91 98****3210`), email (`re****@gmail.com`), and UPI IDs. |
| **3. Efficiency** | • **Graph Caching**: In-memory memoization of NetworkX graph & Cytoscape elements with automatic cache invalidation upon report submission (<10ms retrieval).<br>• **Database Indexing**: Compound indexes on `(entity_type, normalized_value)` and foreign keys.<br>• **Bundle Code-Splitting**: Vite manual chunks for `cytoscape`, `recharts`, `lucide-react`, and React vendor to minimize initial load time. |
| **4. Testing** | • **Automated Pytest Suite**: 20 comprehensive unit, integration, and security tests in `backend/tests/` (100% pass rate in 2.08s).<br>• Tests extraction regexes, risk scoring boundaries (0–100 cap), XSS sanitization, oversized file rejections, and chatbot tool executions. |
| **5. Accessibility (a11y)** | • **WCAG AA Compliance**: High-contrast cybersecurity theme with distinct threat colors.<br>• **Keyboard Navigation**: Explicit `focus-visible:ring-2 focus-visible:ring-cyan-400` on all interactive controls.<br>• **Screen Reader Support**: Semantic HTML (`<main id="main-content">`, `<nav>`, `<aside>`), ARIA labels, `aria-expanded` sidebar states, and a dedicated **Skip to main content** link. |
| **6. Google Services** | • **Google Gemini 1.5 Flash / Pro API**: Configurable first-class AI intelligence provider (`GEMINI_API_KEY`).<br>• **Google Safe Browsing / Web Risk**: Domain reputation checks identifying malicious recruitment phishing links.<br>• **Google Cloud Run**: Production multi-stage `Dockerfile` with dynamic `$PORT` binding for containerized deployment. |
| **7. Problem Statement Alignment** | • **Core Differentiator**: Directly addresses the hackathon problem statement by connecting isolated recruitment complaints through shared identifiers.<br>• **Transparent Explainability**: Granular risk points (+25 registration fee, +15 urgent pressure, etc.).<br>• **India Cybercrime Integration**: Direct linkage to India's **National Cybercrime Reporting Helpline (1930)** and [cybercrime.gov.in](https://cybercrime.gov.in). |

---

## 🏗️ Architecture & Technology Stack

```
offergraph/
├── frontend/                     # React.js SPA (Vite + Tailwind CSS)
│   ├── src/
│   │   ├── components/           # NetworkGraph (Cytoscape.js), RiskBadge, ErrorBoundary
│   │   ├── layouts/              # MainLayout (Accessible Sidebar & Header)
│   │   ├── pages/                # Dashboard, CheckOffer, FraudNetwork, AiAssistant, ReportIncident, History, Safety
│   │   ├── services/             # Centralized API client (api.js)
│   │   ├── App.jsx               # React Router DOM v6 with ErrorBoundary
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js            # Custom Rollup code-splitting chunks
│
├── backend/                      # Python FastAPI Enterprise Backend
│   ├── app/
│   │   ├── main.py               # Security middleware, rate limiter, static SPA mount
│   │   ├── database.py           # SQLAlchemy engine & session factory
│   │   ├── models.py             # Relational schema (Report, Entity, ReportEntity, etc.)
│   │   ├── schemas.py            # Pydantic v2 validation models
│   │   ├── seed.py               # Synthetic Demonstration Data seeder
│   │   ├── routers/              # Modular REST routers (analyze, graph, chat, reports, etc.)
│   │   └── services/             # Extraction, Risk Engine, Graph Caching, Gemini/OpenAI Service
│   ├── tests/                    # 20 Automated Pytest unit, integration, & security tests
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── Dockerfile                    # Multi-stage production container (Cloud Run ready)
├── render.yaml                   # 100% Free deployment blueprint
└── README.md
```

---

## ⚡ Quick Start Guide (Run Locally)

### 1. Backend Setup

```bash
cd backend

# Install dependencies (FastAPI, PyMuPDF, NetworkX, Pytest, etc.)
pip install -r requirements.txt

# Seed the SQLite database with demonstration data
python -m app.seed

# Run the 20 automated tests
python -m pytest tests -v

# Start the FastAPI server (Runs on http://127.0.0.1:8000)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive OpenAPI Swagger Docs: 👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

### 2. Frontend Setup

In a new terminal:

```bash
cd frontend

# Install npm dependencies
npm install

# Start Vite development server (Runs on http://localhost:3000)
npm run dev
```
Open in browser: 👉 **[http://localhost:3000](http://localhost:3000)**

---

## 🧪 Automated Testing Verification

To run the automated test suite verifying extraction accuracy, risk calculations, security controls, and endpoint behavior:

```bash
python -m pytest backend/tests -v
```

Output:
```text
backend/tests/test_api_endpoints.py::TestAPIEndpoints::test_dashboard_stats PASSED
backend/tests/test_api_endpoints.py::TestAPIEndpoints::test_recent_reports PASSED
backend/tests/test_api_endpoints.py::TestAPIEndpoints::test_safety_resources PASSED
backend/tests/test_api_endpoints.py::TestAPIEndpoints::test_graph_elements PASSED
backend/tests/test_api_endpoints.py::TestAPIEndpoints::test_report_creation_and_graph_linkage PASSED
backend/tests/test_api_endpoints.py::TestAPIEndpoints::test_chatbot_tool_execution PASSED
backend/tests/test_api_endpoints.py::TestAPIEndpoints::test_analyze_offer PASSED
backend/tests/test_extraction.py::TestExtractionService::test_phone_normalization_and_masking PASSED
backend/tests/test_extraction.py::TestExtractionService::test_email_normalization_and_masking PASSED
backend/tests/test_extraction.py::TestExtractionService::test_upi_normalization_and_masking PASSED
backend/tests/test_extraction.py::TestExtractionService::test_domain_normalization PASSED
backend/tests/test_extraction.py::TestExtractionService::test_extract_all_entities_from_message PASSED
backend/tests/test_risk_engine.py::TestRiskEngine::test_benign_message_scoring PASSED
backend/tests/test_risk_engine.py::TestRiskEngine::test_high_risk_scam_message_scoring PASSED
backend/tests/test_risk_engine.py::TestRiskEngine::test_score_capped_at_100 PASSED
backend/tests/test_security.py::TestSecurityControls::test_xss_sanitization PASSED
backend/tests/test_security.py::TestSecurityControls::test_null_byte_injection PASSED
backend/tests/test_security.py::TestSecurityControls::test_unsupported_file_extension_rejection PASSED
backend/tests/test_security.py::TestSecurityControls::test_oversized_file_rejection PASSED
backend/tests/test_security.py::TestSecurityControls::test_corrupted_pdf_header_validation PASSED

======================= 20 passed in 2.08s =======================
```

---

## 🎬 3-Minute Hackathon Demonstration Script

```
[00:00 - 00:45] Minute 1: The Problem & Dashboard
1. Open http://localhost:3000.
2. Problem Statement: "Existing detectors evaluate offers in isolation. OfferGraph connects the evidence."
3. Highlight Metrics: 8 reports, 26 entities, 4 syndicate clusters.
4. Point out Top Correlated Identifiers (+91 98****3210 and apexpay@okhdfcbank appearing across multiple reports).

[00:45 - 01:45] Minute 2: Check an Offer (Core Detection & DB Correlation)
1. Navigate to "Check an Offer".
2. Click "Load Sample Scam Offer" (Apex Technologies requesting ₹999 fee via apexpay@okhdfcbank).
3. Click "Analyse Offer".
4. Results show:
   - Risk Score: 85/100 (High Risk) with transparent indicator breakdown (+25 registration fee, +15 urgent pressure).
   - FRAUD NETWORK MATCH: "Extracted phone and UPI match Report #1 and Report #2 in our repository!"

[01:45 - 02:45] Minute 3: Fraud Network Graph & AI Investigator
1. Click "Inspect in Fraud Network".
2. Explore interactive Cytoscape.js force-directed graph.
3. Click on node +91 98****3210 to open Entity Dossier Panel displaying connected companies (Apex Technologies, Nexis Cloud).
4. Click "Investigate in AI Assistant".
5. Ask: "Has +91 9876543210 appeared in previous reports?"
6. The AI Investigator executes backend tool get_connected_reports('9876543210') and cites Report #1 & #2 with evidence.

[02:45 - 03:00] Wrap-up: Safety Centre
1. Show Safety Centre highlighting India's 1930 Cybercrime Helpline and cybercrime.gov.in emergency response.
```
