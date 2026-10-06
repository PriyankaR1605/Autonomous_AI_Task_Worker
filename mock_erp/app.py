import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, Form, Response, status, Query, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from mock_erp.database import (
    init_db,
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
    verify_invoice_record,
    get_all_expenses,
    update_expense_status,
    get_all_customers,
    get_customer,
    get_all_deals,
    create_deal,
    get_all_tickets,
    get_ticket,
    update_ticket,
    get_all_inventory,
    get_low_stock_inventory,
    create_purchase_order,
    get_all_purchase_orders,
    search_knowledge_base,
    get_audit_logs,
    log_audit
)

app = FastAPI(title="CentrAlign Enterprise Operations Portal & ERP", version="2.0.0")

# Setup template directory
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def is_authenticated(request: Request) -> bool:
    session_user = request.cookies.get("session_user")
    return bool(session_user)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=RedirectResponse)
async def root(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="login.html", context={"error": error})

@app.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if username.strip() == "admin" and password.strip() == "company_secure_pass":
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="session_user", value="admin", httponly=True)
        log_audit("USER_LOGIN", f"User {username} successfully logged into enterprise portal.")
        return response
    
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": "Invalid username or password. Please use admin / company_secure_pass"}
    )

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("session_user")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request, 
    tab: str = "overview", 
    message: Optional[str] = None
):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    profile = get_company_profile()
    departments = get_all_departments()
    employees = get_all_employees()
    leave_requests = get_all_leave_requests()
    invoices = get_all_invoices()
    expenses = get_all_expenses()
    customers = get_all_customers()
    deals = get_all_deals()
    tickets = get_all_tickets()
    inventory = get_all_inventory()
    low_stock = get_low_stock_inventory()
    purchase_orders = get_all_purchase_orders()
    audit_logs = get_audit_logs(limit=15)

    # Compute key performance metrics
    total_budget_q3 = sum(d["budget_q3"] for d in departments)
    total_spent_q3 = sum(d["spent_q3"] for d in departments)
    critical_tickets_count = sum(1 for t in tickets if t["priority"] == "CRITICAL" and t["status"] != "RESOLVED")
    pending_leaves_count = sum(1 for l in leave_requests if l["status"] == "PENDING")

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": "admin",
            "active_tab": tab,
            "message": message,
            "profile": profile,
            "departments": departments,
            "employees": employees,
            "leave_requests": leave_requests,
            "invoices": invoices,
            "expenses": expenses,
            "customers": customers,
            "deals": deals,
            "tickets": tickets,
            "inventory": inventory,
            "low_stock": low_stock,
            "purchase_orders": purchase_orders,
            "audit_logs": audit_logs,
            "total_budget_q3": total_budget_q3,
            "total_spent_q3": total_spent_q3,
            "critical_tickets_count": critical_tickets_count,
            "pending_leaves_count": pending_leaves_count
        }
    )

@app.get("/invoices/new", response_class=HTMLResponse)
async def new_invoice_page(request: Request, error: Optional[str] = None):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="new_invoice.html", context={"error": error})

@app.post("/invoices/new")
async def new_invoice_submit(
    request: Request,
    vendor_name: str = Form(...),
    invoice_number: str = Form(...),
    amount: float = Form(...),
    due_date: str = Form(...),
    currency: str = Form("USD"),
    notes: Optional[str] = Form("")
):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    existing = get_invoice_by_number(invoice_number.strip())
    if existing:
        return templates.TemplateResponse(
            request=request,
            name="new_invoice.html",
            context={"error": f"Invoice number '{invoice_number}' already exists in ledger!"}
        )
    
    created = create_invoice(
        invoice_number=invoice_number.strip(),
        vendor_name=vendor_name.strip(),
        amount=amount,
        due_date=due_date.strip(),
        currency=currency.strip(),
        notes=(notes or "").strip()
    )
    
    success_msg = f"Successfully registered invoice {created['invoice_number']} for {created['vendor_name']} (${created['amount']:.2f})!"
    return RedirectResponse(url=f"/dashboard?tab=invoices&message={success_msg}", status_code=status.HTTP_302_FOUND)

