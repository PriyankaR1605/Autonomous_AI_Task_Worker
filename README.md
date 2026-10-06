# CentrAlign Autonomous AI Task Worker

An autonomous, multi-step task worker prototype that receives high-level natural language instructions, breaks them into executable milestones, operates across simulated enterprise tools (local file system, document intelligence, Playwright browser, internal ERP), handles unexpected conditions with self-healing retries, requests human approval when safety thresholds are triggered, and independently verifies outcome completion with an auditable evidence dossier.

---

## 🎯 Capability Showcase

This system solves the user prompt:
> **"Find the latest invoice from Company X, extract the amount and due date, enter it into our internal system, and tell me once it is done."**

### Key Capabilities Demonstrated:
1. **Goal Understanding**: Translates unstructured intent into structured milestone plans without requiring micro-step instructions.
2. **Action Decomposition**: Hierarchical planning broken down into 5 measurable milestones.
3. **Multi-Tool Integration**:
   - `file_search`: Locates and ranks vendor invoice files by recency.
   - `document_extractor`: Parses PDF/text files to extract amounts, dates, and invoice IDs.
   - `browser_automation`: Playwright-driven browser interaction navigating login and form entry in the internal ERP.
   - `erp_api`: Direct REST API integration serving both as primary tool and self-healing fallback.
4. **Perception & State Scratchpad**: Tracks working memory facts across all steps.
5. **Dynamic Self-Healing & Error Recovery**:
   - Heuristic selector recovery if DOM elements change.
   - Automatic fallback to REST API if browser automation faces timeouts or layout changes.
6. **Safety & Human-in-the-Loop (HITL)**:
   - Financial safety guardrail triggers when invoice amounts exceed threshold (e.g. > $3,000).
   - Pauses execution for interactive user authorization before recording high-value entries.
7. **Independent Outcome Verification**:
   - Verifies database ledger records against original extracted document values (amount match, vendor match, due date match).
8. **Auditable Evidence Dossier**:
   - Saves before/after screenshots and outputs an auditable Markdown report with exact timestamps and tool call parameters.

---

## 📁 Project Structure

```text
CentrAlign_AI_Project/
├── AUTONOMOUS_TASK_WORKER_PLAN.md   # Architectural master blueprint
├── requirements.txt                 # Project dependencies
├── .env.example / .env              # Configuration & thresholds
├── run_mock_erp.py                  # Launcher for mock ERP web portal
├── run_worker.py                    # CLI launcher for the Autonomous Worker
├── mock_erp/                        # Simulated Enterprise ERP application
│   ├── app.py                       # FastAPI backend & verification API
│   ├── database.py                  # SQLite ledger & audit log
│   └── templates/                   # Tailwind web UI (Login, Dashboard, Form)
├── data/
│   ├── sample_invoices/             # Realistic synthetic invoices
│   └── storage/                     # Screenshots, downloads, and audit dossiers
├── worker/                          # Agent cognitive architecture
│   ├── agent.py                     # Autonomous ReAct orchestrator loop
│   ├── planner.py                   # Intent decomposition into milestones
│   ├── state.py                     # Pydantic state models & audit trace
│   ├── approval.py                  # Human-in-the-Loop policy gate
│   ├── verifier.py                  # Independent outcome verifier
│   ├── config.py                    # Environment settings
│   ├── reporting/evidence.py        # Generates audit reports
│   └── tools/                       # Modular tool implementations
│       ├── base.py                  # Tool interface & ToolResult
│       ├── file_tool.py             # File search & ranking tool
│       ├── document_tool.py         # PDF & document extraction tool
│       ├── browser_tool.py          # Playwright browser controller
│       └── erp_api_tool.py          # Internal ERP REST API tool
├── ui/
│   └── dashboard.py                 # Streamlit live monitoring dashboard
├── scripts/
│   └── generate_sample_invoices.py  # Sample invoice generator
└── tests/
    └── test_flow.py                 # End-to-end integration test
```

---

## 🚀 Quickstart Guide

### 1. Setup Virtual Environment & Dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

### 2. Generate Test Invoices
```powershell
python scripts/generate_sample_invoices.py
```
This generates:
- `data/sample_invoices/Invoice_CompanyX_Latest.pdf` ($4,850.00, Due: 2026-11-15)
- `data/sample_invoices/Invoice_CompanyX_Old.pdf` ($1,200.00, Due: 2026-05-25)
- `data/sample_invoices/Invoice_CompanyY_Draft.pdf` ($2,890.50, Due: 2026-10-30)

### 3. Start Mock Enterprise ERP Server (Terminal 1)
```powershell
python run_mock_erp.py
```
- Open browser at `http://127.0.0.1:8000/login`
- Login credentials: `admin` / `company_secure_pass`

### 4. Run the Autonomous Worker (Terminal 2)

#### Option A: Interactive Streamlit UI
```powershell
streamlit run ui/dashboard.py
```
Features real-time step progress, thought logs, live screenshots, and downloadable audit reports.

#### Option B: Command Line Interface (CLI)
```powershell
python run_worker.py "Find the latest invoice from Company X, extract the amount and due date, enter it into our internal system, and tell me once it is done."
```

#### Option C: Automated Integration Test
```powershell
python tests/test_flow.py
```
