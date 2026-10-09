import os
import re
import json
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
    policies from CentrAlign databases and document stores (D:\\Projects\\CentrAlign_AI_Project\\data)
    to feed directly into AI models (e.g. Gemini 3.5 Flash, Gemini 3.8 Flash, OpenAI, Claude).
    """

    @staticmethod
    def load_table_records(table_base_name: str) -> List[Dict[str, Any]]:
        """
        Loads authentic enterprise table records directly from data/enterprise_tables/.
        Checks JSON first, then falls back to CSV.
        """
        json_path = os.path.join(settings.TABLES_DIR, f"{table_base_name}.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and "domains" in data:
                        return data.get("domains", {}).get(table_base_name, [])
            except Exception:
                pass

        csv_path = os.path.join(settings.TABLES_DIR, f"{table_base_name}.csv")
        if os.path.exists(csv_path):
            try:
                import csv
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    return list(reader)
            except Exception:
                pass
        return []

    @staticmethod
    def load_doc_text(filename: str, subfolder: str = "company_docs") -> str:
        """
        Loads document text directly from data/{subfolder}.
        Checks TXT first, then extracts text from PDF if needed.
        """
        folder_path = os.path.join(settings.DATA_DIR, subfolder)
        # 1. Check TXT
        txt_name = filename if filename.endswith(".txt") else (os.path.splitext(filename)[0] + ".txt")
        filepath_txt = os.path.join(folder_path, txt_name)
        if os.path.exists(filepath_txt):
            try:
                with open(filepath_txt, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        return content
            except Exception:
                pass

        # 2. Check PDF
        pdf_name = filename if filename.endswith(".pdf") else (os.path.splitext(filename)[0] + ".pdf")
        filepath_pdf = os.path.join(folder_path, pdf_name)
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
    def _read_doc_or_pdf(cls, filename: str) -> str:
        """Backward compatible doc reader."""
        return cls.load_doc_text(filename, "company_docs")

    @classmethod
    def retrieve(cls, domain: str, prompt: str = "") -> Dict[str, Any]:
        """
        Retrieves real company records, database entries, and relevant policy clauses
        directly from D:\\Projects\\CentrAlign_AI_Project\\data for the given domain
        or natural language query.
        """
        domain_clean = (domain or "").lower().strip()
        p_lower = (prompt or "").lower()

        # -------------------------------------------------------------
        # STEP 1: RESOLVE TARGET DOMAIN (Smart Intent Detection)
        # -------------------------------------------------------------
        is_greeting = any(re.search(rf'\b{w}\b', p_lower) for w in (
            "hello", "hi", "hey", "who are you", "what can you do", "help", "capabilities", "features"
        ))

        is_invoice = (
            any(w in p_lower for w in ("invoice", "payable", "vendor", "bill", "due date", "amount due", "inv-", "company x", "company y", "acme", "payment terms", "accounts payable"))
            or ("amount" in p_lower and "enter" in p_lower)
        )
        is_ticket = any(w in p_lower for w in ("ticket", "helpdesk", "incident", "itsm", "tck-", "inc-", "critical priority", "reassign", "assign to", "priority tickets", "support tickets"))
        is_inventory = (
            any(w in p_lower for w in ("inventory", "warehouse", "reorder", "restock", "sku", "purchase order", "po-", "low-stock", "stock level", "catalog", "equipment", "macbook", "laptop", "monitor", "hardware"))
            or (re.search(r'\b(?:sku-\w+|item|items|goods)\b', p_lower) and "ticket" not in p_lower and "expense" not in p_lower)
            or (re.search(r'\b(?:product|products)\b', p_lower) and "product development" not in p_lower and "production" not in p_lower)
        )
        is_budget = any(w in p_lower for w in ("budget", "variance", "expenditure", "allocated", "q3 budget", "surplus", "deficit", "spend", "spending", "burn rate"))
        is_expense = any(w in p_lower for w in ("expense", "exp-", "reimbursement", "spending policy", "credit card", "merchant", "expense claim", "expense report", "receipt"))
        is_policy = any(w in p_lower for w in ("policy", "policies", "handbook", "iso 27001", "soc 2", "compliance standard", "governance", "guidelines", "approval threshold", "procurement threshold"))
        is_crm = any(w in p_lower for w in ("crm", "customer", "customers", "client", "clients", "deal", "deals", "sales pipeline", "contract tier", "annual contract", "arr", "account executive"))
        
        from worker.planner import TaskPlanner
        emp_name = TaskPlanner.extract_target_employee(prompt)
        is_hr = (
            any(w in p_lower for w in ("leave", "vacation", "pto", "time off", "time-off", "hire date", "salary", "compensation", "payroll", "headcount", "personnel", "staff directory"))
            or (emp_name is not None and not is_ticket and not is_expense and not is_invoice and not is_inventory and not is_budget and not is_policy and not is_crm)
            or ("employee" in p_lower and not is_expense and not is_policy)
        )

        # Primary natural language intent routing
        if is_crm:
            target_domain = "crm"
        elif is_invoice:
            target_domain = "invoice"
        elif is_ticket:
            target_domain = "ticket"
        elif is_inventory:
            target_domain = "inventory"
        elif is_expense:
            target_domain = "expense"
        elif is_budget:
            target_domain = "budget"
        elif is_hr:
            target_domain = "hr_leave"
        elif is_policy:
            target_domain = "policy"
        elif is_greeting:
            target_domain = "general"
        elif domain_clean and domain_clean not in ("auto", "all", "general", ""):
            target_domain = domain_clean
        else:
            target_domain = "general"

        # -------------------------------------------------------------
        # STEP 2: BUILD CONTEXT PAYLOAD DIRECTLY FROM DATA/ FOLDER
        # -------------------------------------------------------------

        # DOMAIN 1: HR & EMPLOYEE MANAGEMENT
        if target_domain == "hr_leave":
            employees = cls.load_table_records("employees_master_table") or get_all_employees()
            leave_requests = cls.load_table_records("leave_requests_master_table") or get_all_leave_requests()
            departments = cls.load_table_records("departments_master_table") or get_all_departments()
            handbook = cls.load_doc_text("Employee_Handbook_and_Leave_Policy_2026.txt", "company_docs")

            source_files = [
                "data/enterprise_tables/employees_master_table.json",
                "data/enterprise_tables/leave_requests_master_table.json",
                "data/enterprise_tables/departments_master_table.json",
                "data/company_docs/Employee_Handbook_and_Leave_Policy_2026.txt"
            ]

            target_emp_data = None
            code_match = re.search(r'\b(EMP-\d+)\b', prompt, re.IGNORECASE)
            if code_match:
                c = code_match.group(1).upper()
                for emp in employees:
                    if emp.get("emp_code") == c:
                        target_emp_data = emp
                        break

            if not target_emp_data:
                sorted_emps = sorted(employees, key=lambda x: len(x.get("name", "")), reverse=True)
                for emp in sorted_emps:
                    name_cand = emp.get("name", "").strip()
                    if name_cand and name_cand.lower() in p_lower:
                        target_emp_data = emp
                        break

            dept_matches = [d for d in departments if d.get("name", "").lower() in p_lower]
            target_dept = dept_matches[0] if dept_matches else None
            pending_leaves = [r for r in leave_requests if r.get("status") == "PENDING"]

            entity_found = True
            not_found_reason = ""
            queried_entity = ""

            if code_match and not target_emp_data:
                candidate = code_match.group(1).strip().upper()
                queried_entity = candidate
                entity_found = False
                not_found_reason = f"Employee code '{candidate}' was not found in the enterprise employee directory ({len(employees)} records)."

            total_salary = sum(float(e.get("salary", 0)) for e in employees)
            avg_salary = (total_salary / len(employees)) if employees else 0.0
            dept_salaries = {}
            for e in employees:
                d_name = e.get("department", "Unassigned")
                dept_salaries[d_name] = dept_salaries.get(d_name, 0.0) + float(e.get("salary", 0))

            return {
                "domain": "HR & Employee Directory",
                "domain_key": "hr_leave",
                "source_data_folder": settings.DATA_DIR,
                "source_files_loaded": source_files,
                "total_employees": len(employees),
                "employees": employees,
                "total_salary_payroll": total_salary,
                "average_salary": avg_salary,
                "salary_by_department": dept_salaries,
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
            invoices = cls.load_table_records("invoices_master_table") or get_all_invoices()
            invoices_register = cls.load_doc_text("Master_Invoices_Register.txt", "sample_invoices")
            procurement_policy = cls.load_doc_text("Procurement_and_Expense_Policy.txt", "company_docs")

            source_files = [
                "data/enterprise_tables/invoices_master_table.json",
                "data/sample_invoices/Master_Invoices_Register.txt",
                "data/company_docs/Procurement_and_Expense_Policy.txt"
            ]

            invoice_files = []
            if os.path.exists(settings.INVOICES_DIR):
                for f in sorted(os.listdir(settings.INVOICES_DIR)):
                    if f.endswith((".pdf", ".txt")):
                        invoice_files.append(f)

            matched_invoices = []
            for inv in invoices:
                if (inv.get("vendor_name", "").lower() in p_lower and len(inv.get("vendor_name", "")) > 3) or \
                   (inv.get("invoice_number", "").lower() in p_lower):
                    matched_invoices.append(inv)

            entity_found = True
            not_found_reason = ""
            queried_entity = ""

            inv_match = re.search(r'\b(INV-[A-Za-z0-9\-]+)\b', prompt, re.IGNORECASE)
            if inv_match:
                queried_entity = inv_match.group(1).strip().upper()
                has_inv = any(i.get("invoice_number", "").upper() == queried_entity for i in invoices)
                has_inv_file = any(queried_entity.lower() in f.lower() for f in invoice_files)
                if not has_inv and not has_inv_file:
                    entity_found = False
                    not_found_reason = f"Invoice '{queried_entity}' was not found in accounts payable records ({len(invoices)} invoices) or sample invoices."

            total_invoice_amt = sum(float(i.get("amount", 0)) for i in invoices)
            unpaid_invoices = [i for i in invoices if i.get("status") in ("PENDING", "PENDING_APPROVAL", "UNPAID")]
            unpaid_amt = sum(float(i.get("amount", 0)) for i in unpaid_invoices)

            return {
                "domain": "Finance & Accounts Payable",
                "domain_key": "invoice",
                "source_data_folder": settings.DATA_DIR,
                "source_files_loaded": source_files,
                "total_invoices_in_ledger": len(invoices),
                "invoices_in_ledger": invoices,
                "total_invoices_amount": total_invoice_amt,
                "unpaid_invoices_amount": unpaid_amt,
                "matched_invoices": matched_invoices,
                "available_invoice_files": invoice_files,
                "master_invoices_register_excerpt": invoices_register[:3000] if invoices_register else "",
                "entity_found": entity_found,
                "not_found_reason": not_found_reason,
                "queried_entity": queried_entity,
                "search_status": "FOUND" if entity_found else "NO_DATA_FOUND",
                "procurement_policy": procurement_policy or "Net-30 payment terms standard. Invoices >$3,000 require CFO sign-off.",
                "pending_payable_count": len(unpaid_invoices)
            }

        # DOMAIN 3: IT SUPPORT & HELPDESK TICKETS
        elif target_domain == "ticket":
            tickets = cls.load_table_records("support_tickets_master_table") or get_all_tickets()
            it_security_policy = cls.load_doc_text("IT_Security_and_Access_Control_Policy.txt", "company_docs")
            all_emp = cls.load_table_records("employees_master_table") or get_all_employees()
            it_staff = [e for e in all_emp if e.get("department") in ("Engineering", "IT & Security", "IT", "Operations")]

            source_files = [
                "data/enterprise_tables/support_tickets_master_table.json",
                "data/company_docs/IT_Security_and_Access_Control_Policy.txt",
                "data/enterprise_tables/employees_master_table.json"
            ]

            critical_tickets = [t for t in tickets if t.get("priority") == "CRITICAL"]
            open_tickets = [t for t in tickets if t.get("status") != "RESOLVED"]

            entity_found = True
            not_found_reason = ""
            queried_entity = ""

            tck_match = re.search(r'\b(TCK-[A-Za-z0-9\-]+|INC-[A-Za-z0-9\-]+)\b', prompt, re.IGNORECASE)
            if tck_match:
                queried_entity = tck_match.group(1).strip().upper()
                if not any(t.get("ticket_number", "").upper() == queried_entity for t in tickets):
                    entity_found = False
                    not_found_reason = f"Ticket '{queried_entity}' was not found in the ITSM incident queue ({len(tickets)} tickets)."

            return {
                "domain": "IT Support & Helpdesk Incident Queue",
                "domain_key": "ticket",
                "source_data_folder": settings.DATA_DIR,
                "source_files_loaded": source_files,
                "total_tickets": len(tickets),
                "tickets": tickets,
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
            catalog = cls.load_table_records("inventory_master_table") or get_all_inventory()
            purchase_orders = cls.load_table_records("purchase_orders_master_table") or get_all_purchase_orders()
            procurement_policy = cls.load_doc_text("Procurement_and_Expense_Policy.txt", "company_docs")

            source_files = [
                "data/enterprise_tables/inventory_master_table.json",
                "data/enterprise_tables/purchase_orders_master_table.json",
                "data/company_docs/Procurement_and_Expense_Policy.txt"
            ]

            low_stock = [
                item for item in catalog
                if int(item.get("stock_on_hand", 0)) <= int(item.get("reorder_threshold", 0))
            ]

            target_item = None
            for item in catalog:
                i_name = item.get("item_name", "").lower()
                sku = item.get("sku", "").lower()
                if (sku in p_lower) or (len(i_name) > 3 and i_name in p_lower):
                    target_item = item
                    break

            entity_found = True
            not_found_reason = ""
            queried_entity = ""

            sku_match = re.search(r'\b(SKU-[A-Za-z0-9\-]+)\b', prompt, re.IGNORECASE)
            if sku_match:
                queried_entity = sku_match.group(1).strip().upper()
                if not any(i.get("sku", "").upper() == queried_entity for i in catalog):
                    entity_found = False
                    not_found_reason = f"SKU '{queried_entity}' was not found in the warehouse inventory catalog ({len(catalog)} SKUs)."

            total_inv_val = sum(float(i.get("stock_on_hand", 0)) * float(i.get("unit_cost", 0)) for i in catalog)
            total_units = sum(int(i.get("stock_on_hand", 0)) for i in catalog)

            return {
                "domain": "Inventory Catalog & Warehouse Procurement",
                "domain_key": "inventory",
                "source_data_folder": settings.DATA_DIR,
                "source_files_loaded": source_files,
                "total_catalog_items": len(catalog),
                "total_inventory_valuation": total_inv_val,
                "total_units_on_hand": total_units,
                "all_items": catalog,
                "target_item": target_item,
                "items_below_reorder_threshold": low_stock,
                "existing_purchase_orders": purchase_orders,
                "low_stock_count": len(low_stock),
                "entity_found": entity_found,
                "not_found_reason": not_found_reason,
                "queried_entity": queried_entity,
                "search_status": "FOUND" if entity_found else "NO_DATA_FOUND",
                "procurement_policy": procurement_policy or "Reorder triggers automatically when inventory drops below safety threshold."
            }

        # DOMAIN 5: EXPENSE AUDITING & COMPLIANCE
        elif target_domain == "expense":
            expenses = cls.load_table_records("expenses_master_table") or get_all_expenses()
            departments = cls.load_table_records("departments_master_table") or get_all_departments()
            procurement_policy = cls.load_doc_text("Procurement_and_Expense_Policy.txt", "company_docs")

            source_files = [
                "data/enterprise_tables/expenses_master_table.json",
                "data/enterprise_tables/departments_master_table.json",
                "data/company_docs/Procurement_and_Expense_Policy.txt"
            ]

            flagged = [e for e in expenses if float(e.get("amount", 0)) > settings.HIGH_RISK_AMOUNT_THRESHOLD]
            pending = [e for e in expenses if e.get("status") in ("SUBMITTED", "PENDING")]
            total_exp_amt = sum(float(e.get("amount", 0)) for e in expenses)

            entity_found = True
            not_found_reason = ""
            queried_entity = ""

            exp_match = re.search(r'\b(EXP-[A-Za-z0-9\-]+)\b', prompt, re.IGNORECASE)
            if exp_match:
                queried_entity = exp_match.group(1).strip().upper()
                if not any(e.get("report_number", "").upper() == queried_entity for e in expenses):
                    entity_found = False
                    not_found_reason = f"Expense report '{queried_entity}' was not found in financial records ({len(expenses)} reports)."

            return {
                "domain": "Employee Expenses & Policy Compliance",
                "domain_key": "expense",
                "source_data_folder": settings.DATA_DIR,
                "source_files_loaded": source_files,
                "total_expenses": len(expenses),
                "total_expense_amount": total_exp_amt,
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
            departments = cls.load_table_records("departments_master_table") or get_all_departments()
            expenses = cls.load_table_records("expenses_master_table") or get_all_expenses()
            invoices = cls.load_table_records("invoices_master_table") or get_all_invoices()
            profile = get_company_profile()

            source_files = [
                "data/enterprise_tables/departments_master_table.json",
                "data/enterprise_tables/expenses_master_table.json",
                "data/enterprise_tables/invoices_master_table.json"
            ]

            target_dept = None
            for d in departments:
                d_name = d.get("name", "").lower()
                words = [w for w in re.split(r'[\s&]+', d_name) if len(w) > 2]
                if d_name in p_lower or any(w in p_lower for w in words):
                    target_dept = d
                    break

            total_budget = sum(float(d.get("budget_q3", 0)) for d in departments)
            total_spent = sum(float(d.get("spent_q3", 0)) for d in departments)
            variance = total_budget - total_spent

            return {
                "domain": "Department Budgets & Financial Analytics",
                "domain_key": "budget",
                "source_data_folder": settings.DATA_DIR,
                "source_files_loaded": source_files,
                "company_profile": profile,
                "departments": departments,
                "target_department": target_dept,
                "recent_expenses": expenses[:15],
                "total_allocated_budget": total_budget,
                "total_expenditure_q3": total_spent,
                "overall_variance": variance,
                "variance_status": "Surplus" if variance >= 0 else "Deficit",
                "entity_found": True,
                "not_found_reason": "",
                "queried_entity": "",
                "search_status": "FOUND"
            }

        # DOMAIN 7: CRM ACCOUNTS & SALES DEALS
        elif target_domain == "crm":
            customers = cls.load_table_records("customers_crm_master_table")
            deals = cls.load_table_records("deals_master_table")

            source_files = [
                "data/enterprise_tables/customers_crm_master_table.json",
                "data/enterprise_tables/deals_master_table.json"
            ]

            total_arr = sum(float(c.get("annual_contract_value", 0)) for c in customers)
            total_deals_val = sum(float(d.get("deal_value", 0)) for d in deals)

            entity_found = True
            not_found_reason = ""
            queried_entity = ""

            cust_match = re.search(r'\b(CUST-[A-Za-z0-9\-]+)\b', prompt, re.IGNORECASE)
            if cust_match:
                queried_entity = cust_match.group(1).strip().upper()
                if not any(c.get("customer_code", "").upper() == queried_entity for c in customers):
                    entity_found = False
                    not_found_reason = f"Customer code '{queried_entity}' was not found in CRM client directory ({len(customers)} accounts)."

            return {
                "domain": "CRM Accounts & Sales Pipeline",
                "domain_key": "crm",
                "source_data_folder": settings.DATA_DIR,
                "source_files_loaded": source_files,
                "total_customers": len(customers),
                "customers": customers,
                "total_deals": len(deals),
                "deals": deals,
                "total_arr_contract_value": total_arr,
                "total_deals_pipeline_value": total_deals_val,
                "entity_found": entity_found,
                "not_found_reason": not_found_reason,
                "queried_entity": queried_entity,
                "search_status": "FOUND" if entity_found else "NO_DATA_FOUND"
            }

        # DOMAIN 8: CORPORATE POLICIES & GOVERNANCE
        elif target_domain == "policy":
            handbook = cls.load_doc_text("Employee_Handbook_and_Leave_Policy_2026.txt", "company_docs")
            it_sec = cls.load_doc_text("IT_Security_and_Access_Control_Policy.txt", "company_docs")
            procurement = cls.load_doc_text("Procurement_and_Expense_Policy.txt", "company_docs")
            contract = cls.load_doc_text("Vendor_Contract_CyberShield_Security.txt", "company_docs")
            kb_articles = search_knowledge_base(prompt or "policy")

            source_files = [
                "data/company_docs/Employee_Handbook_and_Leave_Policy_2026.txt",
                "data/company_docs/IT_Security_and_Access_Control_Policy.txt",
                "data/company_docs/Procurement_and_Expense_Policy.txt",
                "data/company_docs/Vendor_Contract_CyberShield_Security.txt"
            ]

            return {
                "domain": "Corporate Policies & Governance",
                "domain_key": "policy",
                "source_data_folder": settings.DATA_DIR,
                "source_files_loaded": source_files,
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
                ],
                "entity_found": True,
                "search_status": "FOUND"
            }

        # DOMAIN 9: GENERAL / CROSS-DEPARTMENTAL OVERVIEW
        else:
            unified_path = os.path.join(settings.TABLES_DIR, "ALL_DOMAINS_ENTERPRISE_MASTER_DATASET.json")
            master_dataset = {}
            if os.path.exists(unified_path):
                try:
                    with open(unified_path, "r", encoding="utf-8") as f:
                        master_dataset = json.load(f)
                except Exception:
                    pass

            source_files = [
                "data/enterprise_tables/ALL_DOMAINS_ENTERPRISE_MASTER_DATASET.json"
            ]

            profile = get_company_profile()
            departments = cls.load_table_records("departments_master_table") or get_all_departments()
            employees = cls.load_table_records("employees_master_table") or get_all_employees()
            tickets = cls.load_table_records("support_tickets_master_table") or get_all_tickets()
            inventory = cls.load_table_records("inventory_master_table") or get_all_inventory()
            invoices = cls.load_table_records("invoices_master_table") or get_all_invoices()
            customers = cls.load_table_records("customers_crm_master_table")
            deals = cls.load_table_records("deals_master_table")
            expenses = cls.load_table_records("expenses_master_table") or get_all_expenses()

            return {
                "domain": "Enterprise Cross-Department Overview",
                "domain_key": "general",
                "source_data_folder": settings.DATA_DIR,
                "source_files_loaded": source_files,
                "company_profile": profile,
                "departments": departments,
                "master_dataset_summary": {
                    "total_employees": len(employees),
                    "total_invoices": len(invoices),
                    "total_tickets": len(tickets),
                    "total_inventory_items": len(inventory),
                    "total_departments": len(departments),
                    "total_customers": len(customers),
                    "total_deals": len(deals),
                    "total_expenses": len(expenses)
                },
                "operational_metrics": {
                    "total_employees": len(employees),
                    "open_support_tickets": len([t for t in tickets if t.get("status") != "RESOLVED"]),
                    "critical_tickets": len([t for t in tickets if t.get("priority") == "CRITICAL"]),
                    "low_stock_skus": len([i for i in inventory if int(i.get("stock_on_hand", 0)) <= int(i.get("reorder_threshold", 0))]),
                    "departments_count": len(departments),
                    "invoices_in_ledger": len(invoices)
                },
                "entity_found": True,
                "search_status": "FOUND"
            }

    @classmethod
    def get_domain_summary(cls, domain: str) -> str:
        """Returns a concise human-readable summary badge string for the given domain."""
        if domain in ("auto", "", "all"):
            return "Multi-Domain Active Ledger | 10 Enterprise Domains"
        ctx = cls.retrieve(domain)
        dom = ctx.get("domain_key", domain)
        if dom == "hr_leave":
            return f"{ctx.get('total_employees', 0)} Employees | {len(ctx.get('pending_leave_requests', []))} Pending Leaves"
        elif dom == "invoice":
            return f"{ctx.get('total_invoices_in_ledger', 0)} Invoices | ${ctx.get('total_invoices_amount', 0):,.0f} Ledger"
        elif dom == "ticket":
            return f"{len(ctx.get('open_tickets', []))} Open Tickets | {len(ctx.get('critical_tickets', []))} Critical P1"
        elif dom == "inventory":
            return f"{ctx.get('total_catalog_items', 0)} SKUs | {ctx.get('low_stock_count', 0)} Low Stock"
        elif dom == "expense":
            return f"{ctx.get('total_expenses', 0)} Expenses | {len(ctx.get('flagged_over_threshold', []))} Flagged >$1,000"
        elif dom == "budget":
            return f"${ctx.get('total_allocated_budget', 0):,.0f} Q3 Budget | {ctx.get('variance_status', 'Balanced')}"
        elif dom == "crm":
            return f"{ctx.get('total_customers', 0)} Accounts | {ctx.get('total_deals', 0)} Deals"
        elif dom == "policy":
            return "4 Governance Handbooks & Policies | ISO 27001 Standards"
        return "Cross-Department Operations Ledger"