# -------------------------------------------------------------
# REST API ENDPOINTS FOR AI WORKER TOOLS & PROGRAMMATIC ACCESS
# -------------------------------------------------------------

@app.get("/api/health")
async def api_health():
    return {
        "status": "ok", 
        "service": "CentrAlign Enterprise Operations Platform", 
        "version": "2.0.0",
        "company": "CentrAlign Technologies Inc."
    }

@app.get("/api/company/profile")
async def api_get_company_profile():
    return {"profile": get_company_profile()}

@app.get("/api/departments")
async def api_get_departments():
    return {"departments": get_all_departments()}

@app.get("/api/employees")
async def api_get_employees(
    query: Optional[str] = Query(None, description="Name or code search query")
):
    if query:
        emp = get_employee(query)
        return {"employees": [emp] if emp else []}
    return {"employees": get_all_employees()}

@app.get("/api/employees/{identifier}")
async def api_get_employee_single(identifier: str):
    emp = get_employee(identifier)
    if not emp:
        return JSONResponse(status_code=404, content={"error": f"Employee '{identifier}' not found."})
    return {"employee": emp}

class EmployeeUpdatePayload(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = None
    status: Optional[str] = None
    leave_balance: Optional[int] = None
    manager_name: Optional[str] = None
    performance_rating: Optional[float] = None

@app.patch("/api/employees/{identifier}")
async def api_update_employee(identifier: str, payload: EmployeeUpdatePayload):
    updates = payload.dict(exclude_unset=True)
    updated = update_employee(identifier, **updates)
    if not updated:
        return JSONResponse(status_code=404, content={"error": f"Employee '{identifier}' not found."})
    return {"success": True, "employee": updated}

@app.get("/api/leave-requests")
async def api_get_leave_requests(status_filter: Optional[str] = Query(None, alias="status")):
    return {"leave_requests": get_all_leave_requests(status=status_filter)}

class LeaveActionPayload(BaseModel):
    status: str  # APPROVED or REJECTED
    notes: Optional[str] = "Processed by CentrAlign Autonomous Worker"

@app.post("/api/leave-requests/{identifier}/action")
async def api_leave_action(identifier: str, payload: LeaveActionPayload):
    updated = update_leave_request_status(identifier, new_status=payload.status, approver_notes=payload.notes or "")
    if not updated:
        return JSONResponse(status_code=404, content={"error": f"Leave request '{identifier}' not found."})
    return {"success": True, "leave_request": updated}

@app.get("/api/invoices")
async def api_get_invoices():
    return {"invoices": get_all_invoices()}

class InvoiceCreatePayload(BaseModel):
    vendor_name: str
    invoice_number: str
    amount: float
    due_date: str
    currency: str = "USD"
    notes: Optional[str] = ""
    invoice_type: Optional[str] = "PAYABLE"

@app.post("/api/invoices")
async def api_create_invoice(payload: InvoiceCreatePayload):
    existing = get_invoice_by_number(payload.invoice_number.strip())
    if existing:
        if abs(existing["amount"] - payload.amount) < 0.01:
            return {"success": True, "invoice": existing, "message": "Invoice already registered in ledger."}
        return JSONResponse(
            status_code=400,
            content={"error": f"Invoice '{payload.invoice_number}' already exists with differing details."}
        )
    created = create_invoice(
        invoice_number=payload.invoice_number.strip(),
        vendor_name=payload.vendor_name.strip(),
        amount=payload.amount,
        due_date=payload.due_date.strip(),
        currency=payload.currency.strip(),
        notes=payload.notes or "",
        invoice_type=payload.invoice_type or "PAYABLE"
    )
    return {"success": True, "invoice": created}

@app.get("/api/invoices/verify")
async def api_verify_invoice(
    vendor: str = Query(..., description="Vendor name to verify"),
    amount: float = Query(..., description="Invoice amount to verify")
):
    match = verify_invoice_record(vendor, amount)
    if match:
        return {
            "verified": True,
            "match": match,
            "message": f"Verified: Found matching record #{match['invoice_number']} for {match['vendor_name']} with amount ${match['amount']:.2f}"
        }
    return {
        "verified": False,
        "match": None,
        "message": f"Verification failed: No invoice found matching vendor '{vendor}' and amount ${amount:.2f}"
    }

@app.get("/api/expenses")
async def api_get_expenses(status_filter: Optional[str] = Query(None, alias="status")):
    return {"expenses": get_all_expenses(status=status_filter)}

class ExpenseActionPayload(BaseModel):
    status: str
    notes: Optional[str] = "Approved by Autonomous AI Worker"

@app.post("/api/expenses/{report_number}/action")
async def api_expense_action(report_number: str, payload: ExpenseActionPayload):
    updated = update_expense_status(report_number, new_status=payload.status, notes=payload.notes or "")
    if not updated:
        return JSONResponse(status_code=404, content={"error": f"Expense report '{report_number}' not found."})
    return {"success": True, "expense": updated}

@app.get("/api/customers")
async def api_get_customers(name: Optional[str] = Query(None)):
    if name:
        cust = get_customer(name)
        return {"customers": [cust] if cust else []}
    return {"customers": get_all_customers()}

@app.get("/api/deals")
async def api_get_deals():
    return {"deals": get_all_deals()}

class DealCreatePayload(BaseModel):
    deal_name: str
    customer_name: str
    stage: str = "Qualification"
    deal_value: float
    close_date: str
    probability_pct: int = 50

@app.post("/api/deals")
async def api_create_deal(payload: DealCreatePayload):
    created = create_deal(
        deal_name=payload.deal_name,
        customer_name=payload.customer_name,
        stage=payload.stage,
        deal_value=payload.deal_value,
        close_date=payload.close_date,
        probability_pct=payload.probability_pct
    )
    return {"success": True, "deal": created}

@app.get("/api/tickets")
async def api_get_tickets(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority")
):
    tickets = get_all_tickets(status=status_filter, priority=priority_filter)
    return {"tickets": tickets, "count": len(tickets)}

@app.get("/api/tickets/{identifier}")
async def api_get_ticket_single(identifier: str):
    ticket = get_ticket(identifier)
    if not ticket:
        return JSONResponse(status_code=404, content={"error": f"Ticket '{identifier}' not found."})
    return {"ticket": ticket}

class TicketUpdatePayload(BaseModel):
    status: Optional[str] = None
    assignee: Optional[str] = None
    resolution_notes: Optional[str] = None

@app.patch("/api/tickets/{ticket_number}")
async def api_update_ticket(ticket_number: str, payload: TicketUpdatePayload):
    updated = update_ticket(
        ticket_number=ticket_number,
        status=payload.status,
        assignee=payload.assignee,
        resolution_notes=payload.resolution_notes
    )
    if not updated:
        return JSONResponse(status_code=404, content={"error": f"Ticket '{ticket_number}' not found."})
    return {"success": True, "ticket": updated}

@app.get("/api/inventory")
async def api_get_inventory(low_stock_only: bool = False):
    if low_stock_only:
        items = get_low_stock_inventory()
    else:
        items = get_all_inventory()
    return {"inventory": items, "count": len(items)}

class PurchaseOrderCreatePayload(BaseModel):
    supplier: str
    items_summary: str
    total_cost: float
    delivery_expected: Optional[str] = ""

@app.post("/api/purchase-orders")
async def api_create_po(payload: PurchaseOrderCreatePayload):
    created = create_purchase_order(
        supplier=payload.supplier,
        items_summary=payload.items_summary,
        total_cost=payload.total_cost,
        delivery_expected=payload.delivery_expected or ""
    )
    return {"success": True, "purchase_order": created}

@app.get("/api/purchase-orders")
async def api_get_pos():
    return {"purchase_orders": get_all_purchase_orders()}

@app.get("/api/knowledge-base")
async def api_search_kb(q: str = Query(..., description="Keyword search query")):
    results = search_knowledge_base(q)
    return {"results": results, "count": len(results)}

@app.get("/api/audit-logs")
async def api_get_logs(limit: int = 25):
    return {"logs": get_audit_logs(limit=limit)}

# --- Universal Outcome Verification Endpoint ---
class VerificationPayload(BaseModel):
    entity_type: str  # invoice, ticket, leave_request, employee, purchase_order, expense
    criteria: Dict[str, Any]

@app.post("/api/verify")
async def api_universal_verify(payload: VerificationPayload):
    entity_type = payload.entity_type.lower()
    c = payload.criteria

    if entity_type == "invoice":
        vendor = c.get("vendor_name", "")
        amount = float(c.get("amount", 0))
        match = verify_invoice_record(vendor, amount)
        return {
            "verified": bool(match),
            "entity_type": entity_type,
            "record": match,
            "message": f"Verified invoice #{match['invoice_number']} for {match['vendor_name']} (${match['amount']:.2f})" if match else "Invoice verification failed: Record not found."
        }

    elif entity_type in ("ticket", "support_ticket"):
        t_id = c.get("ticket_number") or c.get("subject") or ""
        ticket = get_ticket(str(t_id))
        if not ticket:
            return {"verified": False, "message": f"Ticket '{t_id}' not found."}
        
        matches = True
        discrepancies = []
        if "status" in c and ticket["status"] != c["status"].upper():
            matches = False
            discrepancies.append(f"Expected status {c['status']}, found {ticket['status']}")
        if "assignee" in c and c["assignee"].lower() not in (ticket["assignee"] or "").lower():
            matches = False
            discrepancies.append(f"Expected assignee {c['assignee']}, found {ticket['assignee']}")
        return {
            "verified": matches,
            "record": ticket,
            "message": f"Ticket verified: {ticket['ticket_number']} is {ticket['status']} assigned to {ticket['assignee']}" if matches else f"Verification discrepancies: {'; '.join(discrepancies)}"
        }

    elif entity_type in ("leave_request", "leave"):
        emp_name = c.get("emp_name", "")
        reqs = get_all_leave_requests()
        matched_req = None
        for r in reqs:
            if emp_name.lower() in r["emp_name"].lower():
                matched_req = r
                break
        if not matched_req:
            return {"verified": False, "message": f"No leave request found for {emp_name}"}
        
        expected_status = c.get("status", "APPROVED").upper()
        is_verified = (matched_req["status"] == expected_status)
        return {
            "verified": is_verified,
            "record": matched_req,
            "message": f"Leave request {matched_req['req_code']} status confirmed as {matched_req['status']}" if is_verified else f"Expected status {expected_status}, but was {matched_req['status']}"
        }

    elif entity_type == "employee":
        emp_id = c.get("emp_code") or c.get("name") or ""
        emp = get_employee(str(emp_id))
        if not emp:
            return {"verified": False, "message": f"Employee '{emp_id}' not found."}
        
        matches = True
        discrepancies = []
        if "title" in c and c["title"].lower() != emp["title"].lower():
            matches = False
            discrepancies.append(f"Expected title '{c['title']}', found '{emp['title']}'")
        if "salary" in c and abs(float(c["salary"]) - float(emp["salary"])) > 1.0:
            matches = False
            discrepancies.append(f"Expected salary ${float(c['salary']):,.2f}, found ${float(emp['salary']):,.2f}")
        return {
            "verified": matches,
            "record": emp,
            "message": f"Employee profile verified for {emp['name']} ({emp['title']})" if matches else f"Discrepancies: {'; '.join(discrepancies)}"
        }

    elif entity_type in ("purchase_order", "po"):
        supplier = c.get("supplier", "")
        pos = get_all_purchase_orders()
        found = None
        for po in pos:
            if supplier.lower() in po["supplier"].lower():
                found = po
                break
        return {
            "verified": bool(found),
            "record": found,
            "message": f"Purchase order confirmed: {found['po_number']} to {found['supplier']} for ${found['total_cost']:,.2f}" if found else f"No PO found for supplier {supplier}"
        }

    return {"verified": False, "message": f"Unsupported verification entity type: {entity_type}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mock_erp.app:app", host="127.0.0.1", port=8000, reload=True)
