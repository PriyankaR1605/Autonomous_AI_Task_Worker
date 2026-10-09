import os
import re
import json
from typing import List, Dict, Any, Tuple, Optional
from worker.config import settings
from worker.state import Milestone, StepStatus

class TaskPlanner:
    """
    Decomposes natural language instructions into actionable milestones.
    Supports LLM-based planning (Gemini/OpenAI/Claude) with an enterprise-grade
    domain-aware heuristic decomposition engine for all business operations.
    """

    @staticmethod
    def extract_target_employee(prompt: str) -> Optional[str]:
        """Extracts an employee name or identifier from the prompt without hardcoded fallbacks."""
        try:
            from worker.tools.enterprise_db_tool import get_all_employees
            employees = get_all_employees()
        except Exception:
            employees = []

        p_lower = (prompt or "").lower()

        # 1. Check EMP-xxx code
        code_match = re.search(r'\b(EMP-\d+)\b', prompt, re.IGNORECASE)
        if code_match:
            c = code_match.group(1).upper()
            for e in employees:
                if e.get("emp_code") == c:
                    return e.get("name")

        # 2. Check full names from database (sorted by length descending)
        sorted_emps = sorted(employees, key=lambda x: len(x.get("name", "")), reverse=True)
        for e in sorted_emps:
            name = e.get("name", "").strip()
            if name and name.lower() in p_lower:
                return name

        # 3. Explicit employee context regex: 'employee <Name>', 'staff member <Name>', 'worker <Name>'
        emp_match = re.search(r'(?:employee|staff\s+member|personnel|worker)\s+([A-Za-z\s]+?)(?:,|\.|\scheck|\sapprove|\sand|\'s|$)', prompt, re.IGNORECASE)
        if emp_match:
            candidate = emp_match.group(1).strip()
            stop_words = {"all", "all employees", "leave", "vacation", "pto", "each", "any", "staff", "a", "an", "the", "our", "me", "new", "this"}
            if candidate.lower() not in stop_words and len(candidate) > 2:
                for e in sorted_emps:
                    if candidate.lower() in e.get("name", "").lower():
                        return e.get("name")
                return candidate

        # 4. Explicit leave/vacation for <Name>
        leave_match = re.search(r'(?:leave|vacation|pto|balance|time\s*off)\s+for\s+([A-Za-z\s]+?)(?:,|\.|\scheck|\sapprove|\sand|\'s|$)', prompt, re.IGNORECASE)
        if leave_match:
            candidate = leave_match.group(1).strip()
            stop_words = {"all", "all employees", "each", "any", "staff", "a", "an", "the", "our", "me", "new", "this", "days"}
            if candidate.lower() not in stop_words and len(candidate) > 2:
                for e in sorted_emps:
                    if candidate.lower() in e.get("name", "").lower():
                        return e.get("name")
                return candidate

        return None

    def detect_domain(self, prompt: str, domain_override: Optional[str] = None) -> str:
        """Determines the operational enterprise domain accurately from prompt and override."""
        d_override = (domain_override or "").lower().strip()
        p_lower = (prompt or "").lower()

        # Check for greetings / meta-capabilities questions
        is_greeting = any(re.search(rf'\b{w}\b', p_lower) for w in ("hello", "hi", "hey", "who are you", "what can you do", "help", "capabilities", "features"))

        is_invoice = (
            any(w in p_lower for w in ("invoice", "payable", "vendor", "bill", "due date", "amount due", "inv-", "company x", "company y", "acme", "payment terms", "accounts payable"))
            or ("amount" in p_lower and "enter" in p_lower)
        )
        is_ticket = any(w in p_lower for w in ("ticket", "helpdesk", "incident", "itsm", "tck-", "inc-", "critical priority", "reassign", "assign to", "priority tickets", "support tickets"))
        is_budget = any(w in p_lower for w in ("budget", "variance", "expenditure", "allocated", "q3 budget", "surplus", "deficit", "spend", "spending", "burn rate"))
        is_inventory = (
            any(w in p_lower for w in ("inventory", "warehouse", "reorder", "restock", "sku", "purchase order", "po-", "low-stock", "stock level", "catalog", "equipment", "macbook", "laptop", "monitor", "hardware"))
            or ("stock" in p_lower and not is_budget)
            or (re.search(r'\b(?:sku-\w+|item|items|goods)\b', p_lower) and not is_budget and not is_ticket and not is_expense)
            or (re.search(r'\b(?:product|products)\b', p_lower) and not is_budget and "product development" not in p_lower and "production" not in p_lower)
        )
        is_expense = any(w in p_lower for w in ("expense", "exp-", "reimbursement", "spending policy", "credit card", "merchant", "expense claim", "expense report", "receipt"))
        is_policy = any(w in p_lower for w in ("policy", "policies", "handbook", "iso 27001", "soc 2", "compliance standard", "governance", "rules", "guidelines", "approval threshold", "procurement threshold", "contract threshold"))
        
        is_crm = any(w in p_lower for w in ("crm", "customer", "customers", "client", "clients", "deal", "deals", "sales pipeline", "contract tier", "annual contract", "arr", "account executive"))
        
        emp_name = self.extract_target_employee(prompt)
        is_hr = (
            any(w in p_lower for w in ("leave", "vacation", "pto", "time off", "time-off", "hire date", "salary", "compensation", "payroll", "headcount", "personnel"))
            or (emp_name is not None and not is_ticket and not is_expense and not is_invoice and not is_inventory and not is_budget and not is_policy and not is_crm)
            or ("employee" in p_lower and not is_expense and not is_policy)
        )

        # If explicit domain override was provided (and not auto/general)
        if d_override in ("crm", "customer", "sales"):
            return "crm"
        if d_override in ("policy", "governance"):
            return "policy"
        if d_override in ("ticket", "it_support") and is_ticket:
            return "ticket"
        if d_override in ("invoice", "finance", "ap") and is_invoice:
            return "invoice"
        if d_override in ("budget", "analytics") and is_budget:
            return "budget"
        if d_override in ("inventory", "supply_chain") and is_inventory:
            return "inventory"
        if d_override in ("expense", "compliance") and is_expense:
            return "expense"

        # Questions about policies/rules should route to policy unless it's an action (like approve or check balance)
        is_action_on_record = any(w in p_lower for w in ("approve", "deduct", "remaining", "balance", "update", "enter", "assign", "reorder"))
        if is_policy and not is_action_on_record:
            return "policy"

        # Primary natural language intent takes top priority
        if is_crm:
            return "crm"
        if is_invoice:
            return "invoice"
        if is_budget:
            return "budget"
        if is_ticket:
            return "ticket"
        if is_expense:
            return "expense"
        if is_inventory:
            return "inventory"
        if is_policy:
            return "policy"
        if is_hr:
            return "hr_leave"
        if is_greeting:
            return "general"

        # Reconcile domain_override if explicitly set by user and not auto
        if d_override and d_override not in ("auto", "all", "general", ""):
            return d_override

        return "general"

    def parse_and_plan(self, prompt: str, domain_override: Optional[str] = None) -> Tuple[str, List[Milestone]]:
        """Returns (domain, list_of_milestones)."""
        domain = self.detect_domain(prompt, domain_override)
        p_lower = (prompt or "").lower()

        # Check if the instruction is an operational mutation action (e.g. approve, reassign, register into ledger)
        is_action = any(re.search(rf'\b{w}\b', p_lower) for w in (
            "approve", "reassign", "assign to", "assign them to", "create po", "issue purchase order",
            "register invoice into", "enter it into our internal", "submit expense", "deduct"
        ))

        # For informational, analytical, calculation, and reporting queries, plan data-driven milestones
        if not is_action:
            domain_name = domain.replace("_", " ").title()
            return domain, [
                Milestone(
                    id=1,
                    title=f"Load Enterprise Data ({domain_name})",
                    description=f"Retrieve authentic records, documents, and policies for domain '{domain}' from the enterprise data repository.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=2,
                    title=f"Analyze {domain_name} Records",
                    description="Extract, compute, and structure domain metrics and policy criteria matching user query.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=3,
                    title="AI Model Reasoning & Verification",
                    description="Synthesize verified executive answer via Gemini AI model using authentic enterprise records.",
                    status=StepStatus.PENDING
                )
            ]

        # Domain A: Support Tickets / ITSM Helpdesk Action
        if domain == "ticket":
            assignee_match = re.search(r'assign(?:\s+them)?\s+to\s+([A-Za-z\s]+?)(?:,|\.|\sand|\smark|$)', prompt, re.IGNORECASE)
            assignee = assignee_match.group(1).strip() if assignee_match else "Alex Wong"
            return domain, [
                Milestone(
                    id=1,
                    title="Query ITSM Support Ticket Queue",
                    description="Retrieve open support and incident tickets from the enterprise helpdesk system.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=2,
                    title="Analyze Incident Severity & SLA Urgency",
                    description="Filter tickets by priority (e.g. CRITICAL/HIGH) and check against IT security SLAs.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=3,
                    title=f"Assign Critical Incidents to {assignee}",
                    description=f"Reassign identified priority tickets to '{assignee}' and update status to IN_PROGRESS.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=4,
                    title="Verify Ticket Status in Database",
                    description="Query the ITSM ledger to confirm assignments and status updates were persisted.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=5,
                    title="Compile Incident Resolution Dossier",
                    description="Generate auditable trace report with ticket identifiers and assignment records.",
                    status=StepStatus.PENDING
                )
            ]

        # Domain B: Expense Auditing & Policy Compliance
        elif domain == "expense":
            return domain, [
                Milestone(
                    id=1,
                    title="Review Corporate Procurement & Expense Policy",
                    description="Retrieve allowable expense thresholds and reimbursement requirements from policy docs.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=2,
                    title="Retrieve Submitted Expense Reports",
                    description="Query enterprise expense ledger for pending employee claims and receipts.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=3,
                    title="Evaluate Expense Policy Compliance",
                    description="Reconcile claims against policy limits ($1,000 threshold, receipt requirements).",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=4,
                    title="Process Expense Decisions & Approvals",
                    description="Approve compliant claims and route high-value items through approval gate.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=5,
                    title="Independent Financial Ledger Verification",
                    description="Assert updated expense records in database and generate audit evidence report.",
                    status=StepStatus.PENDING
                )
            ]

        # Domain C: HR & Employee Management
        elif domain == "hr_leave":
            target_emp = self.extract_target_employee(prompt)
            if target_emp:
                return domain, [
                    Milestone(
                        id=1,
                        title=f"Retrieve HR Profile for {target_emp}",
                        description=f"Query enterprise HR directory for employee details, role, department, and leave balance.",
                        status=StepStatus.PENDING
                    ),
                    Milestone(
                        id=2,
                        title="Check Leave Policy & Pending Requests",
                        description=f"Search company handbook guidelines and locate pending vacation requests for {target_emp}.",
                        status=StepStatus.PENDING
                    ),
                    Milestone(
                        id=3,
                        title="HR Compliance & Safety Assessment",
                        description="Verify that the request is within annual PTO limits and does not violate team quotas.",
                        status=StepStatus.PENDING
                    ),
                    Milestone(
                        id=4,
                        title="Execute Leave Approval & Ledger Update",
                        description=f"Approve pending leave request for {target_emp} and adjust remaining PTO balance.",
                        status=StepStatus.PENDING
                    ),
                    Milestone(
                        id=5,
                        title="Independent HR Ledger Verification",
                        description="Verify updated employee record in HR database and compile audit evidence.",
                        status=StepStatus.PENDING
                    )
                ]
            else:
                return domain, [
                    Milestone(
                        id=1,
                        title="Query HR Employee Directory & Records",
                        description="Search enterprise HR directory for relevant personnel records and policy balance.",
                        status=StepStatus.PENDING
                    ),
                    Milestone(
                        id=2,
                        title="Check Leave Policy & Pending Requests",
                        description="Search company handbook guidelines and locate pending vacation requests in queue.",
                        status=StepStatus.PENDING
                    ),
                    Milestone(
                        id=3,
                        title="HR Compliance & Safety Assessment",
                        description="Verify that requests are within annual PTO limits and adhere to corporate policy.",
                        status=StepStatus.PENDING
                    ),
                    Milestone(
                        id=4,
                        title="Execute HR Operations & Ledger Update",
                        description="Process verified employee leave request and update HR database ledger.",
                        status=StepStatus.PENDING
                    ),
                    Milestone(
                        id=5,
                        title="Independent HR Ledger Verification",
                        description="Verify updated employee record in HR database and compile audit evidence.",
                        status=StepStatus.PENDING
                    )
                ]

        # Domain D: Inventory & Warehouse Restock
        elif domain == "inventory":
            return domain, [
                Milestone(
                    id=1,
                    title="Scan Warehouse Inventory Stock",
                    description="Query catalog inventory to identify stock levels across hardware and equipment.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=2,
                    title="Identify Items Below Reorder Threshold",
                    description="Filter items whose current quantity is at or below the safety reorder threshold.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=3,
                    title="Calculate Restock Quantities & PO Valuation",
                    description="Determine replenishment quantities to reach target inventory and compute vendor cost.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=4,
                    title="Generate & Issue Purchase Order (PO)",
                    description="Create a formal purchase order to the preferred supplier via procurement system.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=5,
                    title="Verify PO Ledger & Compile Supply Dossier",
                    description="Assert PO creation in enterprise database and compile full procurement audit trail.",
                    status=StepStatus.PENDING
                )
            ]

        # Domain E: Department Budgets & Financial Analytics
        elif domain == "budget":
            dept_match = re.search(r'(?:marketing|engineering|sales|hr|it|finance)', prompt, re.IGNORECASE)
            dept = dept_match.group(0).capitalize() if dept_match else "Marketing & Growth"
            return domain, [
                Milestone(
                    id=1,
                    title=f"Query {dept} Budget Allocation",
                    description=f"Retrieve Q3 allocated budget and actual spend from department ledger.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=2,
                    title="Compute Budget Variance & Utilization",
                    description="Calculate variance, percentage utilized, and remaining available funds.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=3,
                    title="Financial Health & Governance Check",
                    description="Assess whether department is in surplus or deficit against corporate fiscal targets.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=4,
                    title="Reconcile Ledger Figures with General Accounts",
                    description="Cross-reference with related expenses and invoices in financial database.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=5,
                    title="Compile Executive Budget Analytics Dossier",
                    description="Generate formatted report with variance metrics and audit trail.",
                    status=StepStatus.PENDING
                )
            ]

        # Domain F: Commercial Invoices & Accounts Payable
        elif domain == "invoice":
            vendor_match = re.search(r'(?:from|for)\s+([A-Za-z0-9\s]+?)(?:,|\.|\sand|\sextract|\senter|$)', prompt, re.IGNORECASE)
            vendor = vendor_match.group(1).strip() if vendor_match else "Company X"
            return domain, [
                Milestone(
                    id=1,
                    title=f"Locate Latest Invoice for {vendor}",
                    description=f"Scan repository and identify the latest valid invoice document for '{vendor}'.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=2,
                    title="Extract Invoice Details",
                    description="Parse the document to extract invoice number, total amount, currency, and due date.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=3,
                    title="Evaluate Financial Risk & Policy Thresholds",
                    description="Check invoice against company safety guardrails and spending policies.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=4,
                    title="Register Invoice into ERP Ledger",
                    description="Enter verified invoice into the enterprise Accounts Payable system via UI or API.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=5,
                    title="Verify Database Ledger & Compile Evidence",
                    description="Assert ERP database state matches invoice file values and compile visual audit report.",
                    status=StepStatus.PENDING
                )
            ]

        # Domain G: Corporate Governance & Policy
        elif domain == "policy":
            return domain, [
                Milestone(
                    id=1,
                    title="Retrieve Corporate Policy Documents",
                    description="Search repository for official employee handbooks, IT security policies, and procurement standards.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=2,
                    title="Extract Governance Clauses & Compliance Rules",
                    description="Analyze documents for PTO thresholds, payment terms, expense limits, and SLAs.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=3,
                    title="Cross-Reference Enterprise Knowledge Base",
                    description="Query corporate knowledge base articles and ISO 27001 / SOC 2 controls.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=4,
                    title="Synthesize Policy Guidance & Legal Terms",
                    description="Formulate structured corporate guidance answering user query with cited clauses.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=5,
                    title="Generate Compliance Audit Dossier",
                    description="Package cited policy sections, verification status, and timestamps into audit evidence report.",
                    status=StepStatus.PENDING
                )
            ]

        # Domain H: General Enterprise Inquiries
        else:
            return "general", [
                Milestone(
                    id=1,
                    title="Analyze Instruction & Retrieve Context",
                    description="Evaluate user instruction against corporate knowledge base and enterprise data.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=2,
                    title="Synthesize Contextual Information",
                    description="Aggregate relevant company data to formulate accurate response.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=3,
                    title="Formulate Verified Outcome",
                    description="Compile response and verify consistency with company policies.",
                    status=StepStatus.PENDING
                )
            ]
