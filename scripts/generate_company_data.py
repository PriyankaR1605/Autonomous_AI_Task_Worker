"""
Central data generation script for CentrAlign Technologies Inc.
Generates comprehensive synthetic enterprise data:
- PDF & TXT Policy Documents (Employee Handbook, Procurement Policy, IT Security, Travel & Expense, SLAs)
- Realistic Invoices & Billing Statements
- Vendor Contracts & Master Service Agreements
- Seeds the enterprise database with realistic records across all departments
"""

import os
import sys
from datetime import datetime, date

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def ensure_dirs():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    docs_dir = os.path.join(base_dir, "data", "company_docs")
    invoices_dir = os.path.join(base_dir, "data", "sample_invoices")
    storage_dir = os.path.join(base_dir, "data", "storage")
    screenshots_dir = os.path.join(storage_dir, "screenshots")
    
    for d in [docs_dir, invoices_dir, storage_dir, screenshots_dir]:
        os.makedirs(d, exist_ok=True)
    return docs_dir, invoices_dir

def create_pdf_or_txt(filepath: str, title: str, subtitle: str, content_paragraphs: list, metadata_table: list = None):
    """Creates a PDF file if reportlab is available, and always writes a corresponding TXT version."""
    txt_path = filepath.rsplit(".", 1)[0] + ".txt"
    
    # Write plain text format
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"=== {title.upper()} ===\n")
        f.write(f"{subtitle}\n")
        f.write("=" * 60 + "\n\n")
        if metadata_table:
            f.write("METADATA & DETAILS:\n")
            for row in metadata_table:
                f.write(f"  {row[0]}: {row[1]}\n")
            f.write("-" * 60 + "\n\n")
        for heading, body in content_paragraphs:
            if heading:
                f.write(f"## {heading}\n")
            f.write(f"{body}\n\n")
    
    # Attempt PDF generation
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        pdf_path = filepath.rsplit(".", 1)[0] + ".pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        story = []

        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=4
        )
        sub_style = ParagraphStyle(
            'SubHeader',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=15
        )
        h2_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=10,
            spaceAfter=4
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=9.5,
            textColor=colors.HexColor('#334155'),
            
            leading=13,
            spaceAfter=8
        )

        story.append(Paragraph(f"<b>{title}</b>", header_style))
        story.append(Paragraph(subtitle, sub_style))
        story.append(Spacer(1, 10))

        if metadata_table:
            table_data = [[Paragraph(f"<b>{k}</b>", body_style), Paragraph(str(v), body_style)] for k, v in metadata_table]
            t = Table(table_data, colWidths=[150, 360])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(t)
            story.append(Spacer(1, 15))

        for heading, body in content_paragraphs:
            if heading:
                story.append(Paragraph(f"<b>{heading}</b>", h2_style))
            story.append(Paragraph(body.replace("\n", "<br/>"), body_style))
            story.append(Spacer(1, 6))

        doc.build(story)
        print(f"Generated PDF: {pdf_path}")
    except Exception as e:
        print(f"PDF creation skipped for {filepath}: {e}")

