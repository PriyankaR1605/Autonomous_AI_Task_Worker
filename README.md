# CentrAlign Autonomous AI Task Worker

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-brightgreen?style=for-the-badge&logo=render)](https://autonomous-ai-task-worker.onrender.com)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?style=for-the-badge&logo=github)](https://github.com/PriyankaR1605/Autonomous_AI_Task_Worker)

> 🌐 **Live Cloud Deployment**: **[https://autonomous-ai-task-worker.onrender.com](https://autonomous-ai-task-worker.onrender.com)**  
> *The prototype is deployed and accessible 24/7 in the cloud—anyone can run and inspect it from any device anytime!*

An autonomous, multi-step enterprise task worker prototype that receives natural language business instructions, reasons about the end goal, breaks requests into logical milestones, and autonomously executes operations across comprehensive company data—spanning **Finance & Invoices, HR & Staff Directory, IT Support & Incident Helpdesk, Inventory & Supply Chain, Department Budgets, and Corporate Governance Policies**.

---

## 🏢 Comprehensive Company Data & Domains

CentrAlign incorporates synthetic, enterprise-grade datasets modeled after **CentrAlign Technologies Inc.** (250+ employees, $1.5M+ quarterly budget, multi-tier ERP/CRM/ITSM database, policy knowledge base, and vendor agreements):

| Enterprise Domain | Available Company Data & Entities | Example Natural Language Tasks |
| :--- | :--- | :--- |
| **🧾 Finance & Invoices** | Commercial invoices (Payable/Receivable), Net-30 terms, vendor billing statements (Company X, Company Y, Acme Supplies, Global Cloud Hosting). | *"Find the latest invoice from Company X, extract the amount and due date, enter it into our internal system, and tell me once it is done."* |
| **👥 HR & Employee Management** | Staff directory across 7 departments (roles, salaries, managers, PTO balances, hire dates) and pending leave requests. | *"Find employee Sarah Jenkins, check her remaining annual leave balance, approve her pending vacation request, and update the HR system."* |
| **🎫 IT & Customer Support** | ITSM helpdesk ticket queue with P1-P4 priority levels, SLA countdowns, client reporters, and engineer assignments. | *"Scan all open customer support tickets, identify any CRITICAL priority tickets, reassign them to Senior Engineer Alex Wong, and mark them IN_PROGRESS."* |
| **📦 Inventory & Supply Chain** | Warehouse catalog, hardware assets, low-stock reorder thresholds, unit prices, preferred suppliers, and purchase orders. | *"Audit our inventory warehouse for all items below the reorder threshold, calculate restock requirements, and generate a purchase order to the preferred supplier."* |
| **💰 Expense & Compliance** | Employee expense claims, categories, receipts, and $1,000 supervisor threshold rules. | *"Audit recent employee expense reports against our company travel and procurement policy, flag any unapproved expenses over $1,000, and request approval."* |
| **📊 Budgets & Analytics** | Q3 departmental budget allocations vs actual expenditures, burn rates, and variance metrics. | *"Calculate the total Q3 marketing expenditure, compare it against the allocated department budget, and report budget variance."* |
| **📜 Policies & Knowledge Base** | Official PDF & text documents: 2026 Employee Handbook, Procurement Policy, IT Security ISO 27001 Standards, Vendor MSAs. | *"Check the company travel policy for per-diem limits and verify if the latest flight expense complies."* |

---

## 🎯 Key Autonomous Agent Capabilities

1. **Goal Understanding**: Translates unstructured high-level intent into multi-step milestones without requiring micro-step instructions.
2. **Dynamic Action Decomposition**: Hierarchical planning with domain-aware semantic intent classification and optional LLM support (Gemini, GPT-4, Claude).
3. **Multi-Tool Operation**:
   - `file_search`: Locates and ranks vendor invoices, contracts, policies, and receipts.
   - `document_extractor`: Parses PDF and text documents to extract structured metadata, dates, amounts, and policy clauses.
   - `enterprise_db`: Directly queries and executes CRUD operations across all company databases (employees, tickets, inventory, invoices, expenses).
   - `knowledge_search`: Semantically searches corporate governance policies and SLAs.
   - `analytics_calculator`: Computes budget variances, restock quantities, and financial sums.
   - `browser_automation`: Playwright-driven browser controller navigating the enterprise web portal and capturing visual proof.
   - `erp_api`: Programmatic REST API endpoints with self-healing fallback.
4. **Perception & State Scratchpad**: Maintains persistent working memory across all steps.
5. **Dynamic Self-Healing & Error Recovery**:
   - 3-tier execution strategy (Browser UI → REST API → Database Ledger).
   - Heuristic fallback and retry budgets when elements shift or endpoints fail.
6. **Safety & Human-in-the-Loop (HITL)**:
   - Configurable safety policies trigger interactive operator approval for high financial amounts (> $3,000) or sensitive HR modifications.
7. **Independent Outcome Verification**:
   - Programmatically asserts that the destination database record matches the requested state with zero discrepancies.
8. **Auditable Evidence Dossier**:
   - Automatically generates a Markdown audit report with execution timestamps, tool inputs/outputs, reconciliation matrices, and visual proof screenshots.

---

## 📁 Project Structure

```text
CentrAlign_AI_Project/
├── requirements.txt                 # Project dependencies
├── .env.example / .env              # Configuration & thresholds
├── run_mock_erp.py                  # Launcher for mock ERP web portal
├── run_worker.py                    # CLI launcher for the Autonomous Worker
├── mock_erp/                        # Simulated Enterprise ERP application
│   ├── app.py                       # FastAPI backend & verification API
│   ├── database.py                  # SQLite ledger & audit log across all domains
│   └── templates/                   # Tailwind web UI (Overview, Invoices, HR, Tickets, Inventory, CRM)
├── data/
│   ├── company_docs/                # Official PDF policies, handbooks, and contracts
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
│       ├── file_tool.py             # Enterprise file search tool
│       ├── document_tool.py         # PDF & document extraction tool
│       ├── enterprise_db_tool.py    # Direct enterprise database CRUD tool
│       ├── knowledge_tool.py        # Policy & governance retrieval tool
│       ├── analytics_tool.py        # Budget & inventory calculation tool
│       ├── browser_tool.py          # Playwright browser controller
│       └── erp_api_tool.py          # Internal ERP REST API tool
├── ui/
│   └── dashboard.py                 # Streamlit live monitoring dashboard
├── scripts/
│   ├── generate_company_data.py     # Master company data & document generator
│   └── generate_sample_invoices.py  # Sample invoice generator
└── tests/
    ├── test_flow.py                 # E2E Invoice flow integration test
    └── test_all_domains.py          # Full multi-department test suite
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

### 2. Generate Company Data & Seed Database
```powershell
python scripts/generate_company_data.py
```
This automatically generates:
- `data/company_docs/Employee_Handbook_and_Leave_Policy_2026.pdf`
- `data/company_docs/Procurement_and_Expense_Policy.pdf`
- `data/company_docs/IT_Security_and_Access_Control_Policy.pdf`
- `data/company_docs/Vendor_Contract_CyberShield_Security.pdf`
- `data/sample_invoices/Invoice_CompanyX_Latest.pdf` ($4,850.00, Due: 2026-11-15)
- `data/sample_invoices/Invoice_CompanyX_Old.pdf` ($1,200.00, Due: 2026-05-25)
- `data/sample_invoices/Invoice_CompanyY_Draft.pdf` ($2,890.50, Due: 2026-10-30)
- `data/sample_invoices/Invoice_AcmeSupplies_Q3.pdf` ($1,650.00)
- `data/sample_invoices/Invoice_GlobalCloud_Oct2026.pdf` ($2,150.00)
- Seeds the SQLite database with 250+ enterprise records (Staff, Tickets, Inventory, Budgets, Deals).

### 3. Start Mock Enterprise ERP Server (Terminal 1)
```powershell
python run_mock_erp.py
```
- **Live Cloud Deployment**: [https://autonomous-ai-task-worker.onrender.com/dashboard](https://autonomous-ai-task-worker.onrender.com/dashboard)
- **Local Sandbox**: `http://127.0.0.1:8000/dashboard` (or `/login`)
- Login credentials: `admin` / `company_secure_pass`
- Explore tabs: **Overview, Invoices, HR & Staff, IT Support, Inventory, CRM, and Policies**.

### 4. Run the Autonomous Worker (Terminal 2)

#### Option A: Interactive Streamlit AI Chatbot
```powershell
streamlit run ui/dashboard.py
```
- **Live Cloud AI Chatbot**: [https://autonomous-ai-task-worker.onrender.com/](https://autonomous-ai-task-worker.onrender.com/)
- **Local Sandbox**: `http://localhost:8501`
- Conversational chatbot interface with quick action starters, real-time reasoning logs, visual proof screenshots, persistent conversation history, and live verification tables.

#### Option B: Command Line Interface (CLI)
Run any task across any department:
```powershell
# 1. Invoice Processing
python run_worker.py "Find the latest invoice from Company X, extract the amount and due date, enter it into our internal system, and tell me once it is done."

# 2. HR & Vacation Approval
python run_worker.py "Find employee Sarah Jenkins, check her remaining annual leave balance, approve her pending vacation request, and update the HR system."

# 3. IT Support Helpdesk
python run_worker.py "Scan all open customer support tickets, identify any CRITICAL priority tickets, reassign them to Senior Engineer Alex Wong, and mark them IN_PROGRESS."

# 4. Inventory Replenishment
python run_worker.py "Audit our inventory warehouse for all items below the reorder threshold, calculate restock requirements, and generate a purchase order to the preferred supplier."

# 5. Financial Budget Analytics
python run_worker.py "Calculate the total Q3 marketing expenditure, compare it against the allocated department budget, and report budget variance."
```

#### Option C: Automated Multi-Domain Test Suite
```powershell
# Run all 6 enterprise department tests:
python tests/test_all_domains.py

# Run invoice integration test:
python tests/test_flow.py
```
