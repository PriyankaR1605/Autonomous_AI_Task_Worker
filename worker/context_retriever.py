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
    AI models (e.g. Gemini, OpenAI, Claude).
    """

    @staticmethod
    def _read_doc_if_exists(filename: str) -> str:
        filepath = os.path.join(settings.DOCS_DIR, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                pass
        return ""

    @classmethod
    def retrieve(cls, domain: str, prompt: str = "") -> Dict[str, Any]:
        """
        Retrieves real company records, database entries, and relevant policy clauses
        for the given domain or natural language query.
        """
        domain_clean = (domain or "general").lower()
        p_lower = (prompt or "").lower()

        # -------------------------------------------------------------
        # DOMAIN 1: HR & EMPLOYEE MANAGEMENT
        # -------------------------------------------------------------
        if domain_clean in ("hr_leave", "hr", "employee", "leave") or any(w in p_lower for w in ("employee", "leave", "vacation", "pto", "sarah jenkins", "salary", "hiring", "manager")):
            employees = get_all_employees()
            leave_requests = get_all_leave_requests()
            departments = get_all_departments()
            handbook = cls._read_doc_if_exists("Employee_Handbook_and_Leave_Policy_2026.txt")

            # Check if prompt targets a specific employee
            target_emp_data = None
            for emp in employees:
                if emp["name"].lower() in p_lower or emp["emp_code"].lower() in p_lower:
                    target_emp_data = emp
                    break

            return {
                "domain": "HR & Employee Directory",
                "total_employees": len(employees),
                "employees": employees,
                "leave_requests": leave_requests,
                "departments": departments,
                "target_employee": target_emp_data,
                "leave_policy_summary": handbook or "Annual leave allocation: 20 days standard PTO. Requests >5 days require manager approval."
            }

        # -------------------------------------------------------------
        # DOMAIN 2: INVOICES & ACCOUNTS PAYABLE
        # -------------------------------------------------------------
        elif domain_clean in ("invoice", "finance", "ap") or any(w in p_lower for w in ("invoice", "payable", "vendor", "bill", "due date", "company x", "company y", "acme")):
            invoices = get_all_invoices()
            procurement_policy = cls._read_doc_if_exists("Procurement_and_Expense_Policy.txt")
            
            # Locate sample invoice files in repository
            invoice_files = []
            if os.path.exists(settings.INVOICES_DIR):
                for f in os.listdir(settings.INVOICES_DIR):
                    if f.endswith((".pdf", ".txt")):
                        invoice_files.append(f)

            return {
                "domain": "Finance & Accounts Payable",
                "invoices_in_ledger": invoices,
                "available_invoice_files": invoice_files,
                "procurement_policy": procurement_policy or "Net-30 payment terms standard. Invoices >$3,000 require CFO sign-off.",
                "pending_payable_count": len([i for i in invoices if i.get("status") in ("PENDING", "UNPAID")])
            }

        # -------------------------------------------------------------
        # DOMAIN 3: IT SUPPORT & HELPDESK TICKETS
        # -------------------------------------------------------------
        elif domain_clean in ("ticket", "it_support", "helpdesk") or any(w in p_lower for w in ("ticket", "helpdesk", "incident", "alex wong", "critical priority")):
            tickets = get_all_tickets()
            it_security_policy = cls._read_doc_if_exists("IT_Security_and_Access_Control_Policy.txt")
            all_emp = get_all_employees()
            it_staff = [e for e in all_emp if e.get("department") in ("Engineering", "IT", "Operations")]

            return {
                "domain": "IT Support & Helpdesk Incident Queue",
                "total_tickets": len(tickets),
                "open_tickets": [t for t in tickets if t.get("status") != "RESOLVED"],
                "critical_tickets": [t for t in tickets if t.get("priority") == "CRITICAL"],
                "it_staff": it_staff,
                "it_security_policy": it_security_policy or "P1/Critical incidents must be assigned and acknowledged within 1 hour."
            }

        # -------------------------------------------------------------
        # DOMAIN 4: INVENTORY & SUPPLY CHAIN
        # -------------------------------------------------------------
        elif domain_clean in ("inventory", "supply_chain", "po") or any(w in p_lower for w in ("inventory", "reorder", "purchase order", "restock", "sku", "warehouse")):
            catalog = get_all_inventory()
            low_stock = get_low_stock_inventory()
            existing_pos = get_all_purchase_orders()

            return {
                "domain": "Inventory Catalog & Warehouse Procurement",
                "total_catalog_items": len(catalog),
                "all_items": catalog,
                "items_below_reorder_threshold": low_stock,
                "existing_purchase_orders": existing_pos,
                "low_stock_count": len(low_stock)
            }

        # -------------------------------------------------------------
        # DOMAIN 5: EXPENSE AUDITING & COMPLIANCE
        # -------------------------------------------------------------
        elif domain_clean in ("expense", "compliance") or any(w in p_lower for w in ("expense", "reimbursement", "spending policy", "credit card")):
            expenses = get_all_expenses()
            procurement_policy = cls._read_doc_if_exists("Procurement_and_Expense_Policy.txt")
            departments = get_all_departments()

            return {
                "domain": "Employee Expenses & Policy Compliance",
                "total_expenses": len(expenses),
                "all_expenses": expenses,
                "flagged_over_threshold": [e for e in expenses if e.get("amount", 0) > settings.HIGH_RISK_AMOUNT_THRESHOLD],
                "procurement_policy": procurement_policy or "Single expense items exceeding $1,000 require VP or CFO approval.",
                "departments": departments
            }

        # -------------------------------------------------------------
        # DOMAIN 6: BUDGETS & FINANCIAL ANALYTICS
        # -------------------------------------------------------------
        elif domain_clean in ("budget", "analytics") or any(w in p_lower for w in ("budget", "variance", "expenditure", "spend", "q3")):
            departments = get_all_departments()
            profile = get_company_profile()
            expenses = get_all_expenses()

            return {
                "domain": "Department Budgets & Financial Analytics",
                "company_profile": profile,
                "departments": departments,
                "recent_expenses": expenses[:15],
                "total_allocated_budget": sum(d.get("budget_q3", 0) for d in departments),
                "total_expenditure_q3": sum(d.get("spent_q3", 0) for d in departments)
            }

        # -------------------------------------------------------------
        # DOMAIN 7: GENERAL / CROSS-DEPARTMENTAL OVERVIEW
        # -------------------------------------------------------------
        else:
            profile = get_company_profile()
            departments = get_all_departments()
            kb_articles = search_knowledge_base(prompt or "company policy")
            employees = get_all_employees()
            tickets = get_all_tickets()
            low_stock = get_low_stock_inventory()

            return {
                "domain": "Enterprise Cross-Department Overview",
                "company_profile": profile,
                "departments": departments,
                "knowledge_base_articles": kb_articles,
                "operational_metrics": {
                    "total_employees": len(employees),
                    "open_support_tickets": len([t for t in tickets if t.get("status") != "RESOLVED"]),
                    "low_stock_skus": len(low_stock),
                    "departments_count": len(departments)
                }
            }