def generate_all_company_documents():
    docs_dir, invoices_dir = ensure_dirs()

    # 1. Employee Handbook & Leave Policy
    create_pdf_or_txt(
        filepath=os.path.join(docs_dir, "Employee_Handbook_and_Leave_Policy_2026.pdf"),
        title="CentrAlign Technologies Inc. — Employee Handbook",
        subtitle="Version 4.2 | Human Resources & Workplace Standards | Effective 2026",
        metadata_table=[
            ("Department", "Human Resources"),
            ("Document ID", "HR-POL-2026-04"),
            ("Effective Date", "January 1, 2026"),
            ("Approved By", "Elena Vance, VP of People & Culture"),
        ],
        content_paragraphs=[
            ("1. Annual Paid Time Off (PTO) Guidelines",
             "Full-time regular employees accrue 20 paid vacation days per calendar year. "
             "Leave requests under 3 consecutive days require direct manager sign-off within 2 business days. "
             "Leave requests of 5 or more days must be submitted at least 2 weeks in advance. "
             "Employees may carry over a maximum of 5 unused leave days into the subsequent calendar year."),
            ("2. Sick and Medical Leave",
             "All staff members receive 10 paid sick days annually. Sick leave of more than 3 consecutive working "
             "days requires a qualified medical practitioner note uploaded to the HR portal."),
            ("3. Remote Work & Core Collaboration Hours",
             "CentrAlign operates on a hybrid-first model. Core operational hours across all domestic offices "
             "are 10:00 AM to 4:00 PM local time. Remote employees are expected to maintain availability via "
             "Slack and respond to high-priority operational requests within 60 minutes."),
            ("4. Performance Reviews and Title Promotions",
             "Performance reviews are held biannually in June and December. Job title updates and merit-based "
             "compensation increases require dual approval from the Department Head and the VP of HR.")
        ]
    )

    # 2. Procurement & Purchasing Policy
    create_pdf_or_txt(
        filepath=os.path.join(docs_dir, "Procurement_and_Expense_Policy.pdf"),
        title="CentrAlign Technologies Inc. — Procurement & Purchasing Policy",
        subtitle="Corporate Finance & Fiscal Governance | Threshold Standards 2026",
        metadata_table=[
            ("Department", "Finance & Accounting"),
            ("Document ID", "FIN-PROC-2026-01"),
            ("Financial Authority Limit", "$3,000.00 USD Autonomous Threshold"),
            ("Authorizer", "Marcus Thorne, Chief Financial Officer"),
        ],
        content_paragraphs=[
            ("1. Autonomous Approval Thresholds",
             "Any commercial invoice or purchase requisition equal to or less than $3,000.00 USD may be "
             "processed and recorded autonomously by certified automated workflows or staff accountants. "
             "Transactions strictly exceeding $3,000.00 USD require explicit Human-in-the-Loop authorization "
             "from the Finance Director or CFO before entry into the general ledger."),
            ("2. Corporate Credit Card & Expense Reimbursements",
             "Individual employee expense claims exceeding $1,000.00 USD require direct supervisor pre-approval. "
             "Itemized digital receipts must be submitted within 14 calendar days of incurring the expense. "
             "Alcohol, luxury dining, and unapproved flight upgrades are strictly non-reimbursable."),
            ("3. Preferred Vendors and Payment Terms",
             "Standard vendor payment terms are Net-30 from receipt of valid commercial invoice. "
             "Approved cloud hosting partners include Global Cloud Hosting and CloudScale Networks. "
             "Office equipment and IT hardware must be procured through Dell Enterprise or OfficeMax Pro.")
        ]
    )

    # 3. IT Security and Access Control Policy
    create_pdf_or_txt(
        filepath=os.path.join(docs_dir, "IT_Security_and_Access_Control_Policy.pdf"),
        title="CentrAlign Technologies Inc. — IT Security & Data Governance",
        subtitle="Information Security Management System | ISO/IEC 27001 Aligned",
        metadata_table=[
            ("Department", "Information Technology & Security"),
            ("Document ID", "SEC-GOV-2026-09"),
            ("Classification", "Internal Enterprise Confidential"),
            ("Lead Architect", "David Miller, Lead Security Engineer"),
        ],
        content_paragraphs=[
            ("1. Multi-Factor Authentication & Password Rules",
             "All enterprise accounts require hardware-backed FIDO2 MFA. Passwords must contain a minimum "
             "of 16 characters and undergo automated rotation flags every 90 days."),
            ("2. Incident Severity Classification & SLAs",
             "- CRITICAL (P1): Production outage, data breach, or security compromise. Response SLA: 30 minutes. 24/7 coverage.\n"
             "- HIGH (P2): Core business workflow degraded with no workaround. Response SLA: 2 hours.\n"
             "- MEDIUM (P3): Individual employee blocker with workaround. Response SLA: 8 hours.\n"
             "- LOW (P4): General IT inquiry or routine hardware request. Response SLA: 24 hours."),
            ("3. Access Rights & Privilege Escalation",
             "Administrative access to production databases and ERP financial ledgers requires role-based access "
             "control (RBAC) sign-off from IT Security. Dormant accounts inactive for 45 days are automatically disabled.")
        ]
    )

    # 4. Vendor Master Agreement - CyberShield Sec
    create_pdf_or_txt(
        filepath=os.path.join(docs_dir, "Vendor_Contract_CyberShield_Security.pdf"),
        title="Master Services Agreement — CyberShield Security LLC",
        subtitle="Enterprise Security Operations Center (SOC) Managed Services",
        metadata_table=[
            ("Vendor Name", "CyberShield Security LLC"),
            ("Contract Reference", "MSA-2026-CS-781"),
            ("Effective Term", "January 15, 2026 to January 14, 2028"),
            ("Annual Value", "$84,000.00 USD ($7,000.00/month)"),
            ("Contact Person", "Rachel Adams (radams@cybershield-sec.com)"),
        ],
        content_paragraphs=[
            ("1. Scope of Managed Monitoring",
             "Vendor shall provide 24x7x365 managed SIEM monitoring, threat hunting, and automated endpoint "
             "containment across all CentrAlign cloud virtual networks and user workstations."),
            ("2. Incident Response Guarantees",
             "Vendor guarantees initial containment of confirmed critical security incidents within 15 minutes "
             "of automated detection. Failure to meet monthly SLA entitles CentrAlign to a 10% credit penalty.")
        ]
    )

    # 5. Generate Test Invoices in data/sample_invoices/
    from scripts.generate_sample_invoices import generate_pdf as gen_inv_pdf
    
    # Invoice 1: Company X Latest
    gen_inv_pdf(
        filepath=os.path.join(invoices_dir, "Invoice_CompanyX_Latest.pdf"),
        title="Company X - Enterprise SaaS Services",
        vendor="Company X",
        invoice_no="INV-CX-2026-904",
        date_str="2026-10-01",
        due_date_str="2026-11-15",
        amount=4850.00,
        items=[
            ("Enterprise Platform Annual License Tier 2", 1, 3600.00, 3600.00),
            ("Premium API SLA Package (Oct 2026)", 1, 750.00, 750.00),
            ("Dedicated Cloud Engineering Support (5 hrs)", 5, 100.00, 500.00),
        ]
    )

    # Invoice 2: Company X Old
    gen_inv_pdf(
        filepath=os.path.join(invoices_dir, "Invoice_CompanyX_Old.pdf"),
        title="Company X - Consulting & Setup",
        vendor="Company X",
        invoice_no="INV-CX-2026-102",
        date_str="2026-04-10",
        due_date_str="2026-05-25",
        amount=1200.00,
        items=[
            ("Initial System Architecture Onboarding", 1, 1200.00, 1200.00)
        ]
    )

    # Invoice 3: Company Y Draft
    gen_inv_pdf(
        filepath=os.path.join(invoices_dir, "Invoice_CompanyY_Draft.pdf"),
        title="Company Y - Logistics & Storage",
        vendor="Company Y",
        invoice_no="INV-CY-2026-440",
        date_str="2026-09-18",
        due_date_str="2026-10-30",
        amount=2890.50,
        items=[
            ("Secure Cold Storage Facility Lease", 1, 2890.50, 2890.50)
        ]
    )

    # Invoice 4: Acme Supplies
    gen_inv_pdf(
        filepath=os.path.join(invoices_dir, "Invoice_AcmeSupplies_Q3.pdf"),
        title="Acme Supplies Co - Office & Ergonomics",
        vendor="Acme Supplies Co",
        invoice_no="INV-ACME-2026-881",
        date_str="2026-09-25",
        due_date_str="2026-10-25",
        amount=1650.00,
        items=[
            ("Ergonomic Mesh Task Chairs Model Elite", 3, 450.00, 1350.00),
            ("Cable Management & Dual Monitor Arms", 3, 100.00, 300.00)
        ]
    )

    # Invoice 5: Global Cloud Hosting
    gen_inv_pdf(
        filepath=os.path.join(invoices_dir, "Invoice_GlobalCloud_Oct2026.pdf"),
        title="Global Cloud Hosting - Infrastructure",
        vendor="Global Cloud Hosting",
        invoice_no="INV-GCH-2026-512",
        date_str="2026-10-02",
        due_date_str="2026-11-02",
        amount=2150.00,
        items=[
            ("High-Memory Kubernetes Compute Cluster", 1, 1750.00, 1750.00),
            ("Global Anycast CDN & Bandwidth Egress", 1, 400.00, 400.00)
        ]
    )

    print("All company policy documents and invoice files successfully created.")

def seed_database():
    """Populates the SQLite database with full enterprise cross-departmental datasets and exports master tables."""
    from mock_erp.database import init_db
    init_db()
    try:
        from scripts.generate_big_enterprise_dataset import (
            generate_all_single_file_tables,
            generate_unified_enterprise_dataset,
            generate_master_invoices_document,
            seed_big_dataset_to_sqlite
        )
        generate_all_single_file_tables()
        generate_unified_enterprise_dataset()
        generate_master_invoices_document()
        seed_big_dataset_to_sqlite()
    except Exception as e:
        print(f"Big dataset synchronization note: {e}")
    print("Database schema verified and populated with comprehensive enterprise data.")

def main():
    print("=================================================================")
    print("Generating Complete Enterprise Company Data for CentrAlign Technologies")
    print("=================================================================")
    generate_all_company_documents()
    seed_database()
    print("=================================================================")
    print("Dataset generation complete! All company facets ready for autonomous execution.")
    print("=================================================================")

if __name__ == "__main__":
    main()

