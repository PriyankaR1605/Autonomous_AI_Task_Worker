import os
from typing import Optional
from fastapi import FastAPI, Request, Form, Response, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from mock_erp.database import (
    init_db,
    get_all_invoices,
    get_invoice_by_number,
    create_invoice,
    verify_invoice_record,
    log_audit
)

app = FastAPI(title="CentrAlign Mock Enterprise ERP", version="1.0.0")

# Setup template directory
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Static files if needed
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mock Auth Helper
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
        log_audit("USER_LOGIN", f"User {username} successfully logged in.")
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
async def dashboard_page(request: Request, message: Optional[str] = None):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    invoices = get_all_invoices()
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": "admin", "invoices": invoices, "message": message}
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
    
    # Check if duplicate invoice number
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
    return RedirectResponse(url=f"/dashboard?message={success_msg}", status_code=status.HTTP_302_FOUND)

# --- REST API Endpoints for Direct Tool Usage & Verification ---

class InvoiceCreatePayload(BaseModel):
    vendor_name: str
    invoice_number: str
    amount: float
    due_date: str
    currency: str = "USD"
    notes: Optional[str] = ""

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "service": "CentrAlign Mock ERP"}

@app.get("/api/invoices")
async def api_get_invoices():
    return {"invoices": get_all_invoices()}

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
        notes=payload.notes or ""
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mock_erp.app:app", host="127.0.0.1", port=8000, reload=True)
