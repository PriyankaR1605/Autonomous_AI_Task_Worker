import os
import sys
from datetime import datetime

def generate_pdf(filepath: str, title: str, vendor: str, invoice_no: str, date_str: str, due_date_str: str, amount: float, items: list):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        story = []

        # Title / Vendor Header
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=6
        )
        sub_style = ParagraphStyle(
            'SubHeader',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=15
        )

        story.append(Paragraph(f"<b>{vendor}</b>", header_style))
        story.append(Paragraph("Commercial Invoice & Billing Statement", sub_style))
        story.append(Spacer(1, 15))

        # Invoice Metadata Table
        meta_data = [
            [Paragraph("<b>Invoice Number:</b>", styles['Normal']), Paragraph(invoice_no, styles['Normal'])],
            [Paragraph("<b>Issue Date:</b>", styles['Normal']), Paragraph(date_str, styles['Normal'])],
            [Paragraph("<b>Payment Due Date:</b>", styles['Normal']), Paragraph(f"<font color='#DC2626'><b>{due_date_str}</b></font>", styles['Normal'])],
            [Paragraph("<b>Billed To:</b>", styles['Normal']), Paragraph("CentrAlign Technologies Inc.", styles['Normal'])],
        ]
        meta_table = Table(meta_data, colWidths=[130, 380])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 20))

        # Line Items
        table_data = [["Item Description", "Qty", "Unit Price", "Total"]]
        for desc, qty, unit, line_total in items:
            table_data.append([desc, str(qty), f"${unit:.2f}", f"${line_total:.2f}"])
        
        table_data.append(["", "", "Total Due:", f"${amount:.2f}"])

        items_table = Table(table_data, colWidths=[260, 60, 90, 100])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#CBD5E1')),
            ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (3, -1), (3, -1), colors.HexColor('#059669')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F1F5F9')),
            ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor('#0F172A')),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 30))

        footer_text = Paragraph(
            "<i>Thank you for your business. Remit electronic payment before the due date. For inquiries, contact billing@companyx.internal.</i>",
            styles['Italic']
        )
        story.append(footer_text)

        doc.build(story)
        print(f"Generated PDF invoice: {filepath}")

    except ImportError:
        # Fallback to structured text file if reportlab not yet compiled
        txt_path = filepath.replace(".pdf", ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"=== {vendor} ===\n")
            f.write(f"Invoice Number: {invoice_no}\n")
            f.write(f"Issue Date: {date_str}\n")
            f.write(f"Due Date: {due_date_str}\n")
            f.write(f"Total Amount: ${amount:.2f} USD\n")
            f.write("\nItems:\n")
            for desc, qty, unit, line_total in items:
                f.write(f"  - {desc} (Qty: {qty}) @ ${unit:.2f} = ${line_total:.2f}\n")
        print(f"Reportlab not installed yet. Generated fallback TXT invoice: {txt_path}")

def main():
    dest_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_invoices")
    os.makedirs(dest_dir, exist_ok=True)

    # 1. Latest Invoice for Company X (The primary target for the user prompt!)
    generate_pdf(
        filepath=os.path.join(dest_dir, "Invoice_CompanyX_Latest.pdf"),
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

    # 2. Older / Previous Invoice for Company X (to test that the agent finds the *latest* invoice)
    generate_pdf(
        filepath=os.path.join(dest_dir, "Invoice_CompanyX_Old.pdf"),
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

    # 3. Invoice for Company Y (to test vendor discrimination)
    generate_pdf(
        filepath=os.path.join(dest_dir, "Invoice_CompanyY_Draft.pdf"),
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

if __name__ == "__main__":
    main()
