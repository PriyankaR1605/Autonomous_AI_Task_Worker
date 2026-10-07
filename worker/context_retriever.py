import os
import re
from typing import Dict, Any, List, Optional

from mock_erp.database import (
    get_all_employees,
    get_employee,
    get_all_leave_requests,
    get_all_departments,
    get_all_invoices,
    get_all_tickets,
    get_all_inventory,
    get_low_stock_inventory,
    get_all_purchase_orders,
    get_all_expenses,
    get_company_profile,
    search_knowledge_base
)
from worker.config import settings

class EnterpriseContextRetriever:
    """
    Retrieves authentic domain-specific enterprise data and corporate governance
    policies from CentrAlign databases and document stores to feed directly into
    AI models (e.g. Gemini 3.8 Flash, OpenAI, Claude).
    """

    @staticmethod
    def _read_doc_or_pdf(filename: str) -> str:
        """Reads text from a file, falling back to PDF extraction if needed."""
        # 1. Check text file
        txt_name = filename if filename.endswith(".txt") else (os.path.splitext(filename)[0] + ".txt")
        filepath_txt = os.path.join(settings.DOCS_DIR, txt_name)
        if os.path.exists(filepath_txt):
            try:
                with open(filepath_txt, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        return content
            except Exception:
                pass

        # 2. Check PDF file
        pdf_name = filename if filename.endswith(".pdf") else (os.path.splitext(filename)[0] + ".pdf")
        filepath_pdf = os.path.join(settings.DOCS_DIR, pdf_name)
        if os.path.exists(filepath_pdf):
            try:
                import pypdf
                reader = pypdf.PdfReader(filepath_pdf)
                pages = [page.extract_text() or "" for page in reader.pages]
                extracted = "\n".join(pages).strip()
                if extracted:
                    return extracted
            except Exception:
                pass
        return ""

    @classmethod
    def retrieve(cls, domain: str, prompt: str = "") -> Dict[str, Any]:
        """
        Retrieves real company records, database entries, and relevant policy clauses
        for the given domain or natural language query.
        """
        domain_clean = (domain or "").lower().strip()
        p_lower = (prompt or "").lower()

        # -------------------------------------------------------------
        # STEP 1: RESOLVE TARGET DOMAIN (Strict parameter priority -> Keyword fallback)
        # -------------------------------------------------------------
        if domain_clean in ("hr_leave", "hr", "employee", "leave"):
            target_domain = "hr_leave"
        elif domain_clean in ("invoice", "finance", "ap"):
            target_domain = "invoice"
        elif domain_clean in ("ticket", "it_support", "helpdesk"):
            target_domain = "ticket"
        elif domain_clean in ("inventory", "supply_chain", "po"):
            target_domain = "inventory"
        elif domain_clean in ("expense", "compliance"):
            target_domain = "expense"
        elif domain_clean in ("budget", "analytics"):
            target_domain = "budget"
        elif domain_clean in ("policy", "governance", "handbook", "contract"):
            target_domain = "policy"
        elif domain_clean in ("general", "all", ""):
            # Fallback to keyword semantic inference when domain is general or unspecified
            if any(w in p_lower for w in ("employee", "leave", "vacation", "pto", "sarah jenkins", "salary", "hiring", "manager")):
                target_domain = "hr_leave"
            elif any(w in p_lower for w in ("invoice", "payable", "vendor", "bill", "due date", "company x", "company y", "acme")):
                target_domain = "invoice"
            elif any(w in p_lower for w in ("ticket", "helpdesk", "incident", "alex wong", "critical priority")):
                target_domain = "ticket"
            elif any(w in p_lower for w in ("inventory", "reorder", "purchase order", "restock", "sku", "warehouse")):
                target_domain = "inventory"
            elif any(w in p_lower for w in ("expense", "reimbursement", "spending policy", "credit card")):
                target_domain = "expense"
            elif any(w in p_lower for w in ("budget", "variance", "expenditure", "spend", "q3")):
                target_domain = "budget"
            elif any(w in p_lower for w in ("policy", "handbook", "compliance", "iso 27001", "governance", "contract")):
                target_domain = "policy"
            else:
                target_domain = "general"
        else:
            target_domain = "general"

        # -------------------------------------------------------------
        # STEP 2: BUILD CONTEXT PAYLOAD FOR TARGET DOMAIN
        # -------------------------------------------------------------

        # DOMAIN 1: HR & EMPLOYEE MANAGEMENT
        if target_domain == "hr_leave":
            employees = get_all_employees()
            leave_requests = get_all_leave_requests()
            departments = get_all_departments()
            handbook = cls._read_doc_or_pdf("Employee_Handbook_and_Leave_Policy_2026.txt")

            # Check if prompt targets a specific employee (full name or name parts)
            target_emp_data = None
            for emp in employees:
                emp_name = emp.get("name", "").lower()
                name_parts = emp_name.split()
                if (emp.get("emp_code", "").lower() in p_lower or
                    emp_name in p_lower or
                    any(p in p_lower for p in name_parts if len(p) > 2)):
                    target_emp_data = emp
                    break

            # Filter department if mentioned
            dept_matches = [d for d in departments if d.get("name", "").lower() in p_lower]
            target_dept = dept_matches[0] if dept_matches else None

            pending_leaves = [r for r in leave_requests if r.get("status") == "PENDING"]

            # Entity presence validation
            entity_found = True
            not_found_reason = ""
            queried_entity = ""

            emp_match = re.search(r'(?:employee|for|staff)\s+([A-Za-z\s]+?)(?:,|\.|\scheck|\sapprove|\sand|\'s|$)', prompt, re.IGNORECASE)
            code_match = re.search(r'\b(EMP-\d+)\b', prompt, re.IGNORECASE)
            if emp_match:
                candidate = emp_match.group(1).strip()
                if candidate.lower() not in ("all", "all employees", "leave", "vacation", "each", "any", "staff", "a", "an", "the"):
                    queried_entity = candidate
                    if not target_emp_data:
                        entity_found = False
                        not_found_reason = f"Employee '{candidate}' was not found in the enterprise employee directory."
            elif code_match:
                candidate = code_match.group(1).strip().upper()
                queried_entity = candidate
                if not target_emp_data:
                    entity_found = False
                    not_found_reason = f"Employee code '{candidate}' was not found in the enterprise employee directory."

            return {
                "domain": "HR & Employee Directory",
                "domain_key": "hr_leave",
                "total_employees": len(employees),
                "employees": employees,
                "leave_requests": leave_requests,
                "pending_leave_requests": pending_leaves,
                "departments": departments,
                "target_employee": target_emp_data,
                "target_department": target_dept,
                "entity_found": entity_found,
                "not_found_reason": not_found_reason,
                "queried_entity": queried_entity,
                "search_status": "FOUND" if entity_found else "NO_DATA_FOUND",
                "leave_policy_summary": handbook or "Annual leave allocation: 20 days standard PTO. Requests >5 days require manager approval."
            }

        # DOMAIN 2: INVOICES & ACCOUNTS PAYABLE
        elif target_domain == "invoice":
            invoices = get_all_invoices()
            procurement_policy = cls._read_doc_or_pdf("Procurement_and_Expense_Policy.txt")
            
            # Locate sample invoice files in repository
            invoice_files = []
            if os.path.exists(settings.INVOICES_DIR):
                for f in sorted(os.listdir(settings.INVOICES_DIR)):
                    if f.endswith((".pdf", ".txt")):
                        invoice_files.append(f)

            # Match target vendor if mentioned
            matched_invoices = []
            for inv in invoices:
                if inv.get("vendor_name", "").lower() in p_lower or inv.get("invoice_number", "").lower() in p_lower:
                    matched_invoices.append(inv)

            # Entity presence validation
            entity_found = True
            not_found_reason = ""
            queried_entity = ""

            vendor_match = re.search(r'(?:from|for|vendor)\s+([A-Za-z0-9\s]+?)(?:,|\.|\sand|\sextract|\senter|$)', prompt, re.IGNORECASE)
            inv_match = re.search(r'\b(INV-[A-Za-z0-9\-]+)\b', prompt, re.IGNORECASE)

            if inv_match:
                queried_entity = inv_match.group(1).strip().upper()
                has_inv = any(i.get("invoice_number", "").upper() == queried_entity for i in invoices)
                has_inv_file = any(queried_entity.lower() in f.lower() for f in invoice_files)
                if not has_inv and not has_inv_file:
                    entity_found = False
                    not_found_reason = f"Invoice '{queried_entity}' was not found in accounts payable records or document repository."
            elif vendor_match:
                cand = vendor_match.group(1).strip()
                if cand.lower() not in ("all", "latest", "the", "system", "our", "internal", "a", "an", "all vendors", "company"):
                    queried_entity = cand
                    has_vendor = any(cand.lower() in inv.get("vendor_name", "").lower() for inv in invoices)
                    has_vendor_file = any(re.sub(r'[^a-zA-Z0-9]', '', cand.lower()) in re.sub(r'[^a-zA-Z0-9]', '', f.lower()) for f in invoice_files)
                    if not has_vendor and not has_vendor_file:
                        entity_found = False
                        not_found_reason = f"Vendor '{cand}' was not found in accounts payable invoices or document files."

            return {
                "domain": "Finance & Accounts Payable",
                "domain_key": "invoice",
                "total_invoices_in_ledger": len(invoices),
                "invoices_in_ledger": invoices,
                "matched_invoices": matched_invoices,
                "available_invoice_files": invoice_files,
                "entity_found": entity_found,
                "not_found_reason": not_found_reason,
                "queried_entity": queried_entity,
                "search_status": "FOUND" if entity_found else "NO_DATA_FOUND",
                "procurement_policy": procurement_policy or "Net-30 payment terms standard. Invoices >$3,000 require CFO sign-off.",
                "pending_payable_count": len([i for i in invoices if i.get("status") in ("PENDING", "UNPAID")])
            }

        # DOMAIN 3: IT SUPPORT & HELPDESK TICKETS
        elif target_domain == "ticket":
            tickets = get_all_tickets()
            it_security_policy = cls._read_doc_or_pdf("IT_Security_and_Access_Control_Policy.txt")
            all_emp = get_all_employees()
            it_staff = [e for e in all_emp if e.get("department") in ("Engineering", "IT", "Operations")]

            critical_tickets = [t for t in tickets if t.get("priority") == "CRITICAL"]
            open_tickets = [t for t in tickets if t.get("status") != "RESOLVED"]

            # Entity presence validation
            entity_found = True
            not_found_reason = ""
            queried_entity = ""

            tck_match = re.search(r'\b(TCK-[A-Za-z0-9\-]+|INC-[A-Za-z0-9\-]+)\b', prompt, re.IGNORECASE)
            assignee_match = re.search(r'assign(?:\s+them)?\s+to\s+([A-Za-z\s]+?)(?:,|\.|\sand|\smark|$)', prompt, re.IGNORECASE)

            if tck_match:
                queried_entity = tck_match.group(1).strip().upper()
                if not any(t.get("ticket_number", "").upper() == queried_entity for t in tickets):
                    entity_found = False
                    not_found_reason = f"Ticket '{queried_entity}' was not found in the ITSM incident queue."
            elif assignee_match:
                cand = assignee_match.group(1).strip()
                if cand.lower() not in ("someone", "engineer", "staff", "agent", "senior engineer", "anyone"):
                    has_assignee = any(cand.lower() in e.get("name", "").lower() for e in all_emp)
                    if not has_assignee:
                        queried_entity = cand
                        entity_found = False
                        not_found_reason = f"Engineer/staff member '{cand}' was not found in the employee directory."

            return {
                "domain": "IT Support & Helpdesk Incident Queue",
                "domain_key": "ticket",
                "total_tickets": len(tickets),
                "open_tickets": open_tickets,
                "critical_tickets": critical_tickets,
                "it_staff": it_staff,
                "entity_found": entity_found,
                "not_found_reason": not_found_reason,
                "queried_entity": queried_entity,
                "search_status": "FOUND" if entity_found else "NO_DATA_FOUND",
                "it_security_policy": it_security_policy or "P1/Critical incidents must be assigned and acknowledged within 1 hour."
            }

        # DOMAIN 4: INVENTORY & SUPPLY CHAIN
        elif target_domain == "inventory":
            catalog = get_all_inventory()
            low_stock = get_low_stock_inventory()
            existing_pos = get_all_purchase_orders()

            # Target item if mentioned in prompt
            target_item = None
            for item in catalog:
                i_name = item.get("item_name", "").lower()
                name_words = [w for w in re.split(r'\W+', i_name) if len(w) > 3]
                if (item.get("sku", "").lower() in p_lower or
                    i_name in p_lower or
                    any(w in p_lower for w in name_words if w not in ("dell", "store", "enterprise"))):
                    target_item = item
                    break

            # Entity presence validation
            entity_found = True
            not_found_reason = ""
            queried_entity = ""

            sku_match = re.search(r'\b(SKU-[A-Za-z0-9\-]+)\b', prompt, re.IGNORECASE)
            item_match = re.search(r'(?:item|product|for|restock)\s+([A-Za-z0-9\s]+?)(?:,|\.|\sbelow|\scalculate|\sand|$)', prompt, re.IGNORECASE)

            if sku_match:
                queried_entity = sku_match.group(1).strip().upper()
                if not any(i.get("sku", "").upper() == queried_entity for i in catalog):
                    entity_found = False
                    not_found_reason = f"SKU '{queried_entity}' was not found in the warehouse inventory catalog."
            elif item_match:
                cand = item_match.group(1).strip()
                if cand.lower() not in ("all", "all items", "our inventory", "low stock", "threshold", "catalog", "warehouse", "items"):
                    if not target_item and not any(cand.lower() in i.get("item_name", "").lower() for i in catalog):
                        queried_entity = cand
                        entity_found = False
                        not_found_reason = f"Inventory item '{cand}' was not found in warehouse catalog."

            return {
                "domain": "Inventory Catalog & Warehouse Procurement",
                "domain_key": "inventory",
                "total_catalog_items": len(catalog),
                "all_items": catalog,
                "target_item": target_item,
                "items_below_reorder_threshold": low_stock,
                "existing_purchase_orders": existing_pos,
                "low_stock_count": len(low_stock),
                "entity_found": entity_found,
                "not_found_reason": not_found_reason,
                "queried_entity": queried_entity,
                "search_status": "FOUND" if entity_found else "NO_DATA_FOUND"
            }

        # DOMAIN 5: EXPENSE AUDITING & COMPLIANCE
        elif target_domain == "expense":
            expenses = get_all_expenses()
            procurement_policy = cls._read_doc_or_pdf("Procurement_and_Expense_Policy.txt")
            departments = get_all_departments()

            flagged = [e for e in expenses if e.get("amount", 0) > settings.HIGH_RISK_AMOUNT_THRESHOLD]
            pending = [e for e in expenses if e.get("status") == "PENDING"]

            # Entity presence validation
            entity_found = True
            not_found_reason = ""
            queried_entity = ""

            exp_match = re.search(r'\b(EXP-[A-Za-z0-9\-]+)\b', prompt, re.IGNORECASE)
            claimant_match = re.search(r'(?:employee|for|by)\s+([A-Za-z\s]+?)(?:,|\.|\sclaim|\sexpense|\sand|$)', prompt, re.IGNORECASE)

            if exp_match:
                queried_entity = exp_match.group(1).strip().upper()
                if not any(e.get("report_number", "").upper() == queried_entity for e in expenses):
                    entity_found = False
                    not_found_reason = f"Expense report '{queried_entity}' was not found in financial records."
            elif claimant_match:
                cand = claimant_match.group(1).strip()
                if cand.lower() not in ("all", "recent", "policy", "threshold", "travel", "procurement", "unapproved", "approval"):
                    if not any(cand.lower() in e.get("employee_name", "").lower() for e in expenses):
                        queried_entity = cand
                        entity_found = False
                        not_found_reason = f"No expense claims found for employee '{cand}'."

            return {
                "domain": "Employee Expenses & Policy Compliance",
                "domain_key": "expense",
                "total_expenses": len(expenses),
                "all_expenses": expenses,
                "flagged_over_threshold": flagged,
                "pending_claims": pending,
                "procurement_policy": procurement_policy or "Single expense items exceeding $1,000 require VP or CFO approval.",
                "departments": departments,
                "entity_found": entity_found,
                "not_found_reason": not_found_reason,
                "queried_entity": queried_entity,
                "search_status": "FOUND" if entity_found else "NO_DATA_FOUND"
            }

        # DOMAIN 6: BUDGETS & FINANCIAL ANALYTICS
        elif target_domain == "budget":
            departments = get_all_departments()
            profile = get_company_profile()
            expenses = get_all_expenses()

            # Highlight specific department if mentioned
            dept_matches = [d for d in departments if d.get("name", "").lower() in p_lower]
            target_dept = dept_matches[0] if dept_matches else None

            # Entity presence validation
            entity_found = True
            not_found_reason = ""
            queried_entity = ""

            dept_match = re.search(r'(?:department|for)\s+([A-Za-z\s&]+?)(?:,|\.|\sbudget|\sexpenditure|\sand|$)', prompt, re.IGNORECASE)
            if dept_match:
                cand = dept_match.group(1).strip()
                if cand.lower() not in ("all", "q3", "the", "our", "total", "each", "any", "marketing", "engineering", "sales", "hr", "it", "finance"):
                    if not target_dept and not any(cand.lower() in d.get("name", "").lower() for d in departments):
                        queried_entity = cand
                        entity_found = False
                        not_found_reason = f"Department '{cand}' was not found in company budget allocations."

            total_budget = sum(d.get("budget_q3", 0) for d in departments)
            total_spent = sum(d.get("spent_q3", 0) for d in departments)
            variance = total_budget - total_spent

            return {
                "domain": "Department Budgets & Financial Analytics",
                "domain_key": "budget",
                "company_profile": profile,
                "departments": departments,
                "target_department": target_dept,
                "recent_expenses": expenses[:15],
                "total_allocated_budget": total_budget,
                "total_expenditure_q3": total_spent,
                "overall_variance": variance,
                "variance_status": "Surplus" if variance >= 0 else "Deficit",
                "entity_found": entity_found,
                "not_found_reason": not_found_reason,
                "queried_entity": queried_entity,
                "search_status": "FOUND" if entity_found else "NO_DATA_FOUND"
            }

        # DOMAIN 7: CORPORATE POLICIES & GOVERNANCE
        elif target_domain == "policy":
            kb_articles = search_knowledge_base(prompt or "policy")
            handbook = cls._read_doc_or_pdf("Employee_Handbook_and_Leave_Policy_2026.txt")
            it_sec = cls._read_doc_or_pdf("IT_Security_and_Access_Control_Policy.txt")
            procurement = cls._read_doc_or_pdf("Procurement_and_Expense_Policy.txt")
            contract = cls._read_doc_or_pdf("Vendor_Contract_CyberShield_Security.txt")

            return {
                "domain": "Corporate Policies & Governance",
                "domain_key": "policy",
                "knowledge_base_articles": kb_articles,
                "policies": {
                    "employee_handbook_and_leave_policy": handbook,
                    "it_security_and_access_control": it_sec,
                    "procurement_and_expense_policy": procurement,
                    "vendor_contract_cybershield": contract
                },
                "governance_rules": [
                    "Standard Annual Leave: 20 days standard PTO. Requests >5 days require manager approval.",
                    "Payment Terms: Standard Net-30 terms. Vendor invoices >$3,000 require CFO sign-off.",
                    "Employee Expenses: Items >$1,000 require VP or CFO authorization.",
                    "IT Incident Response: Critical (P1) incidents must be acknowledged and assigned within 1 hour.",
                    "Supply Chain: Automated restocking triggered when inventory drops below safety threshold."
                ]
            }

        # DOMAIN 8: GENERAL / CROSS-DEPARTMENTAL OVERVIEW
        else:
            profile = get_company_profile()
            departments = get_all_departments()
            kb_articles = search_knowledge_base(prompt or "company policy")
            employees = get_all_employees()
            tickets = get_all_tickets()
            low_stock = get_low_stock_inventory()
            invoices = get_all_invoices()

            return {
                "domain": "Enterprise Cross-Department Overview",
                "domain_key": "general",
                "company_profile": profile,
                "departments": departments,
                "knowledge_base_articles": kb_articles,
                "operational_metrics": {
                    "total_employees": len(employees),
                    "open_support_tickets": len([t for t in tickets if t.get("status") != "RESOLVED"]),
                    "critical_tickets": len([t for t in tickets if t.get("priority") == "CRITICAL"]),
                    "low_stock_skus": len(low_stock),
                    "departments_count": len(departments),
                    "invoices_in_ledger": len(invoices)
                }
            }

    @classmethod
    def get_domain_summary(cls, domain: str) -> str:
        """Returns a concise human-readable summary badge string for the given domain."""
        ctx = cls.retrieve(domain)
        dom = ctx.get("domain_key", domain)
        if dom == "hr_leave":
            return f"{ctx.get('total_employees', 0)} Employees | {len(ctx.get('pending_leave_requests', []))} Pending Leaves"
        elif dom == "invoice":
            return f"{ctx.get('total_invoices_in_ledger', 0)} Invoices | {ctx.get('pending_payable_count', 0)} Pending Payable"
        elif dom == "ticket":
            return f"{len(ctx.get('open_tickets', []))} Open Tickets | {len(ctx.get('critical_tickets', []))} Critical P1"
        elif dom == "inventory":
            return f"{ctx.get('total_catalog_items', 0)} SKUs | {ctx.get('low_stock_count', 0)} Low Stock"
        elif dom == "expense":
            return f"{ctx.get('total_expenses', 0)} Expenses | {len(ctx.get('flagged_over_threshold', []))} Flagged >$1,000"
        elif dom == "budget":
            return f"${ctx.get('total_allocated_budget', 0):,.0f} Q3 Budget | {ctx.get('variance_status', 'Balanced')}"
        elif dom == "policy":
            return "4 Governance Handbooks & Policies | ISO 27001 Standards"
        return "Cross-Department Operations Ledger"
