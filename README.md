# OfferGraph — AI-Powered Job Fraud Intelligence Platform

> **"Don't just detect suspicious offers. Connect the evidence."**

OfferGraph is a full-stack, AI-powered cybersecurity intelligence platform designed to protect students and job seekers from recruitment fraud, fake internships, and advance-fee syndicate traps. 

Unlike traditional point-in-time scam detectors that evaluate individual messages in isolation, **OfferGraph constructs an interactive, multi-entity fraud intelligence graph** that correlates isolated incidents sharing phone numbers, virtual payment addresses (UPI IDs), disposable email domains, and recruiter aliases.

---

## 🌟 Key Differentiators & Highlights

1. **Connected Fraud Intelligence Graph (Cytoscape.js & NetworkX)**:
   - Evaluates multi-report threat clusters in real time.
   - Revealing syndicated fraud rings reusing contact and payment infrastructure across distinct company fronts.
2. **OfferGraph AI Investigator (OpenAI GPT Function Calling + Deterministic Fallback)**:
   - Autonomous cybersecurity forensic assistant capable of querying the live database (`get_connected_reports`, `search_entity`, `get_report_details`, `get_network_connections`).
   - Operates in live OpenAI mode when `OPENAI_API_KEY` is present, or switches seamlessly to a high-fidelity **Deterministic Demo Mode** without breaking or faking data.
3. **Forensic Entity Extraction & Explainable Scoring**:
   - PyMuPDF text parsing for PDF offer letters and raw pasted messages.
   - Regex & contextual heuristics for Indian phone numbers (`+91`), UPI handles (`@okhdfcbank`, `@ybl`, `@paytm`), disposable webmail, and payment amounts.
   - Transparent rule-based risk scoring (0–100 scale: Low, Medium, High Risk) with granular evidence snippets.
4. **Structured Incident Reporting & Verification**:
   - Multi-stage incident intake with review confirmation and automated graph relationship linking (`MENTIONS_COMPANY`, `USES_PHONE`, `CONTAINS_UPI`, `CONTAINS_EMAIL`).
5. **India Cybercrime Integration (1930 Helpline & cybercrime.gov.in)**:
   - Dedicated incident response protocol highlighting the 'Golden Hour' inter-bank freeze procedure.

---

## 🏗️ Architecture & Technology Stack

```
offergraph/
├── frontend/                     # React.js SPA (Vite + Tailwind CSS)
│   ├── src/
│   │   ├── components/           # NetworkGraph (Cytoscape.js), RiskBadge
│   │   ├── layouts/              # MainLayout (Cybersecurity Sidebar & Header)
│   │   ├── pages/                # Dashboard, CheckOffer, FraudNetwork, AiAssistant, ReportIncident, History, Safety
│   │   ├── services/             # Centralized API client (api.js)
│   │   ├── App.jsx               # React Router DOM v6
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── backend/                      # Python FastAPI Enterprise Backend
│   ├── app/
│   │   ├── main.py               # Application entrypoint & CORS middleware
│   │   ├── database.py           # SQLAlchemy engine & session factory
│   │   ├── models.py             # Relational schema (Report, Entity, ReportEntity, etc.)
│   │   ├── schemas.py            # Pydantic v2 validation models
│   │   ├── seed.py               # Synthetic Demonstration Data seeder
│   │   ├── routers/              # Modular REST routers
│   │   │   ├── dashboard.py
│   │   │   ├── analyze.py
│   │   │   ├── reports.py
│   │   │   ├── entities.py
│   │   │   ├── graph.py
│   │   │   ├── chat.py
│   │   │   └── safety.py
│   │   └── services/
│   │       ├── extraction_service.py   # Regex & heuristics entity normalizer
│   │       ├── risk_engine.py          # Explainable rule-based scoring engine
│   │       ├── graph_service.py        # NetworkX topology & Cytoscape exporter
│   │       ├── ai_service.py           # OpenAI SDK integration & fallback
│   │       └── chatbot_service.py      # AI Investigator agent with DB tools
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── README.md
└── .gitignore
```

---

## ⚡ Quick Start Guide (Run Locally)

