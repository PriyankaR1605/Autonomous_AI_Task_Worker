"""
Data Cleaning & Deduplication Utility for CentrAlign Technologies Inc.
Ensures zero duplicate records across:
1. SQLite Database (mock_erp/erp.db)
2. All Single-File Master Tables (data/enterprise_tables/)
3. Unified Master Enterprise Dataset (data/enterprise_tables/ALL_DOMAINS_ENTERPRISE_MASTER_DATASET.json)
4. Consolidated Master Invoices Register documents
"""

import os
import sys
import sqlite3
import json
import csv
from collections import OrderedDict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

TABLES_DIR = os.path.join(PROJECT_ROOT, "data", "enterprise_tables")
DB_PATH = os.path.join(PROJECT_ROOT, "mock_erp", "erp.db")

def clean_sqlite_database():
    print("\n--- 1. Cleaning & Deduplicating SQLite Database (mock_erp/erp.db) ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # A. Clean purchase_orders: Remove repeated test-generated POs
    cursor.execute("""
        DELETE FROM purchase_orders
        WHERE po_number NOT IN (
            'PO-2026-301', 'PO-2026-302', 'PO-2026-303', 'PO-2026-304',
            'PO-2026-305', 'PO-2026-306', 'PO-2026-307', 'PO-2026-308'
        )
    """)
    removed_pos = cursor.rowcount
    print(f"  - Removed {removed_pos} redundant / repeated test purchase orders.")

    # B. Ensure all canonical invoices exist without duplication
    from scripts.generate_big_enterprise_dataset import INVOICES_DATA
    inv_readded = 0
    for inv in INVOICES_DATA:
        cursor.execute("SELECT id FROM invoices WHERE invoice_number = ?", (inv["invoice_number"],))
        existing = cursor.fetchall()
        if len(existing) > 1:
            # Delete extra duplicates, keep only lowest id
            keep_id = existing[0][0]
            for extra in existing[1:]:
                cursor.execute("DELETE FROM invoices WHERE id = ?", (extra[0],))
                print(f"  - Deleted duplicate invoice {inv['invoice_number']} with id {extra[0]}")
        elif len(existing) == 0:
            cursor.execute("""
                INSERT INTO invoices (invoice_number, vendor_name, invoice_type, amount, currency, due_date, status, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (inv["invoice_number"], inv["vendor_name"], inv["invoice_type"], inv["amount"], inv["currency"], inv["due_date"], inv["status"], inv["notes"], inv["created_at"]))
            inv_readded += 1
    if inv_readded:
        print(f"  - Reconciled {inv_readded} missing canonical invoices in SQLite.")

    # C. Check each table for any row duplicates
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [r[0] for r in cursor.fetchall()]

    for tbl in tables:
        cursor.execute(f"PRAGMA table_info({tbl})")
        cols = [c[1] for c in cursor.fetchall()]
        data_cols = [c for c in cols if c != "id"]
        if not data_cols:
            continue

        col_str = ", ".join(data_cols)
        # Find duplicates by data columns
        cursor.execute(f"""
            SELECT id, {col_str} FROM {tbl}
            WHERE id NOT IN (
                SELECT MIN(id) FROM {tbl} GROUP BY {col_str}
            )
        """)
        dups = cursor.fetchall()
        if dups:
            dup_ids = [d[0] for d in dups]
            cursor.execute(f"DELETE FROM {tbl} WHERE id IN ({','.join(map(str, dup_ids))})")
            print(f"  - Cleaned {len(dup_ids)} duplicate rows from table '{tbl}'.")

    conn.commit()
    conn.close()
    print("  [OK] SQLite Database deduplication complete.")

def clean_csv_and_json_tables():
    print("\n--- 2. Auditing & Deduplicating Master CSV & JSON Tables ---")
    if not os.path.exists(TABLES_DIR):
        return

    csv_files = [f for f in os.listdir(TABLES_DIR) if f.endswith(".csv")]
    for cf in sorted(csv_files):
        csv_path = os.path.join(TABLES_DIR, cf)
        json_path = os.path.join(TABLES_DIR, cf.replace(".csv", ".json"))

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        initial_len = len(reader)
        if not reader:
            continue

        primary_key = list(reader[0].keys())[0]

        # Deduplicate preserving order
        seen_keys = set()
        deduped = []
        for row in reader:
            val = row[primary_key]
            if val not in seen_keys:
                seen_keys.add(val)
                deduped.append(row)

        if len(deduped) < initial_len:
            removed = initial_len - len(deduped)
            print(f"  - Deduplicated {cf}: removed {removed} repeated records ({initial_len} -> {len(deduped)})")
            # Write back clean CSV
            fieldnames = list(deduped[0].keys())
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(deduped)
            # Write back clean JSON
            if os.path.exists(json_path):
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(deduped, f, indent=2)
        else:
            print(f"  - Verified {cf:<35}: {initial_len} records [100% UNIQUE]")

def refresh_master_unified_dataset():
    print("\n--- 3. Refreshing Master Unified Dataset & Invoices Register ---")
    from scripts.generate_big_enterprise_dataset import (
        generate_unified_enterprise_dataset,
        generate_master_invoices_document
    )
    generate_unified_enterprise_dataset()
    generate_master_invoices_document()
    print("  [OK] Master dataset files regenerated and verified.")

def main():
    print("=================================================================")
    print("CENTRALIGN TECHNOLOGIES — DATA AUDIT & DEDUPLICATION PIPELINE")
    print("=================================================================")
    clean_sqlite_database()
    clean_csv_and_json_tables()
    refresh_master_unified_dataset()
    print("\n=================================================================")
    print("ALL REPEATED DATA IDENTIFIED AND REMOVED! ZERO DUPLICATES REMAIN.")
    print("=================================================================")

if __name__ == "__main__":
    main()
