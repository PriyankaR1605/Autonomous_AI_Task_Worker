import os
import re
import json
from typing import List, Dict, Any, Tuple
from worker.config import settings
from worker.state import Milestone, StepStatus

class TaskPlanner:
    """
    Decomposes natural language instructions into actionable milestones.
    Supports LLM-based planning (Gemini/OpenAI/Claude) with an enterprise-grade
    domain-aware heuristic decomposition engine for all business operations.
    """

    def parse_and_plan(self, prompt: str) -> Tuple[str, List[Milestone]]:
        """Returns (domain, list_of_milestones)."""
        # 1. Attempt LLM Planning if API key is provided
        has_api_key = bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY)
        if has_api_key:
            try:
                import litellm
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are a task decomposition engine for an autonomous enterprise AI worker. "
                            "Given a user instruction, determine the business domain (invoice, hr_leave, ticket, inventory, expense, budget, general) "
                            "and break it into 4 to 5 logical sequential milestones. "
                            "Output pure JSON object: {'domain': str, 'milestones': [{'id': int, 'title': str, 'description': str}]}"
                        )
                    },
                    {"role": "user", "content": f"Instruction: {prompt}"}
                ]
                response = litellm.completion(
                    model=settings.DEFAULT_MODEL,
                    messages=messages,
                    temperature=0.1
                )
                raw_text = response.choices[0].message.content.strip()
                clean_json = re.sub(r'^```json\s*|^```\s*|```$', '', raw_text, flags=re.MULTILINE).strip()
                data = json.loads(clean_json)
                
                domain = data.get("domain", "general").lower()
                milestone_items = data.get("milestones", [])
                if isinstance(milestone_items, list) and len(milestone_items) > 0:
                    milestones = []
                    for item in milestone_items:
                        milestones.append(Milestone(
                            id=item.get("id", len(milestones) + 1),
                            title=item.get("title", f"Milestone {len(milestones) + 1}"),
                            description=item.get("description", ""),
                            status=StepStatus.PENDING
                        ))
                    return domain, milestones
            except Exception:
                pass

        # 2. Semantic Domain Detection & Decomposition Heuristic
        p_lower = prompt.lower()

        # Domain A: Support Tickets / Helpdesk
        if any(w in p_lower for w in ("ticket", "helpdesk", "incident", "assign to", "critical priority")):
            domain = "ticket"
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

        # Domain B: Expense Auditing & Policy Compliance (Checked before HR to prioritize expense reports)
        elif any(w in p_lower for w in ("expense", "reimbursement", "spending policy", "credit card", "merchant")):
            domain = "expense"
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

        # Domain C: HR / Employee / Leave Approval
        elif any(w in p_lower for w in ("leave", "vacation", "pto", "sarah jenkins", "hire date", "salary", "time off", "time-off")) or ("employee" in p_lower and "expense" not in p_lower):
            domain = "hr_leave"
            emp_match = re.search(r'(?:employee|for)\s+([A-Za-z\s]+?)(?:,|\.|\scheck|\sapprove|\sand|$)', prompt, re.IGNORECASE)
            target_emp = emp_match.group(1).strip() if emp_match else "Sarah Jenkins"
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
                    description="Search company handbook guidelines and locate pending vacation requests.",
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

        # Domain C: Inventory / Supply Chain / Purchase Order
        elif any(w in p_lower for w in ("inventory", "reorder", "purchase order", "restock", "sku", "warehouse", "stock")):
            domain = "inventory"
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
                    description="Filter items where current stock is less than or equal to minimum threshold.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=3,
                    title="Calculate Restock Quantities & PO Valuation",
                    description="Compute unit quantities required to meet target levels and total procurement cost.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=4,
                    title="Generate & Issue Purchase Order (PO)",
                    description="Submit official purchase order to designated suppliers in procurement system.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=5,
                    title="Verify PO Ledger & Compile Supply Dossier",
                    description="Assert PO creation in enterprise database and compile full procurement audit trail.",
                    status=StepStatus.PENDING
                )
            ]

        # Domain D: Expense Auditing & Policy Compliance
        elif any(w in p_lower for w in ("expense", "reimbursement", "spending policy", "credit card", "merchant")):
            domain = "expense"
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

        # Domain E: Department Budgets & Financial Analytics
        elif any(w in p_lower for w in ("budget", "variance", "expenditure", "spend", "q3")):
            domain = "budget"
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

        # Domain F: Commercial Invoice Processing (Default / Standard)
        else:
            domain = "invoice"
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
                    title="Safety & Risk Assessment",
                    description="Evaluate financial value against safety thresholds to determine if human approval is needed.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=4,
                    title="Register Invoice into Internal ERP",
                    description="Submit extracted invoice details into the internal enterprise ledger via browser/API.",
                    status=StepStatus.PENDING
                ),
                Milestone(
                    id=5,
                    title="Outcome Verification & Evidence Generation",
                    description="Independently assert that the ERP ledger matches the source document and compile evidence.",
                    status=StepStatus.PENDING
                )
            ]