### Prerequisites
- **Python**: 3.10+ (Tested on Python 3.14)
- **Node.js**: v18+ (Tested on v24.18.0)
- **Git**

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# (Optional) Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed the SQLite database with demonstration data
python -m app.seed

# Start the FastAPI server (Runs on http://127.0.0.1:8000)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive OpenAPI Swagger Documentation will be available at:  
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

### 2. Frontend Setup

In a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite development server (Runs on http://localhost:3000)
npm run dev
```

Open your browser and navigate to:  
👉 **[http://localhost:3000](http://localhost:3000)**

---

## ⚙️ Environment Variables

Copy `backend/.env.example` to `backend/.env`:

```env
# Optional: Set your OpenAI API key for live GPT-4o-mini generation
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

# Database: Defaults to local SQLite if omitted
DATABASE_URL=sqlite:///./offergraph.db
# Or use Supabase:
# SUPABASE_DATABASE_URL=postgresql://user:password@host:port/database

# Server Configuration
HOST=127.0.0.1
PORT=8000
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

> **Note**: If `OPENAI_API_KEY` is not provided, OfferGraph automatically operates in **Deterministic Demo Mode**. All database queries, tool executions, and risk assessments run locally with zero cloud dependencies.

---

## 🎬 3-Minute Hackathon Demonstration Script

Follow this sequence for an impactful live demonstration:

### Minute 1: The Problem & Dashboard Overview
1. Open **Dashboard** at `http://localhost:3000`.
2. Point out the **Threat Metrics**: 8 total reports, 26 entities, and 4 detected syndicate clusters.
3. Show the **Top Correlated Identifiers** card highlighting phone number `+91 98****3210` and UPI ID `ap****@okhdfcbank` appearing repeatedly across multiple complaints.
4. Note the ethical disclaimer: *"Synthetic Demonstration Data Active — Not Real Complaints"*.

### Minute 2: Check an Offer (Core Forensic Pipeline)
1. Navigate to **Check an Offer** in the sidebar.
2. Click the **"Load Sample Scam Offer"** button. An authentic internship offer from *"Apex Technologies"* requesting a ₹999 refundable registration fee via `apexpay@okhdfcbank` is autofilled.
3. Click **"Analyse Offer"**.
4. Show the results:
   - **Risk Score**: `85/100 (High Risk)`.
   - **Explainable Indicators**: Breakdown of flags (+25 registration fee, +15 urgent 24h pressure, +15 free webmail).
   - **Network Match Alert**: OfferGraph highlights that `apexpay@okhdfcbank` and `+91 9876543210` match **Report #1 and Report #2** previously logged in the database!

### Minute 3: Interactive Fraud Network & AI Investigator
1. Click **"Inspect in Fraud Network"** (or open the **Fraud Network** tab).
2. The interactive force-directed graph (Cytoscape.js) renders the entire threat landscape.
3. Click on the phone node `+91 98****3210` or UPI node `ap****@okhdfcbank`.
4. The **Entity Dossier Panel** opens on the right, showing 2 linked reports, connected companies (*Apex Technologies*, *Nexis Cloud*), and full incident history.
5. Click **"Investigate in AI Assistant"**.
6. The chat opens with the AI Investigator. Type or click the chip:  
   *"Has +91 9876543210 appeared in previous reports?"*
7. Watch the AI execute backend tool `get_connected_reports('9876543210')` and cite Report #1 and Report #2 with evidence references!
8. Conclude by demonstrating the **Safety Centre** and the 1930 National Cybercrime helpline advisory.

---

## 🔒 Security & Privacy Practices

- **Identifier Masking**: Sensitive phone numbers (`+91 98****3210`), email usernames (`re****@gmail.com`), and UPI handles are masked in user-facing views to preserve privacy.
- **Unverified Labeling**: Submitted reports are explicitly designated as *Unverified Submissions* until corroboration algorithms detect multi-victim clustering.
- **No Hardcoded Keys**: API keys are strictly read from environment variables; frontend code never exposes backend secrets.

---

## 🚀 Deployment Readiness

- **Frontend**: Prepared for Vercel/Netlify (`npm run build` generates optimized production static assets in `frontend/dist/`).
- **Backend**: Prepared for Render/Railway/Fly.io via Uvicorn with standard ASGI entrypoint `backend.app.main:app`.
