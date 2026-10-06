import sqlite3
import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "erp.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users table (Admin & Portal authentication)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'accountant',
            email TEXT
        )
    """)

    # 2. Company Profile
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            legal_name TEXT NOT NULL,
            brand_name TEXT NOT NULL,
            tax_id TEXT NOT NULL,
            hq_address TEXT NOT NULL,
            phone TEXT NOT NULL,
            website TEXT NOT NULL,
            bank_name TEXT NOT NULL,
            bank_routing TEXT NOT NULL,
            founded_year INTEGER NOT NULL,
            total_employees INTEGER DEFAULT 250
        )
    """)

    # 3. Departments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            head_of_dept TEXT NOT NULL,
            budget_q3 REAL NOT NULL,
            spent_q3 REAL NOT NULL,
            headcount INTEGER NOT NULL
        )
    """)

    # 4. Employees & HR Directory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            title TEXT NOT NULL,
            manager_name TEXT NOT NULL,
            hire_date TEXT NOT NULL,
            salary REAL NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            leave_balance INTEGER DEFAULT 20,
            phone TEXT,
            emergency_contact TEXT,
            performance_rating REAL DEFAULT 4.5
        )
    """)

    # 5. Leave Requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            req_code TEXT UNIQUE NOT NULL,
            emp_name TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            days_requested INTEGER NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'PENDING',
            approver_notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # 6. Invoices (Accounts Payable & Receivable)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            vendor_name TEXT NOT NULL,
            invoice_type TEXT DEFAULT 'PAYABLE',
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            due_date TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING_APPROVAL',
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Check and add invoice_type column migration if invoices table predates it
    cursor.execute("PRAGMA table_info(invoices)")
    inv_cols = [c[1] for c in cursor.fetchall()]
    if "invoice_type" not in inv_cols:
        try:
            cursor.execute("ALTER TABLE invoices ADD COLUMN invoice_type TEXT DEFAULT 'PAYABLE'")
        except Exception:
            pass

    # 7. Employee Expense Reports
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_number TEXT UNIQUE NOT NULL,
            employee_name TEXT NOT NULL,
            department TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            merchant TEXT NOT NULL,
            expense_date TEXT NOT NULL,
            status TEXT DEFAULT 'SUBMITTED',
            notes TEXT,
            receipt_ref TEXT
        )
    """)

    # 8. Customers & Accounts (CRM)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_code TEXT UNIQUE NOT NULL,
            company_name TEXT NOT NULL,
            industry TEXT NOT NULL,
            contract_tier TEXT NOT NULL,
            annual_contract_value REAL NOT NULL,
            account_executive TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            health_score INTEGER DEFAULT 95,
            primary_contact TEXT
        )
    """)

    # 9. Deals & Sales Pipeline
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_name TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            stage TEXT NOT NULL,
            deal_value REAL NOT NULL,
            close_date TEXT NOT NULL,
            probability_pct INTEGER NOT NULL
        )
    """)

    # 10. Support & Incident Tickets (ITSM / Helpdesk)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            requester_email TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'OPEN',
            assignee TEXT,
            resolution_notes TEXT,
            created_at TEXT NOT NULL,
            sla_due TEXT NOT NULL
        )
    """)

    # 11. Inventory & Hardware Assets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            stock_on_hand INTEGER NOT NULL,
            reorder_threshold INTEGER NOT NULL,
            target_reorder_qty INTEGER NOT NULL,
            unit_cost REAL NOT NULL,
            supplier TEXT NOT NULL,
            warehouse_location TEXT NOT NULL
        )
    """)

    # 12. Purchase Orders
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT UNIQUE NOT NULL,
            supplier TEXT NOT NULL,
            items_summary TEXT NOT NULL,
            total_cost REAL NOT NULL,
            status TEXT DEFAULT 'ISSUED',
            created_at TEXT NOT NULL,
            delivery_expected TEXT NOT NULL
        )
    """)

    # 13. Knowledge Base & Policies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            summary TEXT NOT NULL,
            file_path TEXT NOT NULL,
            tags TEXT
        )
    """)

    # 14. Audit Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    # -------------------------------------------------------------
    # SEED DATA INITIALIZATION
    # -------------------------------------------------------------

    # Users
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
            ("admin", "company_secure_pass", "finance_admin", "admin@centralign.internal")
        )

    # Company Profile
    cursor.execute("SELECT COUNT(*) FROM company_profile")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO company_profile (legal_name, brand_name, tax_id, hq_address, phone, website, bank_name, bank_routing, founded_year, total_employees)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "CentrAlign Technologies Inc.",
            "CentrAlign AI",
            "US-EIN-94-3829104",
            "500 Howard Street, Suite 400, San Francisco, CA 94105",
            "+1 (415) 555-0199",
            "https://www.centralign.internal",
            "Silicon Valley Commercial Bank",
            "SVB-021000089",
            2021,
            245
        ))

    # Departments
    cursor.execute("SELECT COUNT(*) FROM departments")
    if cursor.fetchone()[0] == 0:
        sample_depts = [
            ("Engineering", "Marcus Vance", 450000.0, 395400.0, 95),
            ("Sales & Revenue", "Jessica Alba-Ruiz", 320000.0, 280100.0, 48),
            ("Marketing & Growth", "David Sterling", 180000.0, 162500.0, 22),
            ("Customer Success", "Amina Patel", 140000.0, 118000.0, 35),
            ("Human Resources", "Elena Vance", 90000.0, 72000.0, 12),
            ("Finance & Legal", "Marcus Thorne", 110000.0, 89500.0, 15),
            ("IT & Security", "Alex Wong", 160000.0, 142000.0, 18),
        ]
        cursor.executemany("""
            INSERT INTO departments (name, head_of_dept, budget_q3, spent_q3, headcount)
            VALUES (?, ?, ?, ?, ?)
        """, sample_depts)

    # Employees
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        sample_employees = [
            ("EMP-101", "Sarah Jenkins", "sarah.jenkins@centralign.internal", "Engineering", "Senior Software Engineer", "Marcus Vance", "2022-03-15", 148000.0, "ACTIVE", 16, "+1-415-555-0111", "Robert Jenkins (Spouse)", 4.8),
            ("EMP-102", "Alex Wong", "alex.wong@centralign.internal", "IT & Security", "Lead Systems Architect", "Marcus Vance", "2021-08-01", 162000.0, "ACTIVE", 14, "+1-415-555-0112", "Mei Wong (Mother)", 4.9),
            ("EMP-103", "David Miller", "david.miller@centralign.internal", "Engineering", "Staff Infrastructure Engineer", "Marcus Vance", "2022-11-10", 155000.0, "ACTIVE", 18, "+1-415-555-0113", "Clara Miller (Sister)", 4.7),
            ("EMP-104", "Elena Vance", "elena.vance@centralign.internal", "Human Resources", "VP of People & Culture", "CEO", "2021-02-01", 175000.0, "ACTIVE", 12, "+1-415-555-0114", "Marcus Vance (Brother)", 5.0),
            ("EMP-105", "Marcus Thorne", "marcus.thorne@centralign.internal", "Finance & Legal", "Chief Financial Officer", "CEO", "2021-01-15", 210000.0, "ACTIVE", 10, "+1-415-555-0115", "Victoria Thorne (Spouse)", 5.0),
            ("EMP-106", "Jessica Alba-Ruiz", "jessica.alba@centralign.internal", "Sales & Revenue", "VP of Worldwide Sales", "CEO", "2021-05-12", 185000.0, "ACTIVE", 15, "+1-415-555-0116", "Carlos Ruiz (Spouse)", 4.8),
            ("EMP-107", "David Sterling", "david.sterling@centralign.internal", "Marketing & Growth", "Director of Product Marketing", "CEO", "2023-01-09", 140000.0, "ACTIVE", 17, "+1-415-555-0117", "Alice Sterling (Spouse)", 4.6),
            ("EMP-108", "Amina Patel", "amina.patel@centralign.internal", "Customer Success", "Director of Customer Success", "CEO", "2022-06-20", 138000.0, "ACTIVE", 19, "+1-415-555-0118", "Tariq Patel (Brother)", 4.7),
            ("EMP-109", "Chloe Martin", "chloe.martin@centralign.internal", "Engineering", "Frontend Developer", "Sarah Jenkins", "2023-04-18", 115000.0, "ACTIVE", 15, "+1-415-555-0119", "Luc Martin (Father)", 4.5),
            ("EMP-110", "Liam O'Connor", "liam.oconnor@centralign.internal", "IT & Security", "Security Operations Analyst", "Alex Wong", "2023-09-01", 105000.0, "ACTIVE", 20, "+1-415-555-0120", "Sean O'Connor (Brother)", 4.6),
            ("EMP-111", "Maya Lin", "maya.lin@centralign.internal", "Sales & Revenue", "Senior Enterprise Account Exec", "Jessica Alba-Ruiz", "2022-09-15", 135000.0, "ACTIVE", 14, "+1-415-555-0121", "Wei Lin (Father)", 4.9),
            ("EMP-112", "Thomas Becker", "thomas.becker@centralign.internal", "Finance & Legal", "Senior Corporate Accountant", "Marcus Thorne", "2022-02-14", 112000.0, "ACTIVE", 13, "+1-415-555-0122", "Greta Becker (Spouse)", 4.7),
        ]
        cursor.executemany("""
            INSERT INTO employees (emp_code, name, email, department, title, manager_name, hire_date, salary, status, leave_balance, phone, emergency_contact, performance_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_employees)

    # Leave Requests
    cursor.execute("SELECT COUNT(*) FROM leave_requests")
    if cursor.fetchone()[0] == 0:
        sample_leaves = [
            ("LV-2026-001", "Sarah Jenkins", "Annual Vacation", "2026-11-20", "2026-11-25", 4, "Family holiday trip to Japan", "PENDING", None, "2026-10-04 09:30:00"),
            ("LV-2026-002", "Chloe Martin", "Sick Leave", "2026-09-12", "2026-09-13", 2, "Mild seasonal flu recovery", "APPROVED", "Approved by Sarah Jenkins", "2026-09-11 18:00:00"),
            ("LV-2026-003", "David Miller", "Annual Vacation", "2026-12-24", "2026-12-31", 5, "Christmas & New Year break with parents", "PENDING", None, "2026-10-02 14:15:00"),
            ("LV-2026-004", "Maya Lin", "Personal Leave", "2026-10-18", "2026-10-19", 2, "Attending sibling graduation ceremony", "APPROVED", "Approved by Jessica Alba-Ruiz", "2026-10-01 11:20:00"),
        ]
        cursor.executemany("""
            INSERT INTO leave_requests (req_code, emp_name, leave_type, start_date, end_date, days_requested, reason, status, approver_notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_leaves)

    # Invoices (AP & AR)
    cursor.execute("SELECT COUNT(*) FROM invoices")
    if cursor.fetchone()[0] == 0:
        sample_invoices = [
            ("INV-2026-001", "Acme Supplies Co", "PAYABLE", 1450.50, "USD", "2026-10-15", "APPROVED", "Monthly office consumables & paper", "2026-09-15 10:30:00"),
            ("INV-2026-002", "Global Cloud Hosting", "PAYABLE", 820.00, "USD", "2026-10-20", "PAID", "Dedicated server cluster renewal", "2026-09-20 14:15:00"),
            ("INV-2026-003", "Apex Logistics Ltd", "PAYABLE", 3120.00, "USD", "2026-11-01", "PENDING_APPROVAL", "Q3 Freight & customs charges", "2026-09-28 09:00:00"),
            ("INV-2026-004", "CloudScale Networks", "PAYABLE", 2400.00, "USD", "2026-10-28", "APPROVED", "Enterprise SD-WAN interconnects", "2026-09-30 11:45:00"),
            ("INV-2026-005", "CyberShield Security LLC", "PAYABLE", 7000.00, "USD", "2026-11-10", "PENDING_APPROVAL", "Monthly SOC 24/7 SIEM monitoring retainer", "2026-10-01 08:30:00"),
            ("INV-2026-006", "OfficeMax Pro", "PAYABLE", 530.25, "USD", "2026-10-25", "PAID", "Breakroom coffee and pantry stocking", "2026-09-22 13:00:00"),
            ("INV-CLI-901", "Nexus Healthcare Systems", "RECEIVABLE", 45000.00, "USD", "2026-11-30", "PENDING_APPROVAL", "CentrAlign AI Engine enterprise subscription Q4", "2026-10-01 09:00:00"),
            ("INV-CLI-902", "Vertex FinTech Corp", "RECEIVABLE", 32500.00, "USD", "2026-10-31", "PAID", "Custom API integration & onboarding package", "2026-09-10 16:30:00"),
        ]
        cursor.executemany("""
            INSERT INTO invoices (invoice_number, vendor_name, invoice_type, amount, currency, due_date, status, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_invoices)

    # Expense Reports
    cursor.execute("SELECT COUNT(*) FROM expense_reports")
    if cursor.fetchone()[0] == 0:
        sample_expenses = [
            ("EXP-2026-101", "Sarah Jenkins", "Engineering", "Hardware", 1250.00, "Dell Enterprise Store", "2026-09-28", "SUBMITTED", "4K UltraSharp curved developer monitor", "receipt_dell_4k.pdf"),
            ("EXP-2026-102", "Maya Lin", "Sales & Revenue", "Travel", 890.00, "United Airlines", "2026-09-24", "APPROVED", "Roundtrip flight to Chicago for Nexus client pitch", "receipt_flight_ord.pdf"),
            ("EXP-2026-103", "David Sterling", "Marketing & Growth", "Software", 350.00, "Canva Enterprise", "2026-09-30", "APPROVED", "Design team collaborative subscription", "receipt_canva.pdf"),
            ("EXP-2026-104", "Alex Wong", "IT & Security", "Hardware", 1850.00, "Cisco Systems", "2026-10-02", "SUBMITTED", "Replacement 24-port PoE Gigabit switch", "receipt_cisco_poe.pdf"),
            ("EXP-2026-105", "Chloe Martin", "Engineering", "Meals & Entertainment", 145.50, "Piazza D'Angelo", "2026-10-03", "SUBMITTED", "Team sprint retrospective lunch celebration", "receipt_lunch.pdf"),
        ]
        cursor.executemany("""
            INSERT INTO expense_reports (report_number, employee_name, department, category, amount, merchant, expense_date, status, notes, receipt_ref)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_expenses)

    # Customers (CRM)
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        sample_customers = [
            ("CUST-1001", "Nexus Healthcare Systems", "Healthcare & Biotech", "Enterprise Tier", 180000.0, "Maya Lin", "ACTIVE", 98, "Dr. Robert Vance, CIO"),
            ("CUST-1002", "Vertex FinTech Corp", "Financial Services", "Enterprise Tier", 130000.0, "Maya Lin", "ACTIVE", 92, "Claire Chen, Head of Trading Tech"),
            ("CUST-1003", "Quantum Dynamics Logistics", "Supply Chain", "Mid-Market", 75000.0, "Jessica Alba-Ruiz", "ACTIVE", 88, "Thomas Hardy, VP Ops"),
            ("CUST-1004", "FinEdge Global Capital", "Banking & Investment", "Enterprise Tier", 210000.0, "Jessica Alba-Ruiz", "ACTIVE", 99, "Jonathan Ross, CTO"),
            ("CUST-1005", "OmniMedia Digital Group", "Media & Entertainment", "Mid-Market", 60000.0, "Maya Lin", "ACTIVE", 91, "Sarah Connor, Lead Arch"),
        ]
        cursor.executemany("""
            INSERT INTO customers (customer_code, company_name, industry, contract_tier, annual_contract_value, account_executive, status, health_score, primary_contact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_customers)

    # Deals Pipeline
    cursor.execute("SELECT COUNT(*) FROM deals")
    if cursor.fetchone()[0] == 0:
        sample_deals = [
            ("Apex Global AI Renewal & Expansion", "Apex Logistics Ltd", "Negotiation", 95000.0, "2026-11-15", 85),
            ("Nexus Healthcare AI Automation Add-On", "Nexus Healthcare Systems", "Proposal", 60000.0, "2026-11-30", 70),
            ("Vertex FinTech Core Platform Multi-Year", "Vertex FinTech Corp", "Closed Won", 260000.0, "2026-09-28", 100),
            ("FinEdge High-Frequency Ingestion Module", "FinEdge Global Capital", "Qualification", 120000.0, "2026-12-15", 50),
        ]
        cursor.executemany("""
            INSERT INTO deals (deal_name, customer_name, stage, deal_value, close_date, probability_pct)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_deals)

    # Support & Incident Tickets (Helpdesk)
    cursor.execute("SELECT COUNT(*) FROM support_tickets")
    if cursor.fetchone()[0] == 0:
        sample_tickets = [
            ("TCK-2026-801", "Vertex FinTech Corp", "cchen@vertexfintech.com", "Bug", "CRITICAL", "API Webhook Failures on Settlement Ingestion", "High latency and intermittent 504 Gateway Timeouts observed on production /api/v2/settle endpoints during market open.", "OPEN", "Unassigned", None, "2026-10-06 08:15:00", "2026-10-06 10:15:00"),
            ("TCK-2026-802", "Nexus Healthcare Systems", "support@nexushealth.org", "IT Support", "HIGH", "SSO Login Certificate Expiring in 48 Hours", "Our Okta SAML signing cert will rotate on Thursday; need CentrAlign team to update metadata XML.", "IN_PROGRESS", "Alex Wong", "Updating IdP configuration in staging environment", "2026-10-05 14:00:00", "2026-10-06 18:00:00"),
            ("TCK-2026-803", "Quantum Dynamics Logistics", "ops@quantumdyn.com", "Billing", "MEDIUM", "Invoice Query on Additional Worker Threads", "Requesting breakdown of additional $450 compute surcharge on September invoice INV-CLI-890.", "OPEN", "Thomas Becker", None, "2026-10-04 11:20:00", "2026-10-07 11:20:00"),
            ("TCK-2026-804", "CentrAlign Internal Staff", "chloe.martin@centralign.internal", "System Access", "LOW", "VPN Profile Renewal for Tokyo Staging Cluster", "Requesting configuration profile for new AWS ap-northeast-1 VPC peering bastion.", "RESOLVED", "Alex Wong", "Provisioned WireGuard key and granted access via security group sg-9920", "2026-10-03 16:45:00", "2026-10-04 16:45:00"),
            ("TCK-2026-805", "FinEdge Global Capital", "security@finedge.com", "IT Support", "CRITICAL", "Database Read Replica High Lag Alert", "Secondary Postgres replication lag exceeded 45 seconds on east-1 region.", "OPEN", "Unassigned", None, "2026-10-06 09:00:00", "2026-10-06 11:00:00"),
        ]
        cursor.executemany("""
            INSERT INTO support_tickets (ticket_number, customer_name, requester_email, category, priority, subject, description, status, assignee, resolution_notes, created_at, sla_due)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_tickets)

    # Inventory & Hardware Assets
    cursor.execute("SELECT COUNT(*) FROM inventory")
    if cursor.fetchone()[0] == 0:
        sample_inventory = [
            ("SKU-LAP-M3P", "Apple MacBook Pro 16\" M3 Pro (36GB)", "Hardware", 4, 5, 10, 2499.00, "Apple Enterprise Direct", "Aisle 3 - Secure Cage A"),
            ("SKU-LAP-DELL", "Dell XPS 15 9530 (i7, 32GB, 1TB)", "Hardware", 8, 4, 8, 1750.00, "Dell Enterprise Store", "Aisle 3 - Shelf B"),
            ("SKU-MON-4K", "Dell UltraSharp 32\" 4K USB-C Hub Monitor", "Peripherals", 3, 6, 12, 650.00, "Dell Enterprise Store", "Aisle 2 - Bay 4"),
            ("SKU-NET-SW24", "Cisco Catalyst 24-Port Gigabit PoE Switch", "Network", 2, 3, 5, 1200.00, "Cisco Systems", "Aisle 1 - Server Room"),
            ("SKU-SRV-NV1", "NVIDIA RTX 6000 Ada Generation GPU (48GB)", "Server", 1, 2, 4, 6800.00, "PNY Commercial", "Aisle 1 - High Value Safe"),
            ("SKU-ACC-DOCK", "CalDigit TS4 Thunderbolt 4 Docking Station", "Peripherals", 12, 5, 10, 399.00, "CalDigit Direct", "Aisle 2 - Shelf A"),
            ("SKU-OFF-CHAIR", "Herman Miller Aeron Chair Size B", "Office Supplies", 6, 4, 6, 1195.00, "Acme Supplies Co", "Warehouse Warehouse Floor East"),
            ("SKU-OFF-CABLE", "Cat6A Shielded Ethernet Cable 10ft (10-Pack)", "Network", 25, 10, 20, 45.00, "OfficeMax Pro", "Aisle 2 - Bin 12"),
        ]
        cursor.executemany("""
            INSERT INTO inventory (sku, item_name, category, stock_on_hand, reorder_threshold, target_reorder_qty, unit_cost, supplier, warehouse_location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_inventory)

    # Purchase Orders
    cursor.execute("SELECT COUNT(*) FROM purchase_orders")
    if cursor.fetchone()[0] == 0:
        sample_pos = [
            ("PO-2026-301", "Apple Enterprise Direct", "5x MacBook Pro 14\" M3", 9995.00, "DELIVERED", "2026-09-10 10:00:00", "2026-09-18"),
            ("PO-2026-302", "Dell Enterprise Store", "8x Dell UltraSharp 32\" Monitors", 5200.00, "ISSUED", "2026-10-02 11:30:00", "2026-10-12"),
            ("PO-2026-303", "Acme Supplies Co", "6x Herman Miller Ergonomic Chairs", 7170.00, "ISSUED", "2026-10-04 15:45:00", "2026-10-20"),
        ]
        cursor.executemany("""
            INSERT INTO purchase_orders (po_number, supplier, items_summary, total_cost, status, created_at, delivery_expected)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_pos)

    # Knowledge Base
    cursor.execute("SELECT COUNT(*) FROM knowledge_base")
    if cursor.fetchone()[0] == 0:
        sample_kb = [
            ("KB-HR-01", "Employee Handbook & PTO Policy 2026", "HR", "Complete standards for annual leave (20 days), sick leave (10 days), remote work, and performance promotions.", "data/company_docs/Employee_Handbook_and_Leave_Policy_2026.pdf", "leave, pto, sick leave, hr, benefits, hours"),
            ("KB-FIN-01", "Procurement & Expense Policy 2026", "Finance", "Autonomous threshold limit ($3,000 USD), expense reimbursement rules, corporate card guidelines, Net-30 terms.", "data/company_docs/Procurement_and_Expense_Policy.pdf", "procurement, invoice, threshold, approval, expense, limit"),
            ("KB-SEC-01", "IT Security & Incident Governance", "Security", "MFA guidelines, password rotation, ticket response SLAs: Critical P1 (30m), High P2 (2h), Medium P3 (8h).", "data/company_docs/IT_Security_and_Access_Control_Policy.pdf", "security, mfa, incident, sla, priority, access"),
            ("KB-VND-01", "Vendor Contract - CyberShield Security", "Contracts", "Master Services Agreement for 24/7 SOC managed monitoring at $84k/year ($7,000/mo) through 2028.", "data/company_docs/Vendor_Contract_CyberShield_Security.pdf", "vendor, contract, cybershield, soc, security"),
        ]
        cursor.executemany("""
            INSERT INTO knowledge_base (doc_id, title, category, summary, file_path, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_kb)

    conn.commit()
    conn.close()

# -------------------------------------------------------------
# AUDIT LOGGING HELPER
# -------------------------------------------------------------
def log_audit(action: str, details: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (action, details, timestamp) VALUES (?, ?, ?)",
        (action, details, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# -------------------------------------------------------------
# COMPANY PROFILE & DEPARTMENTS
# -------------------------------------------------------------
def get_company_profile() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM company_profile LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def get_all_departments() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM departments ORDER BY budget_q3 DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_department(name: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM departments WHERE LOWER(name) LIKE ? LIMIT 1", (f"%{name.lower().strip()}%",))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# -------------------------------------------------------------
# EMPLOYEES & HR
# -------------------------------------------------------------
def get_all_employees() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_employee(identifier: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    ident = identifier.strip().lower()
    cursor.execute("""
        SELECT * FROM employees 
        WHERE LOWER(emp_code) = ? OR LOWER(name) LIKE ? OR LOWER(email) LIKE ?
        LIMIT 1
    """, (ident, f"%{ident}%", f"%{ident}%"))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_employee(emp_identifier: str, **kwargs) -> Optional[Dict[str, Any]]:
    emp = get_employee(emp_identifier)
    if not emp:
        return None
    
    conn = get_connection()
    cursor = conn.cursor()
    allowed_fields = ["title", "department", "salary", "status", "leave_balance", "manager_name", "performance_rating"]
    updates = []
    values = []
    
    for k, v in kwargs.items():
        if k in allowed_fields:
            updates.append(f"{k} = ?")
            values.append(v)
            
    if not updates:
        conn.close()
        return emp
        
    values.append(emp["id"])
    query = f"UPDATE employees SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    
    log_audit("EMPLOYEE_UPDATED", f"Updated employee {emp['name']} ({emp['emp_code']}): {kwargs}")
    return get_employee(emp["emp_code"])

# -------------------------------------------------------------
# LEAVE REQUESTS
# -------------------------------------------------------------
def get_all_leave_requests(status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM leave_requests WHERE UPPER(status) = ? ORDER BY id DESC", (status.upper(),))
    else:
        cursor.execute("SELECT * FROM leave_requests ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_leave_request_status(identifier: str, new_status: str, approver_notes: str = "") -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    ident = identifier.strip().lower()
    cursor.execute("""
        SELECT * FROM leave_requests 
        WHERE LOWER(req_code) = ? OR LOWER(emp_name) LIKE ?
        ORDER BY id DESC LIMIT 1
    """, (ident, f"%{ident}%"))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    req = dict(row)
    cursor.execute("""
        UPDATE leave_requests 
        SET status = ?, approver_notes = ?
        WHERE id = ?
    """, (new_status.upper(), approver_notes, req["id"]))
    
    # If approved, deduct days from employee leave balance
    if new_status.upper() == "APPROVED" and req["status"] != "APPROVED":
        cursor.execute("""
            UPDATE employees 
            SET leave_balance = MAX(0, leave_balance - ?)
            WHERE LOWER(name) = ?
        """, (req["days_requested"], req["emp_name"].lower()))
        
    conn.commit()
    conn.close()
    
    log_audit("LEAVE_REQUEST_UPDATED", f"Leave request {req['req_code']} for {req['emp_name']} marked {new_status}. Notes: {approver_notes}")
    
    # Return refreshed record
    conn2 = get_connection()
    c2 = conn2.cursor()
    c2.execute("SELECT * FROM leave_requests WHERE id = ?", (req["id"],))
    updated_row = c2.fetchone()
    conn2.close()
    return dict(updated_row) if updated_row else None

# -------------------------------------------------------------
# INVOICES
# -------------------------------------------------------------
def get_all_invoices() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_invoice_by_number(invoice_number: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_invoice(invoice_number: str, vendor_name: str, amount: float, due_date: str, currency: str = "USD", notes: str = "", invoice_type: str = "PAYABLE") -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """INSERT INTO invoices (invoice_number, vendor_name, invoice_type, amount, currency, due_date, status, notes, created_at)
           VALUES (?, ?, ?, ?, ?, ?, 'ENTERED', ?, ?)""",
        (invoice_number, vendor_name, invoice_type, amount, currency, due_date, notes, created_at)
    )
    invoice_id = cursor.lastrowid
    conn.commit()
    conn.close()
    log_audit("INVOICE_CREATED", f"Created {invoice_type} invoice {invoice_number} for {vendor_name} amount: ${amount:.2f} {currency}")
    return {
        "id": invoice_id,
        "invoice_number": invoice_number,
        "vendor_name": vendor_name,
        "invoice_type": invoice_type,
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
    cursor.execute(
        """SELECT * FROM invoices 
           WHERE LOWER(vendor_name) LIKE ? AND ABS(amount - ?) < 0.01
           ORDER BY id DESC LIMIT 1""",
        (f"%{vendor_name.lower().strip()}%", amount)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# -------------------------------------------------------------
# EXPENSE REPORTS
# -------------------------------------------------------------
def get_all_expenses(status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM expense_reports WHERE UPPER(status) = ? ORDER BY id DESC", (status.upper(),))
    else:
        cursor.execute("SELECT * FROM expense_reports ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_expense_status(report_number: str, new_status: str, notes: str = "") -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expense_reports WHERE report_number = ?", (report_number,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    cursor.execute("UPDATE expense_reports SET status = ?, notes = ? WHERE report_number = ?", (new_status.upper(), notes, report_number))
    conn.commit()
    conn.close()
    log_audit("EXPENSE_UPDATED", f"Expense {report_number} marked {new_status}")
    
    conn2 = get_connection()
    c2 = conn2.cursor()
    c2.execute("SELECT * FROM expense_reports WHERE report_number = ?", (report_number,))
    updated = c2.fetchone()
    conn2.close()
    return dict(updated) if updated else None

# -------------------------------------------------------------
# CUSTOMERS & DEALS (CRM)
# -------------------------------------------------------------
def get_all_customers() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY annual_contract_value DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_customer(name: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE LOWER(company_name) LIKE ? LIMIT 1", (f"%{name.lower().strip()}%",))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_deals() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deals ORDER BY deal_value DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_deal(deal_name: str, customer_name: str, stage: str, deal_value: float, close_date: str, probability_pct: int = 50) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO deals (deal_name, customer_name, stage, deal_value, close_date, probability_pct)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (deal_name, customer_name, stage, deal_value, close_date, probability_pct))
    deal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    log_audit("DEAL_CREATED", f"Created deal '{deal_name}' for {customer_name} (${deal_value:,.2f})")
    return {"id": deal_id, "deal_name": deal_name, "customer_name": customer_name, "deal_value": deal_value, "stage": stage}

# -------------------------------------------------------------
# SUPPORT TICKETS (ITSM / Helpdesk)
# -------------------------------------------------------------
def get_all_tickets(status: Optional[str] = None, priority: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM support_tickets WHERE 1=1"
    params = []
    if status:
        query += " AND UPPER(status) = ?"
        params.append(status.upper())
    if priority:
        query += " AND UPPER(priority) = ?"
        params.append(priority.upper())
    query += " ORDER BY CASE priority WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END, id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_ticket(ticket_identifier: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    ident = ticket_identifier.strip().lower()
    cursor.execute("""
        SELECT * FROM support_tickets 
        WHERE LOWER(ticket_number) = ? OR LOWER(subject) LIKE ?
        LIMIT 1
    """, (ident, f"%{ident}%"))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_ticket(ticket_number: str, status: Optional[str] = None, assignee: Optional[str] = None, resolution_notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
    ticket = get_ticket(ticket_number)
    if not ticket:
        return None
    
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if status:
        updates.append("status = ?")
        params.append(status.upper())
    if assignee:
        updates.append("assignee = ?")
        params.append(assignee)
    if resolution_notes:
        updates.append("resolution_notes = ?")
        params.append(resolution_notes)
        
    if not updates:
        conn.close()
        return ticket
        
    params.append(ticket["id"])
    cursor.execute(f"UPDATE support_tickets SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    
    log_audit("TICKET_UPDATED", f"Updated ticket {ticket['ticket_number']}: status={status}, assignee={assignee}")
    return get_ticket(ticket["ticket_number"])

# -------------------------------------------------------------
# INVENTORY & SUPPLY CHAIN
# -------------------------------------------------------------
def get_all_inventory() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory ORDER BY stock_on_hand ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_low_stock_inventory() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE stock_on_hand <= reorder_threshold ORDER BY stock_on_hand ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_purchase_order(supplier: str, items_summary: str, total_cost: float, delivery_expected: str = "") -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    po_num = f"PO-{datetime.now().strftime('%Y')}-{abs(hash(items_summary + now_str)) % 900 + 100}"
    if not delivery_expected:
        delivery_expected = datetime.fromtimestamp(datetime.now().timestamp() + 86400 * 14).strftime("%Y-%m-%d")
        
    cursor.execute("""
        INSERT INTO purchase_orders (po_number, supplier, items_summary, total_cost, status, created_at, delivery_expected)
        VALUES (?, ?, ?, ?, 'ISSUED', ?, ?)
    """, (po_num, supplier, items_summary, total_cost, now_str, delivery_expected))
    po_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    log_audit("PURCHASE_ORDER_ISSUED", f"Issued {po_num} to {supplier} for ${total_cost:,.2f} ({items_summary})")
    return {
        "id": po_id,
        "po_number": po_num,
        "supplier": supplier,
        "items_summary": items_summary,
        "total_cost": total_cost,
        "status": "ISSUED",
        "created_at": now_str,
        "delivery_expected": delivery_expected
    }

def get_all_purchase_orders() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM purchase_orders ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# -------------------------------------------------------------
# KNOWLEDGE BASE & POLICIES
# -------------------------------------------------------------
def search_knowledge_base(query_str: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    q = f"%{query_str.lower().strip()}%"
    cursor.execute("""
        SELECT * FROM knowledge_base
        WHERE LOWER(title) LIKE ? OR LOWER(summary) LIKE ? OR LOWER(tags) LIKE ? OR LOWER(category) LIKE ?
    """, (q, q, q, q))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# -------------------------------------------------------------
# TEST RECORD RESET
# -------------------------------------------------------------
def reset_test_records():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoices WHERE invoice_number LIKE 'INV-CX-%' OR vendor_name LIKE '%Company X%'")
    # Reset Sarah Jenkins leave request if tested
    cursor.execute("UPDATE leave_requests SET status = 'PENDING', approver_notes = NULL WHERE req_code = 'LV-2026-001'")
    cursor.execute("UPDATE employees SET leave_balance = 16 WHERE emp_code = 'EMP-101'")
    # Reset support ticket 801
    cursor.execute("UPDATE support_tickets SET status = 'OPEN', assignee = 'Unassigned', resolution_notes = NULL WHERE ticket_number = 'TCK-2026-801'")
    # Clean test POs
    cursor.execute("DELETE FROM purchase_orders WHERE po_number LIKE 'PO-TEST-%'")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Enterprise Database initialized and seeded successfully.")
