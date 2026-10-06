import json
from typing import Optional, Dict, Any, List
from worker.tools.base import BaseTool, ToolResult
from mock_erp.database import (
    get_company_profile,
    get_all_departments,
    get_department,
    get_all_employees,
    get_employee,
    update_employee,
    get_all_leave_requests,
    update_leave_request_status,
    get_all_invoices,
    get_invoice_by_number,
    create_invoice,
    get_all_expenses,
    update_expense_status,
    get_all_customers,
    get_customer,
    get_all_deals,
    get_all_tickets,
    get_ticket,
    update_ticket,
    get_all_inventory,
    get_low_stock_inventory,
    create_purchase_order,
    get_all_purchase_orders,
    search_knowledge_base
)

class EnterpriseDatabaseTool(BaseTool):
    name = "enterprise_db"
    description = (
        "Queries and modifies records in the enterprise operational database across "
        "Employees, Tickets, Inventory, Invoices, Expenses, Budgets, Deals, and Customers."
    )

    async def execute(self, action: str, **kwargs) -> ToolResult:
        try:
            # 1. EMPLOYEES & HR
            if action == "get_employee":
                query = kwargs.get("name") or kwargs.get("emp_code") or kwargs.get("identifier", "")
                emp = get_employee(str(query))
                if not emp:
                    return ToolResult(success=False, output=f"No employee found matching '{query}'.", error="NOT_FOUND")
                return ToolResult(
                    success=True,
                    output=f"Employee Record: {emp['name']} | Code: {emp['emp_code']} | Title: {emp['title']} | Dept: {emp['department']} | Salary: ${emp['salary']:,.0f} | PTO Balance: {emp['leave_balance']} days",
                    data=emp
                )

            elif action == "update_employee":
                identifier = kwargs.get("identifier") or kwargs.get("name") or kwargs.get("emp_code", "")
                updates = {k: v for k, v in kwargs.items() if k not in ("identifier", "name", "emp_code")}
                updated = update_employee(str(identifier), **updates)
                if not updated:
                    return ToolResult(success=False, output=f"Failed to update employee '{identifier}'.", error="NOT_FOUND")
                return ToolResult(
                    success=True,
                    output=f"Successfully updated employee {updated['name']}: {updates}",
                    data=updated
                )

            elif action == "list_leave_requests":
                status = kwargs.get("status")
                reqs = get_all_leave_requests(status=status)
                return ToolResult(
                    success=True,
                    output=f"Found {len(reqs)} leave requests" + (f" with status '{status}'" if status else "") + f":\n" +
                           "\n".join([f"- {r['req_code']}: {r['emp_name']} ({r['days_requested']} days, {r['start_date']} to {r['end_date']}) - {r['status']}" for r in reqs[:5]]),
                    data={"leave_requests": reqs, "count": len(reqs)}
                )

            elif action == "approve_leave_request":
                identifier = kwargs.get("identifier") or kwargs.get("emp_name") or kwargs.get("req_code", "")
                notes = kwargs.get("notes", "Approved by Autonomous AI Task Worker")
                updated = update_leave_request_status(str(identifier), new_status="APPROVED", approver_notes=notes)
                if not updated:
                    return ToolResult(success=False, output=f"Leave request '{identifier}' not found.", error="NOT_FOUND")
                return ToolResult(
                    success=True,
                    output=f"Successfully approved leave request {updated['req_code']} for {updated['emp_name']} ({updated['days_requested']} days). Remaining leave balance deducted.",
                    data=updated
                )

            # 2. SUPPORT TICKETS
            elif action == "list_tickets":
                priority = kwargs.get("priority")
                status = kwargs.get("status")
                tickets = get_all_tickets(status=status, priority=priority)
                summary_lines = [f"- {t['ticket_number']} [{t['priority']}] {t['subject']} (Status: {t['status']}, Assignee: {t['assignee']})" for t in tickets]
                return ToolResult(
                    success=True,
                    output=f"Retrieved {len(tickets)} tickets:\n" + "\n".join(summary_lines[:8]),
                    data={"tickets": tickets, "count": len(tickets)}
                )

            elif action == "get_ticket":
                query = kwargs.get("ticket_number") or kwargs.get("identifier", "")
                ticket = get_ticket(str(query))
                if not ticket:
                    return ToolResult(success=False, output=f"Ticket '{query}' not found.", error="NOT_FOUND")
                return ToolResult(
                    success=True,
                    output=f"Ticket {ticket['ticket_number']} [{ticket['priority']}] '{ticket['subject']}' | Client: {ticket['customer_name']} | Status: {ticket['status']} | Assignee: {ticket['assignee']}",
                    data=ticket
                )

            elif action == "update_ticket":
                tck_no = kwargs.get("ticket_number") or kwargs.get("identifier", "")
                new_status = kwargs.get("status")
                assignee = kwargs.get("assignee")
                res_notes = kwargs.get("resolution_notes")
                updated = update_ticket(str(tck_no), status=new_status, assignee=assignee, resolution_notes=res_notes)
                if not updated:
                    return ToolResult(success=False, output=f"Failed to update ticket '{tck_no}'.", error="NOT_FOUND")
                return ToolResult(
                    success=True,
                    output=f"Successfully updated ticket {updated['ticket_number']}: Status='{updated['status']}', Assignee='{updated['assignee']}'",
                    data=updated
                )

            # 3. INVENTORY & SUPPLY CHAIN
            elif action == "check_low_stock":
                low = get_low_stock_inventory()
                if not low:
                    return ToolResult(success=True, output="All inventory items are currently above reorder thresholds.", data={"low_stock": []})
                lines = [f"- {item['sku']}: {item['item_name']} (In Stock: {item['stock_on_hand']}, Threshold: {item['reorder_threshold']}, Target Reorder: {item['target_reorder_qty']}, Supplier: {item['supplier']}, Unit Cost: ${item['unit_cost']:.2f})" for item in low]
                return ToolResult(
                    success=True,
                    output=f"Alert: {len(low)} items are below reorder threshold:\n" + "\n".join(lines),
                    data={"low_stock": low, "count": len(low)}
                )

            elif action == "create_purchase_order":
                supplier = kwargs.get("supplier", "Preferred Supplier")
                items = kwargs.get("items_summary", "Restock supplies")
                total_cost = float(kwargs.get("total_cost", 0.0))
                po = create_purchase_order(supplier=supplier, items_summary=items, total_cost=total_cost)
                return ToolResult(
                    success=True,
                    output=f"Created Purchase Order {po['po_number']} to {po['supplier']} for ${po['total_cost']:,.2f} ({po['items_summary']}). Delivery expected by {po['delivery_expected']}.",
                    data=po
                )

            # 4. INVOICES
            elif action == "create_invoice":
                inv = create_invoice(
                    invoice_number=kwargs.get("invoice_number", ""),
                    vendor_name=kwargs.get("vendor_name", ""),
                    amount=float(kwargs.get("amount", 0)),
                    due_date=kwargs.get("due_date", ""),
                    currency=kwargs.get("currency", "USD"),
                    notes=kwargs.get("notes", "Entered by Autonomous AI Worker"),
                    invoice_type=kwargs.get("invoice_type", "PAYABLE")
                )
                return ToolResult(
                    success=True,
                    output=f"Successfully registered invoice {inv['invoice_number']} for {inv['vendor_name']} (${inv['amount']:,.2f} {inv['currency']}) in general ledger.",
                    data=inv
                )

            elif action == "get_invoice":
                inv_no = kwargs.get("invoice_number", "")
                inv = get_invoice_by_number(inv_no)
                if not inv:
                    return ToolResult(success=False, output=f"Invoice '{inv_no}' not found in ledger.", error="NOT_FOUND")
                return ToolResult(
                    success=True,
                    output=f"Invoice {inv['invoice_number']} | Vendor: {inv['vendor_name']} | Amount: ${inv['amount']:,.2f} | Due: {inv['due_date']} | Status: {inv['status']}",
                    data=inv
                )

            # 5. EXPENSES
            elif action == "list_expenses":
                status = kwargs.get("status")
                exps = get_all_expenses(status=status)
                lines = [f"- {e['report_number']}: {e['employee_name']} ({e['category']}) ${e['amount']:,.2f} at {e['merchant']} - {e['status']}" for e in exps]
                return ToolResult(
                    success=True,
                    output=f"Retrieved {len(exps)} expense claims:\n" + "\n".join(lines),
                    data={"expenses": exps, "count": len(exps)}
                )

            elif action == "approve_expense":
                rep_no = kwargs.get("report_number", "")
                notes = kwargs.get("notes", "Approved by Autonomous AI Task Worker")
                updated = update_expense_status(rep_no, new_status="APPROVED", notes=notes)
                if not updated:
                    return ToolResult(success=False, output=f"Expense report '{rep_no}' not found.", error="NOT_FOUND")
                return ToolResult(
                    success=True,
                    output=f"Successfully approved expense report {updated['report_number']} for {updated['employee_name']} (${updated['amount']:,.2f}).",
                    data=updated
                )

            # 6. BUDGETS & DEPARTMENTS
            elif action == "get_department_budget":
                dept_name = kwargs.get("department", "")
                dept = get_department(dept_name)
                if not dept:
                    return ToolResult(success=False, output=f"Department '{dept_name}' not found.", error="NOT_FOUND")
                rem = dept["budget_q3"] - dept["spent_q3"]
                pct = (dept["spent_q3"] / dept["budget_q3"]) * 100
                return ToolResult(
                    success=True,
                    output=f"Department: {dept['name']} (Head: {dept['head_of_dept']})\n- Q3 Budget: ${dept['budget_q3']:,.2f}\n- Q3 Spent: ${dept['spent_q3']:,.2f} ({pct:.1f}% utilized)\n- Remaining Budget: ${rem:,.2f}",
                    data=dept
                )

            # 7. COMPANY PROFILE
            elif action == "get_company_profile":
                prof = get_company_profile()
                return ToolResult(
                    success=True,
                    output=f"Company Profile: {prof.get('legal_name')} | Tax ID: {prof.get('tax_id')} | HQ: {prof.get('hq_address')} | Bank: {prof.get('bank_name')} ({prof.get('bank_routing')})",
                    data=prof
                )

            else:
                return ToolResult(
                    success=False,
                    output=f"Unknown enterprise database action: '{action}'",
                    error="UNKNOWN_ACTION"
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Database execution failed: {str(e)}",
                error=str(e)
            )
