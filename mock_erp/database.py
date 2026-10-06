import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "erp.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'accountant'
        )
    """)

    # Invoices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            vendor_name TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            due_date TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING_APPROVAL',
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Audit log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    # Seed admin user if not exists
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "company_secure_pass", "finance_admin")
        )

    # Seed sample baseline invoices if table empty
    cursor.execute("SELECT COUNT(*) FROM invoices")
    if cursor.fetchone()[0] == 0:
        sample_invoices = [
            ("INV-2026-001", "Acme Supplies Co", 1450.50, "USD", "2026-10-15", "APPROVED", "Monthly office consumables", "2026-09-15 10:30:00"),
            ("INV-2026-002", "Global Cloud Hosting", 820.00, "USD", "2026-10-20", "PAID", "Dedicated server renewal", "2026-09-20 14:15:00"),
            ("INV-2026-003", "Apex Logistics Ltd", 3120.00, "USD", "2026-11-01", "PENDING_APPROVAL", "Q3 Freight charges", "2026-09-28 09:00:00"),
        ]
        cursor.executemany(
            """INSERT INTO invoices (invoice_number, vendor_name, amount, currency, due_date, status, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            sample_invoices
        )

    conn.commit()
    conn.close()

def log_audit(action: str, details: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (action, details, timestamp) VALUES (?, ?, ?)",
        (action, details, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_all_invoices() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices ORDER BY id DESC")
    rows = cursor.fetchall()
    invoices = [dict(row) for row in rows]
    conn.close()
    return invoices

def get_invoice_by_number(invoice_number: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_invoice(invoice_number: str, vendor_name: str, amount: float, due_date: str, currency: str = "USD", notes: str = "") -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """INSERT INTO invoices (invoice_number, vendor_name, amount, currency, due_date, status, notes, created_at)
           VALUES (?, ?, ?, ?, ?, 'ENTERED', ?, ?)""",
        (invoice_number, vendor_name, amount, currency, due_date, notes, created_at)
    )
    invoice_id = cursor.lastrowid
    conn.commit()
    conn.close()
    log_audit("INVOICE_CREATED", f"Created invoice {invoice_number} for {vendor_name} amount: {amount} {currency}")
    return {
        "id": invoice_id,
        "invoice_number": invoice_number,
        "vendor_name": vendor_name,
        "amount": amount,
        "currency": currency,
        "due_date": due_date,
        "status": "ENTERED",
        "notes": notes,
        "created_at": created_at
    }

def verify_invoice_record(vendor_name: str, amount: float, due_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    # Fuzzy/case-insensitive match for vendor name and close match for amount
    cursor.execute(
        """SELECT * FROM invoices 
           WHERE LOWER(vendor_name) LIKE ? AND ABS(amount - ?) < 0.01
           ORDER BY id DESC LIMIT 1""",
        (f"%{vendor_name.lower().strip()}%", amount)
    )
    row = cursor.fetchone()
    conn.close()
def reset_test_records():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoices WHERE invoice_number LIKE 'INV-CX-%' OR vendor_name LIKE '%Company X%'")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Mock ERP Database initialized successfully.")
