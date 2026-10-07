"""
Master Big Dataset Generator for CentrAlign Technologies Inc.
Generates a comprehensive, enterprise-grade multi-domain dataset:
1. Domain-specific single master table files (CSV & JSON) in data/enterprise_tables/
   - invoices_master_table.csv / .json (ALL invoices for all vendors, clients & people in ONE file)
   - employees_master_table.csv / .json (Complete 60+ staff directory in ONE file)
   - leave_requests_master_table.csv / .json (Leave requests in ONE file)
   - support_tickets_master_table.csv / .json (ITSM helpdesk tickets in ONE file)
   - inventory_master_table.csv / .json (Warehouse assets & hardware in ONE file)
   - expenses_master_table.csv / .json (Employee expense claims in ONE file)
   - customers_crm_master_table.csv / .json (Enterprise CRM accounts in ONE file)
   - deals_master_table.csv / .json (Sales pipeline in ONE file)
   - departments_master_table.csv / .json (Department budgets & headcounts in ONE file)
   - purchase_orders_master_table.csv / .json (Procurement orders in ONE file)
2. Unified Master Dataset file:
   - ALL_DOMAINS_ENTERPRISE_MASTER_DATASET.json (Entire company dataset in ONE file)
3. Consolidated Corporate Document:
   - data/sample_invoices/Master_Invoices_Register.pdf & .txt
4. Seeds the enterprise SQLite database (mock_erp/erp.db) with the full big dataset.
"""

import os
import sys
import csv
import json
import sqlite3
from datetime import datetime, date

# Ensure root directory is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

TABLES_DIR = os.path.join(PROJECT_ROOT, "data", "enterprise_tables")
DOCS_DIR = os.path.join(PROJECT_ROOT, "data", "company_docs")
INVOICES_DIR = os.path.join(PROJECT_ROOT, "data", "sample_invoices")
DB_PATH = os.path.join(PROJECT_ROOT, "mock_erp", "erp.db")

def ensure_directories():
    for d in [TABLES_DIR, DOCS_DIR, INVOICES_DIR]:
        os.makedirs(d, exist_ok=True)

# -------------------------------------------------------------
# 1. DEPARTMENTS DATA (10 Departments)
# -------------------------------------------------------------
DEPARTMENTS_DATA = [
    {"id": 1, "name": "Engineering", "head_of_dept": "Marcus Vance", "budget_q3": 850000.0, "spent_q3": 742500.0, "headcount": 95},
    {"id": 2, "name": "IT & Security", "head_of_dept": "Alex Wong", "budget_q3": 320000.0, "spent_q3": 284000.0, "headcount": 24},
    {"id": 3, "name": "Sales & Revenue", "head_of_dept": "Jessica Alba-Ruiz", "budget_q3": 480000.0, "spent_q3": 421000.0, "headcount": 48},
    {"id": 4, "name": "Marketing & Growth", "head_of_dept": "David Sterling", "budget_q3": 280000.0, "spent_q3": 162500.0, "headcount": 26},
    {"id": 5, "name": "Human Resources", "head_of_dept": "Elena Vance", "budget_q3": 160000.0, "spent_q3": 138000.0, "headcount": 14},
    {"id": 6, "name": "Finance & Legal", "head_of_dept": "Marcus Thorne", "budget_q3": 210000.0, "spent_q3": 184500.0, "headcount": 18},
    {"id": 7, "name": "Customer Success", "head_of_dept": "Amina Patel", "budget_q3": 220000.0, "spent_q3": 192000.0, "headcount": 35},
    {"id": 8, "name": "Product & Design", "head_of_dept": "Samantha Reed", "budget_q3": 310000.0, "spent_q3": 276000.0, "headcount": 22},
    {"id": 9, "name": "Operations & Facilities", "head_of_dept": "Raymond Cruz", "budget_q3": 190000.0, "spent_q3": 165000.0, "headcount": 16},
    {"id": 10, "name": "Data & AI Research", "head_of_dept": "Dr. Aris Thorne", "budget_q3": 420000.0, "spent_q3": 380000.0, "headcount": 20},
]

# -------------------------------------------------------------
# 2. EMPLOYEES DATA (60 Enterprise Staff Members)
# -------------------------------------------------------------
EMPLOYEES_DATA = [
    # Engineering
    {"emp_code": "EMP-101", "name": "Sarah Jenkins", "email": "sarah.jenkins@centralign.internal", "department": "Engineering", "title": "Senior Software Engineer", "manager_name": "Marcus Vance", "hire_date": "2022-03-15", "salary": 148000.0, "status": "ACTIVE", "leave_balance": 16, "phone": "+1-415-555-0111", "emergency_contact": "Robert Jenkins (Spouse)", "performance_rating": 4.8},
    {"emp_code": "EMP-103", "name": "David Miller", "email": "david.miller@centralign.internal", "department": "Engineering", "title": "Staff Infrastructure Engineer", "manager_name": "Marcus Vance", "hire_date": "2022-11-10", "salary": 155000.0, "status": "ACTIVE", "leave_balance": 18, "phone": "+1-415-555-0113", "emergency_contact": "Clara Miller (Sister)", "performance_rating": 4.7},
    {"emp_code": "EMP-109", "name": "Chloe Martin", "email": "chloe.martin@centralign.internal", "department": "Engineering", "title": "Frontend Developer", "manager_name": "Sarah Jenkins", "hire_date": "2023-04-18", "salary": 115000.0, "status": "ACTIVE", "leave_balance": 15, "phone": "+1-415-555-0119", "emergency_contact": "Luc Martin (Father)", "performance_rating": 4.5},
    {"emp_code": "EMP-113", "name": "Marcus Vance", "email": "marcus.vance@centralign.internal", "department": "Engineering", "title": "VP of Engineering", "manager_name": "CEO", "hire_date": "2021-01-10", "salary": 220000.0, "status": "ACTIVE", "leave_balance": 12, "phone": "+1-415-555-0123", "emergency_contact": "Elena Vance (Sister)", "performance_rating": 4.9},
    {"emp_code": "EMP-114", "name": "Ethan Brooks", "email": "ethan.brooks@centralign.internal", "department": "Engineering", "title": "Principal Distributed Systems Architect", "manager_name": "Marcus Vance", "hire_date": "2021-06-01", "salary": 190000.0, "status": "ACTIVE", "leave_balance": 14, "phone": "+1-415-555-0124", "emergency_contact": "Laura Brooks (Spouse)", "performance_rating": 4.9},
    {"emp_code": "EMP-115", "name": "Zoe Chen", "email": "zoe.chen@centralign.internal", "department": "Engineering", "title": "Senior Backend Go Engineer", "manager_name": "Sarah Jenkins", "hire_date": "2022-08-15", "salary": 142000.0, "status": "ACTIVE", "leave_balance": 19, "phone": "+1-415-555-0125", "emergency_contact": "Kevin Chen (Brother)", "performance_rating": 4.7},
    {"emp_code": "EMP-116", "name": "Lucas Rossi", "email": "lucas.rossi@centralign.internal", "department": "Engineering", "title": "DevOps & Cloud Reliability Engineer", "manager_name": "David Miller", "hire_date": "2023-02-01", "salary": 132000.0, "status": "ACTIVE", "leave_balance": 17, "phone": "+1-415-555-0126", "emergency_contact": "Giulia Rossi (Spouse)", "performance_rating": 4.6},
    {"emp_code": "EMP-117", "name": "Aria Montgomery", "email": "aria.montgomery@centralign.internal", "department": "Engineering", "title": "Senior QA Automation Engineer", "manager_name": "Sarah Jenkins", "hire_date": "2022-10-05", "salary": 128000.0, "status": "ACTIVE", "leave_balance": 20, "phone": "+1-415-555-0127", "emergency_contact": "Byron Montgomery (Father)", "performance_rating": 4.8},
    {"emp_code": "EMP-118", "name": "Devin Kowalski", "email": "devin.kowalski@centralign.internal", "department": "Engineering", "title": "Full Stack Platform Engineer", "manager_name": "Sarah Jenkins", "hire_date": "2023-06-12", "salary": 125000.0, "status": "ACTIVE", "leave_balance": 16, "phone": "+1-415-555-0128", "emergency_contact": "Anna Kowalski (Mother)", "performance_rating": 4.4},
    {"emp_code": "EMP-148", "name": "Nadia Hassan", "email": "nadia.hassan@centralign.internal", "department": "Engineering", "title": "Site Reliability Engineer II", "manager_name": "David Miller", "hire_date": "2023-08-01", "salary": 122000.0, "status": "ACTIVE", "leave_balance": 18, "phone": "+1-415-555-0158", "emergency_contact": "Zayd Hassan (Spouse)", "performance_rating": 4.6},
    {"emp_code": "EMP-149", "name": "Carlos Mendoza", "email": "carlos.mendoza@centralign.internal", "department": "Engineering", "title": "Embedded Systems Engineer", "manager_name": "Ethan Brooks", "hire_date": "2022-12-01", "salary": 138000.0, "status": "ACTIVE", "leave_balance": 15, "phone": "+1-415-555-0159", "emergency_contact": "Maria Mendoza (Mother)", "performance_rating": 4.7},
    {"emp_code": "EMP-150", "name": "Seraphina Lin", "email": "seraphina.lin@centralign.internal", "department": "Engineering", "title": "Security Software Engineer", "manager_name": "Ethan Brooks", "hire_date": "2023-03-20", "salary": 140000.0, "status": "ACTIVE", "leave_balance": 19, "phone": "+1-415-555-0160", "emergency_contact": "George Lin (Father)", "performance_rating": 4.8},

    # IT & Security
    {"emp_code": "EMP-102", "name": "Alex Wong", "email": "alex.wong@centralign.internal", "department": "IT & Security", "title": "Lead Systems Architect", "manager_name": "Marcus Vance", "hire_date": "2021-08-01", "salary": 162000.0, "status": "ACTIVE", "leave_balance": 14, "phone": "+1-415-555-0112", "emergency_contact": "Mei Wong (Mother)", "performance_rating": 4.9},
    {"emp_code": "EMP-110", "name": "Liam O'Connor", "email": "liam.oconnor@centralign.internal", "department": "IT & Security", "title": "Security Operations Analyst", "manager_name": "Alex Wong", "hire_date": "2023-09-01", "salary": 105000.0, "status": "ACTIVE", "leave_balance": 20, "phone": "+1-415-555-0120", "emergency_contact": "Sean O'Connor (Brother)", "performance_rating": 4.6},
    {"emp_code": "EMP-119", "name": "Rajiv Sharma", "email": "rajiv.sharma@centralign.internal", "department": "IT & Security", "title": "Senior Network Security Engineer", "manager_name": "Alex Wong", "hire_date": "2022-05-18", "salary": 145000.0, "status": "ACTIVE", "leave_balance": 15, "phone": "+1-415-555-0129", "emergency_contact": "Pooja Sharma (Spouse)", "performance_rating": 4.8},
    {"emp_code": "EMP-120", "name": "Hanna Lindqvist", "email": "hanna.lindqvist@centralign.internal", "department": "IT & Security", "title": "IT Desktop Support Lead", "manager_name": "Alex Wong", "hire_date": "2022-11-20", "salary": 98000.0, "status": "ACTIVE", "leave_balance": 18, "phone": "+1-415-555-0130", "emergency_contact": "Erik Lindqvist (Father)", "performance_rating": 4.7},
    {"emp_code": "EMP-121", "name": "Tariq Mansoor", "email": "tariq.mansoor@centralign.internal", "department": "IT & Security", "title": "IAM & Cloud Identity Specialist", "manager_name": "Alex Wong", "hire_date": "2023-03-10", "salary": 138000.0, "status": "ACTIVE", "leave_balance": 16, "phone": "+1-415-555-0131", "emergency_contact": "Fatima Mansoor (Spouse)", "performance_rating": 4.6},
    {"emp_code": "EMP-151", "name": "Arthur Pendelton", "email": "arthur.pendelton@centralign.internal", "department": "IT & Security", "title": "IT Helpdesk Specialist", "manager_name": "Hanna Lindqvist", "hire_date": "2023-10-01", "salary": 78000.0, "status": "ACTIVE", "leave_balance": 19, "phone": "+1-415-555-0161", "emergency_contact": "Martha Pendelton (Spouse)", "performance_rating": 4.4},

    # Sales & Revenue
    {"emp_code": "EMP-106", "name": "Jessica Alba-Ruiz", "email": "jessica.alba@centralign.internal", "department": "Sales & Revenue", "title": "VP of Worldwide Sales", "manager_name": "CEO", "hire_date": "2021-05-12", "salary": 185000.0, "status": "ACTIVE", "leave_balance": 15, "phone": "+1-415-555-0116", "emergency_contact": "Carlos Ruiz (Spouse)", "performance_rating": 4.8},
    {"emp_code": "EMP-111", "name": "Maya Lin", "email": "maya.lin@centralign.internal", "department": "Sales & Revenue", "title": "Senior Enterprise Account Exec", "manager_name": "Jessica Alba-Ruiz", "hire_date": "2022-09-15", "salary": 135000.0, "status": "ACTIVE", "leave_balance": 14, "phone": "+1-415-555-0121", "emergency_contact": "Wei Lin (Father)", "performance_rating": 4.9},
    {"emp_code": "EMP-122", "name": "Christian Cole", "email": "christian.cole@centralign.internal", "department": "Sales & Revenue", "title": "Strategic Enterprise Sales Director", "manager_name": "Jessica Alba-Ruiz", "hire_date": "2021-10-01", "salary": 165000.0, "status": "ACTIVE", "leave_balance": 11, "phone": "+1-415-555-0132", "emergency_contact": "Diana Cole (Spouse)", "performance_rating": 4.8},
    {"emp_code": "EMP-123", "name": "Sofia Reyes", "email": "sofia.reyes@centralign.internal", "department": "Sales & Revenue", "title": "Mid-Market Account Executive", "manager_name": "Christian Cole", "hire_date": "2023-01-15", "salary": 110000.0, "status": "ACTIVE", "leave_balance": 17, "phone": "+1-415-555-0133", "emergency_contact": "Manuel Reyes (Brother)", "performance_rating": 4.5},
    {"emp_code": "EMP-124", "name": "Brett Henderson", "email": "brett.henderson@centralign.internal", "department": "Sales & Revenue", "title": "Sales Development Representative Lead", "manager_name": "Jessica Alba-Ruiz", "hire_date": "2023-05-01", "salary": 85000.0, "status": "ACTIVE", "leave_balance": 19, "phone": "+1-415-555-0134", "emergency_contact": "Kelly Henderson (Spouse)", "performance_rating": 4.4},
    {"emp_code": "EMP-152", "name": "Daphne Blake", "email": "daphne.blake@centralign.internal", "department": "Sales & Revenue", "title": "Senior Solutions Engineer", "manager_name": "Christian Cole", "hire_date": "2022-07-01", "salary": 145000.0, "status": "ACTIVE", "leave_balance": 16, "phone": "+1-415-555-0162", "emergency_contact": "Fred Blake (Brother)", "performance_rating": 4.8},

    # Marketing & Growth
    {"emp_code": "EMP-107", "name": "David Sterling", "email": "david.sterling@centralign.internal", "department": "Marketing & Growth", "title": "Director of Product Marketing", "manager_name": "CEO", "hire_date": "2023-01-09", "salary": 140000.0, "status": "ACTIVE", "leave_balance": 17, "phone": "+1-415-555-0117", "emergency_contact": "Alice Sterling (Spouse)", "performance_rating": 4.6},
    {"emp_code": "EMP-125", "name": "Natalie Foster", "email": "natalie.foster@centralign.internal", "department": "Marketing & Growth", "title": "Head of Demand Generation", "manager_name": "David Sterling", "hire_date": "2022-04-10", "salary": 130000.0, "status": "ACTIVE", "leave_balance": 15, "phone": "+1-415-555-0135", "emergency_contact": "George Foster (Father)", "performance_rating": 4.7},
    {"emp_code": "EMP-126", "name": "Jordan Rivera", "email": "jordan.rivera@centralign.internal", "department": "Marketing & Growth", "title": "Senior Content & Brand Strategist", "manager_name": "David Sterling", "hire_date": "2022-09-01", "salary": 105000.0, "status": "ACTIVE", "leave_balance": 16, "phone": "+1-415-555-0136", "emergency_contact": "Carmen Rivera (Mother)", "performance_rating": 4.6},
    {"emp_code": "EMP-127", "name": "Kimberly Park", "email": "kimberly.park@centralign.internal", "department": "Marketing & Growth", "title": "Performance Marketing Analyst", "manager_name": "Natalie Foster", "hire_date": "2023-07-15", "salary": 92000.0, "status": "ACTIVE", "leave_balance": 18, "phone": "+1-415-555-0137", "emergency_contact": "Joon Park (Brother)", "performance_rating": 4.5},
    {"emp_code": "EMP-153", "name": "Zachary Vance", "email": "zachary.vance@centralign.internal", "department": "Marketing & Growth", "title": "Digital Growth Marketing Manager", "manager_name": "Natalie Foster", "hire_date": "2022-11-15", "salary": 115000.0, "status": "ACTIVE", "leave_balance": 14, "phone": "+1-415-555-0163", "emergency_contact": "Chloe Vance (Spouse)", "performance_rating": 4.7},

    # Human Resources
    {"emp_code": "EMP-104", "name": "Elena Vance", "email": "elena.vance@centralign.internal", "department": "Human Resources", "title": "VP of People & Culture", "manager_name": "CEO", "hire_date": "2021-02-01", "salary": 175000.0, "status": "ACTIVE", "leave_balance": 12, "phone": "+1-415-555-0114", "emergency_contact": "Marcus Vance (Brother)", "performance_rating": 5.0},
    {"emp_code": "EMP-128", "name": "Claire Dupont", "email": "claire.dupont@centralign.internal", "department": "Human Resources", "title": "Senior HR Business Partner", "manager_name": "Elena Vance", "hire_date": "2022-02-15", "salary": 118000.0, "status": "ACTIVE", "leave_balance": 16, "phone": "+1-415-555-0138", "emergency_contact": "Jean Dupont (Father)", "performance_rating": 4.8},
    {"emp_code": "EMP-129", "name": "Trevor Walsh", "email": "trevor.walsh@centralign.internal", "department": "Human Resources", "title": "Lead Technical Recruiter", "manager_name": "Elena Vance", "hire_date": "2022-06-01", "salary": 112000.0, "status": "ACTIVE", "leave_balance": 14, "phone": "+1-415-555-0139", "emergency_contact": "Grace Walsh (Spouse)", "performance_rating": 4.7},
    {"emp_code": "EMP-130", "name": "Meera Joshi", "email": "meera.joshi@centralign.internal", "department": "Human Resources", "title": "People Operations Coordinator", "manager_name": "Claire Dupont", "hire_date": "2023-04-01", "salary": 78000.0, "status": "ACTIVE", "leave_balance": 20, "phone": "+1-415-555-0140", "emergency_contact": "Sanjay Joshi (Father)", "performance_rating": 4.6},
    {"emp_code": "EMP-154", "name": "Harrison Wells", "email": "harrison.wells@centralign.internal", "department": "Human Resources", "title": "Compensation & Benefits Analyst", "manager_name": "Elena Vance", "hire_date": "2022-09-01", "salary": 105000.0, "status": "ACTIVE", "leave_balance": 17, "phone": "+1-415-555-0164", "emergency_contact": "Nora Wells (Daughter)", "performance_rating": 4.6},

    # Finance & Legal
    {"emp_code": "EMP-105", "name": "Marcus Thorne", "email": "marcus.thorne@centralign.internal", "department": "Finance & Legal", "title": "Chief Financial Officer", "manager_name": "CEO", "hire_date": "2021-01-15", "salary": 210000.0, "status": "ACTIVE", "leave_balance": 10, "phone": "+1-415-555-0115", "emergency_contact": "Victoria Thorne (Spouse)", "performance_rating": 5.0},
    {"emp_code": "EMP-112", "name": "Thomas Becker", "email": "thomas.becker@centralign.internal", "department": "Finance & Legal", "title": "Senior Corporate Accountant", "manager_name": "Marcus Thorne", "hire_date": "2022-02-14", "salary": 112000.0, "status": "ACTIVE", "leave_balance": 13, "phone": "+1-415-555-0122", "emergency_contact": "Greta Becker (Spouse)", "performance_rating": 4.7},
    {"emp_code": "EMP-131", "name": "Samantha Wu", "email": "samantha.wu@centralign.internal", "department": "Finance & Legal", "title": "Senior Legal Counsel & Compliance Lead", "manager_name": "Marcus Thorne", "hire_date": "2021-09-01", "salary": 172000.0, "status": "ACTIVE", "leave_balance": 15, "phone": "+1-415-555-0141", "emergency_contact": "Patrick Wu (Spouse)", "performance_rating": 4.9},
    {"emp_code": "EMP-132", "name": "Jonathan Price", "email": "jonathan.price@centralign.internal", "department": "Finance & Legal", "title": "Financial Planning & Analysis Manager", "manager_name": "Marcus Thorne", "hire_date": "2022-05-01", "salary": 135000.0, "status": "ACTIVE", "leave_balance": 14, "phone": "+1-415-555-0142", "emergency_contact": "Rachel Price (Spouse)", "performance_rating": 4.7},
    {"emp_code": "EMP-133", "name": "Ananya Roy", "email": "ananya.roy@centralign.internal", "department": "Finance & Legal", "title": "Accounts Payable Specialist", "manager_name": "Thomas Becker", "hire_date": "2023-03-15", "salary": 82000.0, "status": "ACTIVE", "leave_balance": 19, "phone": "+1-415-555-0143", "emergency_contact": "Vikram Roy (Brother)", "performance_rating": 4.5},
    {"emp_code": "EMP-155", "name": "Gregory House", "email": "gregory.house@centralign.internal", "department": "Finance & Legal", "title": "Senior Forensic & Tax Auditor", "manager_name": "Marcus Thorne", "hire_date": "2022-03-10", "salary": 142000.0, "status": "ACTIVE", "leave_balance": 12, "phone": "+1-415-555-0165", "emergency_contact": "James Wilson (Friend)", "performance_rating": 4.8},

    # Customer Success
    {"emp_code": "EMP-108", "name": "Amina Patel", "email": "amina.patel@centralign.internal", "department": "Customer Success", "title": "Director of Customer Success", "manager_name": "CEO", "hire_date": "2022-06-20", "salary": 138000.0, "status": "ACTIVE", "leave_balance": 19, "phone": "+1-415-555-0118", "emergency_contact": "Tariq Patel (Brother)", "performance_rating": 4.7},
    {"emp_code": "EMP-134", "name": "Lucas Meyer", "email": "lucas.meyer@centralign.internal", "department": "Customer Success", "title": "Principal Technical Account Manager", "manager_name": "Amina Patel", "hire_date": "2022-03-01", "salary": 128000.0, "status": "ACTIVE", "leave_balance": 16, "phone": "+1-415-555-0144", "emergency_contact": "Leonie Meyer (Spouse)", "performance_rating": 4.8},
    {"emp_code": "EMP-135", "name": "Olivia Taylor", "email": "olivia.taylor@centralign.internal", "department": "Customer Success", "title": "Senior Customer Success Manager", "manager_name": "Amina Patel", "hire_date": "2022-10-15", "salary": 115000.0, "status": "ACTIVE", "leave_balance": 18, "phone": "+1-415-555-0145", "emergency_contact": "James Taylor (Spouse)", "performance_rating": 4.6},
    {"emp_code": "EMP-136", "name": "Daniel Kim", "email": "daniel.kim@centralign.internal", "department": "Customer Success", "title": "Customer Onboarding Specialist", "manager_name": "Amina Patel", "hire_date": "2023-05-10", "salary": 90000.0, "status": "ACTIVE", "leave_balance": 17, "phone": "+1-415-555-0146", "emergency_contact": "Grace Kim (Mother)", "performance_rating": 4.5},
    {"emp_code": "EMP-156", "name": "Fiona Gallagher", "email": "fiona.gallagher@centralign.internal", "department": "Customer Success", "title": "Enterprise Escalation Manager", "manager_name": "Amina Patel", "hire_date": "2022-08-01", "salary": 120000.0, "status": "ACTIVE", "leave_balance": 15, "phone": "+1-415-555-0166", "emergency_contact": "Ian Gallagher (Brother)", "performance_rating": 4.7},

    # Product & Design
    {"emp_code": "EMP-137", "name": "Samantha Reed", "email": "samantha.reed@centralign.internal", "department": "Product & Design", "title": "VP of Product Management", "manager_name": "CEO", "hire_date": "2021-04-01", "salary": 188000.0, "status": "ACTIVE", "leave_balance": 13, "phone": "+1-415-555-0147", "emergency_contact": "Tom Reed (Spouse)", "performance_rating": 4.9},
    {"emp_code": "EMP-138", "name": "Felix Baum", "email": "felix.baum@centralign.internal", "department": "Product & Design", "title": "Principal Product Designer", "manager_name": "Samantha Reed", "hire_date": "2022-01-10", "salary": 145000.0, "status": "ACTIVE", "leave_balance": 15, "phone": "+1-415-555-0148", "emergency_contact": "Heidi Baum (Sister)", "performance_rating": 4.8},
    {"emp_code": "EMP-139", "name": "Kavita Rao", "email": "kavita.rao@centralign.internal", "department": "Product & Design", "title": "Senior Technical Product Manager", "manager_name": "Samantha Reed", "hire_date": "2022-07-20", "salary": 140000.0, "status": "ACTIVE", "leave_balance": 17, "phone": "+1-415-555-0149", "emergency_contact": "Arun Rao (Spouse)", "performance_rating": 4.7},
    {"emp_code": "EMP-140", "name": "Liam Gallagher", "email": "liam.gallagher@centralign.internal", "department": "Product & Design", "title": "UI/UX Interaction Designer", "manager_name": "Felix Baum", "hire_date": "2023-02-15", "salary": 110000.0, "status": "ACTIVE", "leave_balance": 18, "phone": "+1-415-555-0150", "emergency_contact": "Noel Gallagher (Brother)", "performance_rating": 4.4},
    {"emp_code": "EMP-157", "name": "Penelope Cruz-Miller", "email": "penelope.cruz@centralign.internal", "department": "Product & Design", "title": "Design Systems Lead", "manager_name": "Felix Baum", "hire_date": "2022-05-15", "salary": 135000.0, "status": "ACTIVE", "leave_balance": 16, "phone": "+1-415-555-0167", "emergency_contact": "Javier Miller (Spouse)", "performance_rating": 4.8},

    # Operations & Facilities
    {"emp_code": "EMP-141", "name": "Raymond Cruz", "email": "raymond.cruz@centralign.internal", "department": "Operations & Facilities", "title": "Director of Workplace & Facilities", "manager_name": "CEO", "hire_date": "2021-07-01", "salary": 135000.0, "status": "ACTIVE", "leave_balance": 15, "phone": "+1-415-555-0151", "emergency_contact": "Luisa Cruz (Spouse)", "performance_rating": 4.7},
    {"emp_code": "EMP-142", "name": "Brooke Sullivan", "email": "brooke.sullivan@centralign.internal", "department": "Operations & Facilities", "title": "Procurement & Vendor Operations Lead", "manager_name": "Raymond Cruz", "hire_date": "2022-04-01", "salary": 110000.0, "status": "ACTIVE", "leave_balance": 16, "phone": "+1-415-555-0152", "emergency_contact": "Neil Sullivan (Spouse)", "performance_rating": 4.8},
    {"emp_code": "EMP-143", "name": "Mateo Morales", "email": "mateo.morales@centralign.internal", "department": "Operations & Facilities", "title": "Logistics & Inventory Supervisor", "manager_name": "Brooke Sullivan", "hire_date": "2023-01-20", "salary": 88000.0, "status": "ACTIVE", "leave_balance": 19, "phone": "+1-415-555-0153", "emergency_contact": "Sofia Morales (Sister)", "performance_rating": 4.6},
    {"emp_code": "EMP-158", "name": "Winston Bishop", "email": "winston.bishop@centralign.internal", "department": "Operations & Facilities", "title": "Facilities Safety & Security Officer", "manager_name": "Raymond Cruz", "hire_date": "2023-04-10", "salary": 84000.0, "status": "ACTIVE", "leave_balance": 17, "phone": "+1-415-555-0168", "emergency_contact": "Aly Bishop (Spouse)", "performance_rating": 4.6},

    # Data & AI Research
    {"emp_code": "EMP-144", "name": "Dr. Aris Thorne", "email": "aris.thorne@centralign.internal", "department": "Data & AI Research", "title": "Chief AI Scientist", "manager_name": "CEO", "hire_date": "2021-03-01", "salary": 230000.0, "status": "ACTIVE", "leave_balance": 12, "phone": "+1-415-555-0154", "emergency_contact": "Eleni Thorne (Spouse)", "performance_rating": 5.0},
    {"emp_code": "EMP-145", "name": "Priya Sharma", "email": "priya.sharma@centralign.internal", "department": "Data & AI Research", "title": "Senior Machine Learning Engineer", "manager_name": "Dr. Aris Thorne", "hire_date": "2022-05-15", "salary": 165000.0, "status": "ACTIVE", "leave_balance": 17, "phone": "+1-415-555-0155", "emergency_contact": "Rohan Sharma (Brother)", "performance_rating": 4.9},
    {"emp_code": "EMP-146", "name": "Dmitri Volkov", "email": "dmitri.volkov@centralign.internal", "department": "Data & AI Research", "title": "Lead NLP & LLM Systems Engineer", "manager_name": "Dr. Aris Thorne", "hire_date": "2022-09-01", "salary": 168000.0, "status": "ACTIVE", "leave_balance": 15, "phone": "+1-415-555-0156", "emergency_contact": "Olga Volkova (Spouse)", "performance_rating": 4.8},
    {"emp_code": "EMP-147", "name": "Selena Gomez-Tan", "email": "selena.tan@centralign.internal", "department": "Data & AI Research", "title": "Data Infrastructure & MLOps Architect", "manager_name": "Dr. Aris Thorne", "hire_date": "2023-02-01", "salary": 152000.0, "status": "ACTIVE", "leave_balance": 18, "phone": "+1-415-555-0157", "emergency_contact": "Marcus Tan (Spouse)", "performance_rating": 4.7},
    {"emp_code": "EMP-159", "name": "Turing Vance", "email": "turing.vance@centralign.internal", "department": "Data & AI Research", "title": "AI Research Scientist - Agentic Cognition", "manager_name": "Dr. Aris Thorne", "hire_date": "2023-06-01", "salary": 178000.0, "status": "ACTIVE", "leave_balance": 16, "phone": "+1-415-555-0169", "emergency_contact": "Ada Vance (Sister)", "performance_rating": 5.0},
    {"emp_code": "EMP-160", "name": "Hannah Abbott", "email": "hannah.abbott@centralign.internal", "department": "Data & AI Research", "title": "Data Labeling & Annotation Lead", "manager_name": "Priya Sharma", "hire_date": "2023-09-15", "salary": 96000.0, "status": "ACTIVE", "leave_balance": 19, "phone": "+1-415-555-0170", "emergency_contact": "Neville Abbott (Spouse)", "performance_rating": 4.5},
]

# -------------------------------------------------------------
# 3. LEAVE REQUESTS DATA (25 Leave Requests)
# -------------------------------------------------------------
LEAVE_REQUESTS_DATA = [
    {"req_code": "LV-2026-001", "emp_name": "Sarah Jenkins", "leave_type": "Annual Vacation", "start_date": "2026-11-20", "end_date": "2026-11-25", "days_requested": 4, "reason": "Family holiday trip to Japan", "status": "PENDING", "approver_notes": None, "created_at": "2026-10-04 09:30:00"},
    {"req_code": "LV-2026-002", "emp_name": "Chloe Martin", "leave_type": "Sick Leave", "start_date": "2026-09-12", "end_date": "2026-09-13", "days_requested": 2, "reason": "Mild seasonal flu recovery", "status": "APPROVED", "approver_notes": "Approved by Sarah Jenkins", "created_at": "2026-09-11 18:00:00"},
    {"req_code": "LV-2026-003", "emp_name": "David Miller", "leave_type": "Annual Vacation", "start_date": "2026-12-24", "end_date": "2026-12-31", "days_requested": 5, "reason": "Christmas & New Year break with parents", "status": "PENDING", "approver_notes": None, "created_at": "2026-10-02 14:15:00"},
    {"req_code": "LV-2026-004", "emp_name": "Maya Lin", "leave_type": "Personal Leave", "start_date": "2026-10-18", "end_date": "2026-10-19", "days_requested": 2, "reason": "Attending sibling graduation ceremony", "status": "APPROVED", "approver_notes": "Approved by Jessica Alba-Ruiz", "created_at": "2026-10-01 11:20:00"},
    {"req_code": "LV-2026-005", "emp_name": "Alex Wong", "leave_type": "Annual Vacation", "start_date": "2026-11-05", "end_date": "2026-11-09", "days_requested": 3, "reason": "Long weekend camping trip", "status": "PENDING", "approver_notes": None, "created_at": "2026-10-05 10:00:00"},
    {"req_code": "LV-2026-006", "emp_name": "Liam O'Connor", "leave_type": "Sick Leave", "start_date": "2026-09-20", "end_date": "2026-09-21", "days_requested": 1, "reason": "Dental surgery and recovery", "status": "APPROVED", "approver_notes": "Approved by Alex Wong", "created_at": "2026-09-19 16:30:00"},
    {"req_code": "LV-2026-007", "emp_name": "Thomas Becker", "leave_type": "Annual Vacation", "start_date": "2026-10-25", "end_date": "2026-10-29", "days_requested": 3, "reason": "Family anniversary trip", "status": "PENDING", "approver_notes": None, "created_at": "2026-10-03 15:45:00"},
    {"req_code": "LV-2026-008", "emp_name": "Zoe Chen", "leave_type": "Personal Leave", "start_date": "2026-11-12", "end_date": "2026-11-13", "days_requested": 2, "reason": "Home relocation & moving days", "status": "PENDING", "approver_notes": None, "created_at": "2026-10-06 08:30:00"},
    {"req_code": "LV-2026-009", "emp_name": "Lucas Rossi", "leave_type": "Annual Vacation", "start_date": "2026-12-15", "end_date": "2026-12-22", "days_requested": 6, "reason": "Winter ski trip in Dolomites", "status": "PENDING", "approver_notes": None, "created_at": "2026-10-04 11:15:00"},
    {"req_code": "LV-2026-010", "emp_name": "Priya Sharma", "leave_type": "Professional Development", "start_date": "2026-11-02", "end_date": "2026-11-04", "days_requested": 3, "reason": "Attending NeurIPS AI conference in Vancouver", "status": "APPROVED", "approver_notes": "Approved by Dr. Aris Thorne", "created_at": "2026-09-28 14:00:00"},
    {"req_code": "LV-2026-011", "emp_name": "Brett Henderson", "leave_type": "Sick Leave", "start_date": "2026-10-02", "end_date": "2026-10-03", "days_requested": 2, "reason": "Migraine and doctor appointment", "status": "APPROVED", "approver_notes": "Approved by Jessica Alba-Ruiz", "created_at": "2026-10-01 18:20:00"},
    {"req_code": "LV-2026-012", "emp_name": "Felix Baum", "leave_type": "Annual Vacation", "start_date": "2026-11-16", "end_date": "2026-11-20", "days_requested": 5, "reason": "Autumn countryside wellness retreat", "status": "PENDING", "approver_notes": None, "created_at": "2026-10-05 13:40:00"},
    {"req_code": "LV-2026-013", "emp_name": "Nadia Hassan", "leave_type": "Personal Leave", "start_date": "2026-10-22", "end_date": "2026-10-23", "days_requested": 2, "reason": "Family wedding celebration", "status": "PENDING", "approver_notes": None, "created_at": "2026-10-06 14:00:00"},
    {"req_code": "LV-2026-014", "emp_name": "Carlos Mendoza", "leave_type": "Annual Vacation", "start_date": "2026-12-20", "end_date": "2026-12-28", "days_requested": 6, "reason": "Holiday vacation visiting family in Spain", "status": "PENDING", "approver_notes": None, "created_at": "2026-10-05 16:30:00"},
    {"req_code": "LV-2026-015", "emp_name": "Daphne Blake", "leave_type": "Annual Vacation", "start_date": "2026-11-25", "end_date": "2026-11-28", "days_requested": 3, "reason": "Thanksgiving holiday trip", "status": "PENDING", "approver_notes": None, "created_at": "2026-10-06 11:15:00"},
    {"req_code": "LV-2026-016", "emp_name": "Gregory House", "leave_type": "Medical Leave", "start_date": "2026-10-14", "end_date": "2026-10-16", "days_requested": 3, "reason": "Specialist medical consult and rest", "status": "APPROVED", "approver_notes": "Approved by Marcus Thorne", "created_at": "2026-10-04 17:00:00"},
    {"req_code": "LV-2026-017", "emp_name": "Olivia Taylor", "leave_type": "Parental Leave", "start_date": "2026-11-01", "end_date": "2026-11-15", "days_requested": 10, "reason": "Secondary caregiver parental bonding leave", "status": "APPROVED", "approver_notes": "Approved by Elena Vance", "created_at": "2026-09-25 10:30:00"},
    {"req_code": "LV-2026-018", "emp_name": "Winston Bishop", "leave_type": "Annual Vacation", "start_date": "2026-10-30", "end_date": "2026-11-03", "days_requested": 3, "reason": "Short fall road trip", "status": "PENDING", "approver_notes": None, "created_at": "2026-10-06 09:45:00"},
    {"req_code": "LV-2026-019", "emp_name": "Turing Vance", "leave_type": "Professional Development", "start_date": "2026-12-08", "end_date": "2026-12-12", "days_requested": 4, "reason": "Presenting research paper at Agentic Systems Summit", "status": "APPROVED", "approver_notes": "Approved by Dr. Aris Thorne", "created_at": "2026-10-01 15:20:00"},
    {"req_code": "LV-2026-020", "emp_name": "Hannah Abbott", "leave_type": "Sick Leave", "start_date": "2026-10-05", "end_date": "2026-10-06", "days_requested": 2, "reason": "Food poisoning recovery", "status": "APPROVED", "approver_notes": "Approved by Priya Sharma", "created_at": "2026-10-04 20:00:00"},
]

# -------------------------------------------------------------
# 4. INVOICES DATA (55+ Commercial Invoices in ONE Master Table)
# -------------------------------------------------------------
INVOICES_DATA = [
    # Key test invoices
    {"invoice_number": "INV-CX-2026-904", "vendor_name": "Company X", "invoice_type": "PAYABLE", "amount": 4850.00, "currency": "USD", "due_date": "2026-11-15", "status": "PENDING_APPROVAL", "notes": "Enterprise SaaS Platform License & Premium SLA (Oct 2026)", "created_at": "2026-10-01 08:00:00"},
    {"invoice_number": "INV-CX-2026-102", "vendor_name": "Company X", "invoice_type": "PAYABLE", "amount": 1200.00, "currency": "USD", "due_date": "2026-05-25", "status": "PAID", "notes": "Initial System Architecture Onboarding Consulting", "created_at": "2026-04-10 09:30:00"},
    {"invoice_number": "INV-CY-2026-440", "vendor_name": "Company Y", "invoice_type": "PAYABLE", "amount": 2890.50, "currency": "USD", "due_date": "2026-10-30", "status": "APPROVED", "notes": "Secure Cold Storage Facility Lease & Logistics", "created_at": "2026-09-18 14:15:00"},
    {"invoice_number": "INV-ACME-2026-881", "vendor_name": "Acme Supplies Co", "invoice_type": "PAYABLE", "amount": 1650.00, "currency": "USD", "due_date": "2026-10-25", "status": "APPROVED", "notes": "Ergonomic mesh chairs and monitor arms for Engineering floor", "created_at": "2026-09-25 11:20:00"},
    {"invoice_number": "INV-GCH-2026-512", "vendor_name": "Global Cloud Hosting", "invoice_type": "PAYABLE", "amount": 2150.00, "currency": "USD", "due_date": "2026-11-02", "status": "APPROVED", "notes": "High-Memory Kubernetes Compute Cluster & Anycast CDN", "created_at": "2026-10-02 10:00:00"},

    # Standard Payables
    {"invoice_number": "INV-2026-001", "vendor_name": "Acme Supplies Co", "invoice_type": "PAYABLE", "amount": 1450.50, "currency": "USD", "due_date": "2026-10-15", "status": "APPROVED", "notes": "Monthly office consumables & paper", "created_at": "2026-09-15 10:30:00"},
    {"invoice_number": "INV-2026-002", "vendor_name": "Global Cloud Hosting", "invoice_type": "PAYABLE", "amount": 820.00, "currency": "USD", "due_date": "2026-10-20", "status": "PAID", "notes": "Dedicated server cluster renewal", "created_at": "2026-09-20 14:15:00"},
    {"invoice_number": "INV-2026-003", "vendor_name": "Apex Logistics Ltd", "invoice_type": "PAYABLE", "amount": 3120.00, "currency": "USD", "due_date": "2026-11-01", "status": "PENDING_APPROVAL", "notes": "Q3 Freight & customs charges", "created_at": "2026-09-28 09:00:00"},
    {"invoice_number": "INV-2026-004", "vendor_name": "CloudScale Networks", "invoice_type": "PAYABLE", "amount": 2400.00, "currency": "USD", "due_date": "2026-10-28", "status": "APPROVED", "notes": "Enterprise SD-WAN interconnects", "created_at": "2026-09-30 11:45:00"},
    {"invoice_number": "INV-2026-005", "vendor_name": "CyberShield Security LLC", "invoice_type": "PAYABLE", "amount": 7000.00, "currency": "USD", "due_date": "2026-11-10", "status": "PENDING_APPROVAL", "notes": "Monthly SOC 24/7 SIEM monitoring retainer", "created_at": "2026-10-01 08:30:00"},
    {"invoice_number": "INV-2026-006", "vendor_name": "OfficeMax Pro", "invoice_type": "PAYABLE", "amount": 530.25, "currency": "USD", "due_date": "2026-10-25", "status": "PAID", "notes": "Breakroom coffee and pantry stocking", "created_at": "2026-09-22 13:00:00"},

    # Large Infrastructure & Vendor Payables
    {"invoice_number": "INV-AWS-2026-101", "vendor_name": "Amazon Web Services (AWS)", "invoice_type": "PAYABLE", "amount": 14250.00, "currency": "USD", "due_date": "2026-10-31", "status": "APPROVED", "notes": "Production us-east-1 and eu-west-1 cloud compute & Aurora RDS", "created_at": "2026-10-01 00:05:00"},
    {"invoice_number": "INV-DD-2026-402", "vendor_name": "Datadog Observability", "invoice_type": "PAYABLE", "amount": 3850.00, "currency": "USD", "due_date": "2026-11-05", "status": "PENDING_APPROVAL", "notes": "APM and distributed tracing agent telemetry tier", "created_at": "2026-10-02 09:10:00"},
    {"invoice_number": "INV-GH-2026-781", "vendor_name": "GitHub Enterprise", "invoice_type": "PAYABLE", "amount": 2800.00, "currency": "USD", "due_date": "2026-10-28", "status": "PAID", "notes": "120 developer seats + Copilot Enterprise add-on Q3", "created_at": "2026-09-28 15:30:00"},
    {"invoice_number": "INV-SLK-2026-099", "vendor_name": "Slack Technologies / Salesforce", "invoice_type": "PAYABLE", "amount": 3150.00, "currency": "USD", "due_date": "2026-11-04", "status": "APPROVED", "notes": "Enterprise Grid workspace licensing and DLP retention", "created_at": "2026-10-03 10:20:00"},
    {"invoice_number": "INV-SNOW-2026-311", "vendor_name": "Snowflake Inc.", "invoice_type": "PAYABLE", "amount": 8900.00, "currency": "USD", "due_date": "2026-11-12", "status": "PENDING_APPROVAL", "notes": "Analytics data warehouse credit consumption for September", "created_at": "2026-10-01 12:00:00"},
    {"invoice_number": "INV-ZM-2026-880", "vendor_name": "Zoom Video Communications", "invoice_type": "PAYABLE", "amount": 1420.00, "currency": "USD", "due_date": "2026-10-22", "status": "PAID", "notes": "Corporate Zoom One Business licenses & Zoom Rooms audio", "created_at": "2026-09-22 09:40:00"},
    {"invoice_number": "INV-TWLO-2026-441", "vendor_name": "Twilio Telephony", "invoice_type": "PAYABLE", "amount": 850.00, "currency": "USD", "due_date": "2026-11-01", "status": "APPROVED", "notes": "Customer SMS 2FA notification dispatch and voice SIP trunks", "created_at": "2026-10-01 16:15:00"},
    {"invoice_number": "INV-GCP-2026-620", "vendor_name": "Google Cloud Platform", "invoice_type": "PAYABLE", "amount": 16400.00, "currency": "USD", "due_date": "2026-11-18", "status": "PENDING_APPROVAL", "notes": "TPU v5e AI training pods & BigQuery storage tier", "created_at": "2026-10-02 08:30:00"},
    {"invoice_number": "INV-CSCO-2026-512", "vendor_name": "Cisco Systems Commercial", "invoice_type": "PAYABLE", "amount": 5400.00, "currency": "USD", "due_date": "2026-11-14", "status": "APPROVED", "notes": "SmartNet maintenance contract for San Francisco HQ edge switches", "created_at": "2026-09-30 14:00:00"},
    {"invoice_number": "INV-PAN-2026-901", "vendor_name": "Palo Alto Networks", "invoice_type": "PAYABLE", "amount": 6800.00, "currency": "USD", "due_date": "2026-11-20", "status": "PENDING_APPROVAL", "notes": "Prisma Access zero-trust cloud firewall subscriptions", "created_at": "2026-10-03 11:30:00"},
    {"invoice_number": "INV-WW-2026-204", "vendor_name": "WeWork Global Enterprise", "invoice_type": "PAYABLE", "amount": 6500.00, "currency": "USD", "due_date": "2026-10-31", "status": "PAID", "notes": "New York and London satellite team touchdown office desks", "created_at": "2026-09-25 10:00:00"},
    {"invoice_number": "INV-KPMG-2026-701", "vendor_name": "KPMG Audit & Advisory LLP", "invoice_type": "PAYABLE", "amount": 28500.00, "currency": "USD", "due_date": "2026-11-30", "status": "PENDING_APPROVAL", "notes": "Interim SOC-2 Type II independent certification audit retainer", "created_at": "2026-10-01 17:00:00"},
    {"invoice_number": "INV-CLY-2026-810", "vendor_name": "Cooley LLP Corporate Counsel", "invoice_type": "PAYABLE", "amount": 18200.00, "currency": "USD", "due_date": "2026-11-25", "status": "PENDING_APPROVAL", "notes": "Q3 IP patent filing and enterprise SaaS customer terms advisory", "created_at": "2026-10-02 15:45:00"},
    {"invoice_number": "INV-DELL-2026-309", "vendor_name": "Dell Enterprise Store", "invoice_type": "PAYABLE", "amount": 7250.00, "currency": "USD", "due_date": "2026-11-10", "status": "APPROVED", "notes": "Batch of 4x Dell XPS 15 developer laptops and Thunderbolt docks", "created_at": "2026-09-28 13:15:00"},
    {"invoice_number": "INV-APPL-2026-411", "vendor_name": "Apple Commercial Direct", "invoice_type": "PAYABLE", "amount": 11495.00, "currency": "USD", "due_date": "2026-11-15", "status": "PENDING_APPROVAL", "notes": "5x MacBook Pro 16 M3 Pro 36GB for Data Science team", "created_at": "2026-10-04 10:30:00"},
    {"invoice_number": "INV-FDX-2026-112", "vendor_name": "FedEx Corporate Logistics", "invoice_type": "PAYABLE", "amount": 420.50, "currency": "USD", "due_date": "2026-10-20", "status": "PAID", "notes": "Expedited courier shipping for international employee onboarding kits", "created_at": "2026-09-20 16:00:00"},
    {"invoice_number": "INV-STR-2026-801", "vendor_name": "Stripe Payments Inc.", "invoice_type": "PAYABLE", "amount": 1840.00, "currency": "USD", "due_date": "2026-10-18", "status": "PAID", "notes": "Monthly billing merchant processing and interchange fees", "created_at": "2026-09-18 10:00:00"},
    {"invoice_number": "INV-MSFT-2026-992", "vendor_name": "Microsoft Corporation", "invoice_type": "PAYABLE", "amount": 4650.00, "currency": "USD", "due_date": "2026-11-08", "status": "APPROVED", "notes": "Microsoft 365 E5 enterprise licensing for 250 employees", "created_at": "2026-10-02 14:00:00"},
    {"invoice_number": "INV-EQX-2026-303", "vendor_name": "Equinix Data Centers", "invoice_type": "PAYABLE", "amount": 9200.00, "currency": "USD", "due_date": "2026-11-15", "status": "PENDING_APPROVAL", "notes": "Silicon Valley SV5 datacenter cage power, cooling and cross-connects", "created_at": "2026-10-01 11:30:00"},
    {"invoice_number": "INV-ORCL-2026-771", "vendor_name": "Oracle Cloud Infrastructure", "invoice_type": "PAYABLE", "amount": 7800.00, "currency": "USD", "due_date": "2026-11-22", "status": "PENDING_APPROVAL", "notes": "Autonomous Database backup replication vault tier", "created_at": "2026-10-03 13:00:00"},
    {"invoice_number": "INV-CRWD-2026-442", "vendor_name": "CrowdStrike Falcon", "invoice_type": "PAYABLE", "amount": 6200.00, "currency": "USD", "due_date": "2026-11-12", "status": "APPROVED", "notes": "Endpoint detection and response (EDR) agent licensing Q4", "created_at": "2026-09-29 16:20:00"},
    {"invoice_number": "INV-HUBS-2026-110", "vendor_name": "HubSpot Enterprise", "invoice_type": "PAYABLE", "amount": 3400.00, "currency": "USD", "due_date": "2026-10-29", "status": "PAID", "notes": "Marketing Automation and inbound CRM pipeline sync tier", "created_at": "2026-09-20 09:15:00"},
    {"invoice_number": "INV-JIRA-2026-551", "vendor_name": "Atlassian Cloud Services", "invoice_type": "PAYABLE", "amount": 2600.00, "currency": "USD", "due_date": "2026-11-05", "status": "APPROVED", "notes": "Jira Software Premium and Confluence Cloud seats renewal", "created_at": "2026-10-02 17:00:00"},
    {"invoice_number": "INV-IRON-2026-224", "vendor_name": "Iron Mountain Secure Shred", "invoice_type": "PAYABLE", "amount": 750.00, "currency": "USD", "due_date": "2026-10-24", "status": "PAID", "notes": "Secure document destruction and offsite tape vaulting", "created_at": "2026-09-24 12:40:00"},

    # Receivables (Client Billings / Revenue)
    {"invoice_number": "INV-CLI-901", "vendor_name": "Nexus Healthcare Systems", "invoice_type": "RECEIVABLE", "amount": 45000.00, "currency": "USD", "due_date": "2026-11-30", "status": "PENDING_APPROVAL", "notes": "CentrAlign AI Engine enterprise subscription Q4", "created_at": "2026-10-01 09:00:00"},
    {"invoice_number": "INV-CLI-902", "vendor_name": "Vertex FinTech Corp", "invoice_type": "RECEIVABLE", "amount": 32500.00, "currency": "USD", "due_date": "2026-10-31", "status": "PAID", "notes": "Custom API integration & onboarding package", "created_at": "2026-09-10 16:30:00"},
    {"invoice_number": "INV-CLI-903", "vendor_name": "FinEdge Global Capital", "invoice_type": "RECEIVABLE", "amount": 62000.00, "currency": "USD", "due_date": "2026-12-15", "status": "PENDING_APPROVAL", "notes": "High-Frequency Transaction Intelligence Platform license", "created_at": "2026-10-02 11:00:00"},
    {"invoice_number": "INV-CLI-904", "vendor_name": "Quantum Dynamics Logistics", "invoice_type": "RECEIVABLE", "amount": 24500.00, "currency": "USD", "due_date": "2026-11-20", "status": "APPROVED", "notes": "Supply chain optimization worker automation modules", "created_at": "2026-09-28 10:15:00"},
    {"invoice_number": "INV-CLI-905", "vendor_name": "OmniMedia Digital Group", "invoice_type": "RECEIVABLE", "amount": 18000.00, "currency": "USD", "due_date": "2026-10-25", "status": "PAID", "notes": "Digital asset classification & search integration license", "created_at": "2026-09-15 14:00:00"},
    {"invoice_number": "INV-CLI-906", "vendor_name": "BioHealth Diagnostics", "invoice_type": "RECEIVABLE", "amount": 29000.00, "currency": "USD", "due_date": "2026-11-28", "status": "PENDING_APPROVAL", "notes": "Clinical document automated parser & OCR extraction pipeline", "created_at": "2026-10-03 09:45:00"},
    {"invoice_number": "INV-CLI-907", "vendor_name": "Nova Retail Solutions", "invoice_type": "RECEIVABLE", "amount": 38500.00, "currency": "USD", "due_date": "2026-12-05", "status": "APPROVED", "notes": "Omnichannel POS inventory autonomous sync worker setup", "created_at": "2026-10-01 13:20:00"},
    {"invoice_number": "INV-CLI-908", "vendor_name": "Vanguard Asset Management", "invoice_type": "RECEIVABLE", "amount": 85000.00, "currency": "USD", "due_date": "2026-12-20", "status": "PENDING_APPROVAL", "notes": "Enterprise Private Cloud CentrAlign instance deployment & SLA", "created_at": "2026-10-04 15:00:00"},
    {"invoice_number": "INV-CLI-909", "vendor_name": "Horizon Telecommunications", "invoice_type": "RECEIVABLE", "amount": 52000.00, "currency": "USD", "due_date": "2026-11-15", "status": "APPROVED", "notes": "Automated network outage ticket triage and resolution bot", "created_at": "2026-09-26 11:30:00"},
    {"invoice_number": "INV-CLI-910", "vendor_name": "Stellar Mobility Labs", "invoice_type": "RECEIVABLE", "amount": 41000.00, "currency": "USD", "due_date": "2026-12-10", "status": "PENDING_APPROVAL", "notes": "Autonomous fleet dispatch analytics integration package", "created_at": "2026-10-02 16:10:00"},
    {"invoice_number": "INV-CLI-911", "vendor_name": "Aether Dynamics Aerospace", "invoice_type": "RECEIVABLE", "amount": 95000.00, "currency": "USD", "due_date": "2026-12-28", "status": "PENDING_APPROVAL", "notes": "Autonomous telemetry parsing and failure prediction agent deployment", "created_at": "2026-10-05 14:00:00"},
    {"invoice_number": "INV-CLI-912", "vendor_name": "Pacific Rim Maritime Group", "invoice_type": "RECEIVABLE", "amount": 28000.00, "currency": "USD", "due_date": "2026-11-22", "status": "APPROVED", "notes": "Port container routing and customs document extraction API", "created_at": "2026-09-29 15:30:00"},
    {"invoice_number": "INV-CLI-913", "vendor_name": "Crestline Insurance Services", "invoice_type": "RECEIVABLE", "amount": 47500.00, "currency": "USD", "due_date": "2026-12-12", "status": "PENDING_APPROVAL", "notes": "Claims processing adjudication agent workflow pilot", "created_at": "2026-10-03 10:45:00"},
    {"invoice_number": "INV-CLI-914", "vendor_name": "Summit Energy Partners", "invoice_type": "RECEIVABLE", "amount": 36000.00, "currency": "USD", "due_date": "2026-11-19", "status": "APPROVED", "notes": "Smart grid substation meter audit data connector package", "created_at": "2026-09-30 08:30:00"},
    {"invoice_number": "INV-CLI-915", "vendor_name": "Kodiak Robotics Research", "invoice_type": "RECEIVABLE", "amount": 31000.00, "currency": "USD", "due_date": "2026-12-08", "status": "PENDING_APPROVAL", "notes": "Simulation sensor pipeline ingestion & verification module", "created_at": "2026-10-04 16:20:00"},
]

# -------------------------------------------------------------
# 5. SUPPORT TICKETS DATA (25 ITSM Tickets in ONE Master Table)
# -------------------------------------------------------------
SUPPORT_TICKETS_DATA = [
    {"ticket_number": "TCK-2026-801", "customer_name": "Vertex FinTech Corp", "requester_email": "cchen@vertexfintech.com", "category": "Bug", "priority": "CRITICAL", "subject": "API Webhook Failures on Settlement Ingestion", "description": "High latency and intermittent 504 Gateway Timeouts observed on production /api/v2/settle endpoints during market open.", "status": "OPEN", "assignee": "Unassigned", "resolution_notes": None, "created_at": "2026-10-06 08:15:00", "sla_due": "2026-10-06 10:15:00"},
    {"ticket_number": "TCK-2026-802", "customer_name": "Nexus Healthcare Systems", "requester_email": "support@nexushealth.org", "category": "IT Support", "priority": "HIGH", "subject": "SSO Login Certificate Expiring in 48 Hours", "description": "Our Okta SAML signing cert will rotate on Thursday; need CentrAlign team to update metadata XML.", "status": "IN_PROGRESS", "assignee": "Alex Wong", "resolution_notes": "Updating IdP configuration in staging environment", "created_at": "2026-10-05 14:00:00", "sla_due": "2026-10-06 18:00:00"},
    {"ticket_number": "TCK-2026-803", "customer_name": "Quantum Dynamics Logistics", "requester_email": "ops@quantumdyn.com", "category": "Billing", "priority": "MEDIUM", "subject": "Invoice Query on Additional Worker Threads", "description": "Requesting breakdown of additional $450 compute surcharge on September invoice INV-CLI-890.", "status": "OPEN", "assignee": "Thomas Becker", "resolution_notes": None, "created_at": "2026-10-04 11:20:00", "sla_due": "2026-10-07 11:20:00"},
    {"ticket_number": "TCK-2026-804", "customer_name": "CentrAlign Internal Staff", "requester_email": "chloe.martin@centralign.internal", "category": "System Access", "priority": "LOW", "subject": "VPN Profile Renewal for Tokyo Staging Cluster", "description": "Requesting configuration profile for new AWS ap-northeast-1 VPC peering bastion.", "status": "RESOLVED", "assignee": "Alex Wong", "resolution_notes": "Provisioned WireGuard key and granted access via security group sg-9920", "created_at": "2026-10-03 16:45:00", "sla_due": "2026-10-04 16:45:00"},
    {"ticket_number": "TCK-2026-805", "customer_name": "FinEdge Global Capital", "requester_email": "security@finedge.com", "category": "IT Support", "priority": "CRITICAL", "subject": "Database Read Replica High Lag Alert", "description": "Secondary Postgres replication lag exceeded 45 seconds on east-1 region.", "status": "OPEN", "assignee": "Unassigned", "resolution_notes": None, "created_at": "2026-10-06 09:00:00", "sla_due": "2026-10-06 11:00:00"},
    {"ticket_number": "TCK-2026-806", "customer_name": "OmniMedia Digital Group", "requester_email": "sconnor@omnimedia.com", "category": "Feature Request", "priority": "LOW", "subject": "Support for WebP lossless image format export", "description": "Requesting automated conversion and export option for WebP assets in batch worker pipeline.", "status": "OPEN", "assignee": "David Miller", "resolution_notes": None, "created_at": "2026-10-02 13:10:00", "sla_due": "2026-10-09 13:10:00"},
    {"ticket_number": "TCK-2026-807", "customer_name": "BioHealth Diagnostics", "requester_email": "lab-it@biohealth.com", "category": "Security", "priority": "HIGH", "subject": "IP Allowlist update for new laboratory subnet", "description": "Please add 198.51.100.0/24 to the CentrAlign enterprise API ingress security group.", "status": "IN_PROGRESS", "assignee": "Rajiv Sharma", "resolution_notes": "Reviewing security group ingress rules in AWS console", "created_at": "2026-10-05 16:30:00", "sla_due": "2026-10-06 20:30:00"},
    {"ticket_number": "TCK-2026-808", "customer_name": "Nova Retail Solutions", "requester_email": "tech@novaretail.com", "category": "Bug", "priority": "MEDIUM", "subject": "Stock replenishment counter desync in POS view", "description": "Dashboard shows 14 items in stock when physical barcode scanner reports 12 items.", "status": "OPEN", "assignee": "Liam O'Connor", "resolution_notes": None, "created_at": "2026-10-04 15:00:00", "sla_due": "2026-10-07 15:00:00"},
    {"ticket_number": "TCK-2026-809", "customer_name": "Vanguard Asset Management", "requester_email": "infra@vanguard-am.com", "category": "IT Support", "priority": "CRITICAL", "subject": "Dedicated Kubernetes worker node OOMKilled", "description": "Worker node pod-3 in dedicated cluster encountered out-of-memory termination during risk model simulation.", "status": "OPEN", "assignee": "Unassigned", "resolution_notes": None, "created_at": "2026-10-06 07:45:00", "sla_due": "2026-10-06 09:45:00"},
    {"ticket_number": "TCK-2026-810", "customer_name": "Horizon Telecommunications", "requester_email": "noc@horizon-telecom.net", "category": "Network", "priority": "HIGH", "subject": "BGP route flap between us-west and us-east transit", "description": "Observing intermittent packet loss across Direct Connect circuit VLAN 402.", "status": "IN_PROGRESS", "assignee": "Alex Wong", "resolution_notes": "Coordinating with Equinix and AWS networking engineers", "created_at": "2026-10-05 11:15:00", "sla_due": "2026-10-06 15:15:00"},
    {"ticket_number": "TCK-2026-811", "customer_name": "CentrAlign Internal Staff", "requester_email": "sarah.jenkins@centralign.internal", "category": "Hardware", "priority": "LOW", "subject": "Request for second 4K monitor arm", "description": "Workstation desk dual monitor pole mount screw thread stripped.", "status": "RESOLVED", "assignee": "Hanna Lindqvist", "resolution_notes": "Replaced with new Ergotron dual arm from IT storage", "created_at": "2026-10-01 10:00:00", "sla_due": "2026-10-02 10:00:00"},
    {"ticket_number": "TCK-2026-812", "customer_name": "Stellar Mobility Labs", "requester_email": "fleet@stellarmobility.io", "category": "Billing", "priority": "LOW", "subject": "Update corporate billing tax identification number", "description": "Need to update EU VAT ID for European subsidiary on monthly recurring invoice template.", "status": "OPEN", "assignee": "Ananya Roy", "resolution_notes": None, "created_at": "2026-10-03 14:20:00", "sla_due": "2026-10-06 14:20:00"},
    {"ticket_number": "TCK-2026-813", "customer_name": "Aether Dynamics Aerospace", "requester_email": "telemetry@aetherdynamics.com", "category": "Bug", "priority": "HIGH", "subject": "Protobuf serialization exception in streaming client", "description": "Encountering invalid wire type 7 when parsing high-frequency flight sensor payloads.", "status": "OPEN", "assignee": "Ethan Brooks", "resolution_notes": None, "created_at": "2026-10-05 18:00:00", "sla_due": "2026-10-06 22:00:00"},
    {"ticket_number": "TCK-2026-814", "customer_name": "Pacific Rim Maritime Group", "requester_email": "logistics@pacrim-maritime.com", "category": "IT Support", "priority": "MEDIUM", "subject": "Automated customs invoice OCR queue delay", "description": "PDF ingestion batch processing queued for >45 minutes during evening vessel arrivals.", "status": "IN_PROGRESS", "assignee": "Dmitri Volkov", "resolution_notes": "Scaling Celery OCR worker pool from 4 to 12 instances", "created_at": "2026-10-06 02:30:00", "sla_due": "2026-10-06 10:30:00"},
    {"ticket_number": "TCK-2026-815", "customer_name": "CentrAlign Internal Staff", "requester_email": "elena.vance@centralign.internal", "category": "Security", "priority": "CRITICAL", "subject": "Suspicious phishing email reporting credential harvest link", "description": "Multiple employees received mock HR payroll update link pointing to external domain.", "status": "OPEN", "assignee": "Unassigned", "resolution_notes": None, "created_at": "2026-10-06 08:45:00", "sla_due": "2026-10-06 09:45:00"},
]

# -------------------------------------------------------------
# 6. INVENTORY & WAREHOUSE CATALOG (30 Items in ONE Master Table)
# -------------------------------------------------------------
INVENTORY_DATA = [
    # Core test items (retained)
    {"sku": "SKU-LAP-M3P", "item_name": "Apple MacBook Pro 16\" M3 Pro (36GB)", "category": "Hardware", "stock_on_hand": 4, "reorder_threshold": 5, "target_reorder_qty": 10, "unit_cost": 2499.00, "supplier": "Apple Enterprise Direct", "warehouse_location": "Aisle 3 - Secure Cage A"},
    {"sku": "SKU-LAP-DELL", "item_name": "Dell XPS 15 9530 (i7, 32GB, 1TB)", "category": "Hardware", "stock_on_hand": 8, "reorder_threshold": 4, "target_reorder_qty": 8, "unit_cost": 1750.00, "supplier": "Dell Enterprise Store", "warehouse_location": "Aisle 3 - Shelf B"},
    {"sku": "SKU-MON-4K", "item_name": "Dell UltraSharp 32\" 4K USB-C Hub Monitor", "category": "Peripherals", "stock_on_hand": 3, "reorder_threshold": 6, "target_reorder_qty": 12, "unit_cost": 650.00, "supplier": "Dell Enterprise Store", "warehouse_location": "Aisle 2 - Bay 4"},
    {"sku": "SKU-NET-SW24", "item_name": "Cisco Catalyst 24-Port Gigabit PoE Switch", "category": "Network", "stock_on_hand": 2, "reorder_threshold": 3, "target_reorder_qty": 5, "unit_cost": 1200.00, "supplier": "Cisco Systems", "warehouse_location": "Aisle 1 - Server Room"},
    {"sku": "SKU-SRV-NV1", "item_name": "NVIDIA RTX 6000 Ada Generation GPU (48GB)", "category": "Server", "stock_on_hand": 1, "reorder_threshold": 2, "target_reorder_qty": 4, "unit_cost": 6800.00, "supplier": "PNY Commercial", "warehouse_location": "Aisle 1 - High Value Safe"},
    {"sku": "SKU-ACC-DOCK", "item_name": "CalDigit TS4 Thunderbolt 4 Docking Station", "category": "Peripherals", "stock_on_hand": 12, "reorder_threshold": 5, "target_reorder_qty": 10, "unit_cost": 399.00, "supplier": "CalDigit Direct", "warehouse_location": "Aisle 2 - Shelf A"},
    {"sku": "SKU-OFF-CHAIR", "item_name": "Herman Miller Aeron Chair Size B", "category": "Office Supplies", "stock_on_hand": 6, "reorder_threshold": 4, "target_reorder_qty": 6, "unit_cost": 1195.00, "supplier": "Acme Supplies Co", "warehouse_location": "Warehouse Warehouse Floor East"},
    {"sku": "SKU-OFF-CABLE", "item_name": "Cat6A Shielded Ethernet Cable 10ft (10-Pack)", "category": "Network", "stock_on_hand": 25, "reorder_threshold": 10, "target_reorder_qty": 20, "unit_cost": 45.00, "supplier": "OfficeMax Pro", "warehouse_location": "Aisle 2 - Bin 12"},

    # Additional diverse enterprise hardware
    {"sku": "SKU-LAP-THINK", "item_name": "Lenovo ThinkPad X1 Carbon Gen 12", "category": "Hardware", "stock_on_hand": 2, "reorder_threshold": 5, "target_reorder_qty": 8, "unit_cost": 1820.00, "supplier": "Lenovo Commercial Direct", "warehouse_location": "Aisle 3 - Shelf C"},
    {"sku": "SKU-MON-27", "item_name": "LG 27\" UltraFine 4K Ergo Dual Monitor", "category": "Peripherals", "stock_on_hand": 5, "reorder_threshold": 8, "target_reorder_qty": 10, "unit_cost": 480.00, "supplier": "Dell Enterprise Store", "warehouse_location": "Aisle 2 - Bay 2"},
    {"sku": "SKU-NET-FW", "item_name": "Palo Alto PA-440 Next-Gen Hardware Firewall", "category": "Network", "stock_on_hand": 1, "reorder_threshold": 2, "target_reorder_qty": 2, "unit_cost": 3200.00, "supplier": "Palo Alto Networks", "warehouse_location": "Aisle 1 - Server Cage"},
    {"sku": "SKU-SRV-R760", "item_name": "Dell PowerEdge R760 2U Rackmount Server", "category": "Server", "stock_on_hand": 1, "reorder_threshold": 2, "target_reorder_qty": 2, "unit_cost": 8450.00, "supplier": "Dell Enterprise Store", "warehouse_location": "Aisle 1 - Server Room"},
    {"sku": "SKU-KEY-MX", "item_name": "Logitech MX Master 3S + MX Keys Combo", "category": "Peripherals", "stock_on_hand": 14, "reorder_threshold": 8, "target_reorder_qty": 15, "unit_cost": 185.00, "supplier": "OfficeMax Pro", "warehouse_location": "Aisle 2 - Bin 4"},
    {"sku": "SKU-AUD-JABRA", "item_name": "Jabra Evolve2 85 Wireless ANC Headset", "category": "Audio/Video", "stock_on_hand": 3, "reorder_threshold": 6, "target_reorder_qty": 10, "unit_cost": 340.00, "supplier": "Acme Supplies Co", "warehouse_location": "Aisle 2 - Shelf D"},
    {"sku": "SKU-CAM-4K", "item_name": "Logitech Brio 4K Ultra HD Streaming Webcam", "category": "Audio/Video", "stock_on_hand": 7, "reorder_threshold": 5, "target_reorder_qty": 10, "unit_cost": 175.00, "supplier": "OfficeMax Pro", "warehouse_location": "Aisle 2 - Bin 8"},
    {"sku": "SKU-UPS-1500", "item_name": "APC Smart-UPS 1500VA LCD 120V Battery Backup", "category": "Power", "stock_on_hand": 2, "reorder_threshold": 4, "target_reorder_qty": 6, "unit_cost": 620.00, "supplier": "Acme Supplies Co", "warehouse_location": "Aisle 1 - Floor Rack"},
    {"sku": "SKU-SEC-YUBI", "item_name": "Yubico YubiKey 5C NFC Security Key (50-Pack)", "category": "Security", "stock_on_hand": 4, "reorder_threshold": 5, "target_reorder_qty": 10, "unit_cost": 2100.00, "supplier": "Yubico Direct", "warehouse_location": "Aisle 1 - Safe Box 2"},
    {"sku": "SKU-TAB-IPAD", "item_name": "Apple iPad Pro 11\" M4 (256GB Wi-Fi)", "category": "Mobile", "stock_on_hand": 3, "reorder_threshold": 4, "target_reorder_qty": 5, "unit_cost": 949.00, "supplier": "Apple Enterprise Direct", "warehouse_location": "Aisle 3 - Shelf A"},
    {"sku": "SKU-DESK-STAND", "item_name": "Fully Jarvis Motorized Standing Desk 60x30", "category": "Office Supplies", "stock_on_hand": 4, "reorder_threshold": 5, "target_reorder_qty": 8, "unit_cost": 780.00, "supplier": "Acme Supplies Co", "warehouse_location": "Warehouse Floor West"},
    {"sku": "SKU-SSD-2TB", "item_name": "Samsung 990 PRO NVMe M.2 SSD 2TB", "category": "Hardware", "stock_on_hand": 8, "reorder_threshold": 10, "target_reorder_qty": 20, "unit_cost": 170.00, "supplier": "Dell Enterprise Store", "warehouse_location": "Aisle 2 - Bin 15"},
    {"sku": "SKU-SRV-H100", "item_name": "NVIDIA H100 80GB SXM5 AI Accelerator Tensor Core", "category": "Server", "stock_on_hand": 0, "reorder_threshold": 1, "target_reorder_qty": 2, "unit_cost": 32000.00, "supplier": "PNY Commercial", "warehouse_location": "Aisle 1 - High Value Safe"},
    {"sku": "SKU-NET-SFP", "item_name": "Cisco 10GBASE-SR SFP+ Transceiver Module (10-Pack)", "category": "Network", "stock_on_hand": 3, "reorder_threshold": 5, "target_reorder_qty": 10, "unit_cost": 450.00, "supplier": "Cisco Systems", "warehouse_location": "Aisle 1 - Bin 9"},
    {"sku": "SKU-PRN-LASER", "item_name": "HP Color LaserJet Enterprise MFP M578dn", "category": "Office Supplies", "stock_on_hand": 2, "reorder_threshold": 2, "target_reorder_qty": 3, "unit_cost": 1150.00, "supplier": "OfficeMax Pro", "warehouse_location": "Warehouse Floor North"},
    {"sku": "SKU-MIC-SHURE", "item_name": "Shure MV7X Podcast & Conference Vocal Mic", "category": "Audio/Video", "stock_on_hand": 4, "reorder_threshold": 4, "target_reorder_qty": 8, "unit_cost": 199.00, "supplier": "Acme Supplies Co", "warehouse_location": "Aisle 2 - Shelf E"},
    {"sku": "SKU-PDU-RACK", "item_name": "Tripp Lite 30A Switched Server Rack PDU", "category": "Power", "stock_on_hand": 1, "reorder_threshold": 2, "target_reorder_qty": 3, "unit_cost": 580.00, "supplier": "Acme Supplies Co", "warehouse_location": "Aisle 1 - Floor Rack 2"},
]

# -------------------------------------------------------------
# 7. EXPENSE REPORTS DATA (25 Claims in ONE Master Table)
# -------------------------------------------------------------
EXPENSES_DATA = [
    # Core test items (retained)
    {"report_number": "EXP-2026-101", "employee_name": "Sarah Jenkins", "department": "Engineering", "category": "Hardware", "amount": 1250.00, "merchant": "Dell Enterprise Store", "expense_date": "2026-09-28", "status": "SUBMITTED", "notes": "4K UltraSharp curved developer monitor", "receipt_ref": "receipt_dell_4k.pdf"},
    {"report_number": "EXP-2026-102", "employee_name": "Maya Lin", "department": "Sales & Revenue", "category": "Travel", "amount": 890.00, "merchant": "United Airlines", "expense_date": "2026-09-24", "status": "APPROVED", "notes": "Roundtrip flight to Chicago for Nexus client pitch", "receipt_ref": "receipt_flight_ord.pdf"},
    {"report_number": "EXP-2026-103", "employee_name": "David Sterling", "department": "Marketing & Growth", "category": "Software", "amount": 350.00, "merchant": "Canva Enterprise", "expense_date": "2026-09-30", "status": "APPROVED", "notes": "Design team collaborative subscription", "receipt_ref": "receipt_canva.pdf"},
    {"report_number": "EXP-2026-104", "employee_name": "Alex Wong", "department": "IT & Security", "category": "Hardware", "amount": 1850.00, "merchant": "Cisco Systems", "expense_date": "2026-10-02", "status": "SUBMITTED", "notes": "Replacement 24-port PoE Gigabit switch", "receipt_ref": "receipt_cisco_poe.pdf"},
    {"report_number": "EXP-2026-105", "employee_name": "Chloe Martin", "department": "Engineering", "category": "Meals & Entertainment", "amount": 145.50, "merchant": "Piazza D'Angelo", "expense_date": "2026-10-03", "status": "SUBMITTED", "notes": "Team sprint retrospective lunch celebration", "receipt_ref": "receipt_lunch.pdf"},

    # Additional expenses
    {"report_number": "EXP-2026-106", "employee_name": "Christian Cole", "department": "Sales & Revenue", "category": "Travel", "amount": 1450.00, "merchant": "Marriott Downtown Boston", "expense_date": "2026-09-29", "status": "SUBMITTED", "notes": "3 nights hotel stay during FinEdge executive summit", "receipt_ref": "receipt_marriott_bos.pdf"},
    {"report_number": "EXP-2026-107", "employee_name": "Priya Sharma", "department": "Data & AI Research", "category": "Training", "amount": 1800.00, "merchant": "NeurIPS Conference Foundation", "expense_date": "2026-10-01", "status": "SUBMITTED", "notes": "Full registration pass and workshop registration fee", "receipt_ref": "receipt_neurips_conf.pdf"},
    {"report_number": "EXP-2026-108", "employee_name": "David Miller", "department": "Engineering", "category": "Software", "amount": 240.00, "merchant": "JetBrains Commercial", "expense_date": "2026-09-15", "status": "APPROVED", "notes": "All Products Pack annual developer renewal", "receipt_ref": "receipt_jetbrains.pdf"},
    {"report_number": "EXP-2026-109", "employee_name": "Elena Vance", "department": "Human Resources", "category": "Meals & Entertainment", "amount": 320.00, "merchant": "The Cavalier SF", "expense_date": "2026-09-22", "status": "APPROVED", "notes": "New executive director candidate recruitment dinner", "receipt_ref": "receipt_dinner_cavalier.pdf"},
    {"report_number": "EXP-2026-110", "employee_name": "Liam O'Connor", "department": "IT & Security", "category": "Hardware", "amount": 1150.00, "merchant": "B&H Photo Video", "expense_date": "2026-10-04", "status": "SUBMITTED", "notes": "Network diagnostic fiber testing kit and OTDR probe", "receipt_ref": "receipt_bh_network.pdf"},
    {"report_number": "EXP-2026-111", "employee_name": "Natalie Foster", "department": "Marketing & Growth", "category": "Advertising", "amount": 2500.00, "merchant": "LinkedIn Marketing Solutions", "expense_date": "2026-10-02", "status": "SUBMITTED", "notes": "Q4 Enterprise AI whitepaper sponsored content campaign", "receipt_ref": "receipt_linkedin_ads.pdf"},
    {"report_number": "EXP-2026-112", "employee_name": "Lucas Meyer", "department": "Customer Success", "category": "Travel", "amount": 680.00, "merchant": "Delta Air Lines", "expense_date": "2026-09-18", "status": "APPROVED", "notes": "Flight to Atlanta for Quantum Dynamics quarterly business review", "receipt_ref": "receipt_delta_atl.pdf"},
    {"report_number": "EXP-2026-113", "employee_name": "Daphne Blake", "department": "Sales & Revenue", "category": "Travel", "amount": 1320.00, "merchant": "Hyatt Regency Seattle", "expense_date": "2026-09-27", "status": "SUBMITTED", "notes": "Onsite proof of concept demo with Vanguard Asset Management", "receipt_ref": "receipt_hyatt_sea.pdf"},
    {"report_number": "EXP-2026-114", "employee_name": "Turing Vance", "department": "Data & AI Research", "category": "Hardware", "amount": 1950.00, "merchant": "Apple Enterprise Direct", "expense_date": "2026-10-02", "status": "SUBMITTED", "notes": "Local development M3 Max test machine allocation", "receipt_ref": "receipt_apple_dev.pdf"},
    {"report_number": "EXP-2026-115", "employee_name": "Winston Bishop", "department": "Operations & Facilities", "category": "Facilities Supplies", "amount": 450.00, "merchant": "Home Depot Pro", "expense_date": "2026-09-26", "status": "APPROVED", "notes": "Server room thermal acoustic insulation barriers", "receipt_ref": "receipt_homedepot.pdf"},
]

# -------------------------------------------------------------
# 8. CRM CUSTOMERS (18 Accounts in ONE Master Table)
# -------------------------------------------------------------
CUSTOMERS_DATA = [
    {"customer_code": "CUST-1001", "company_name": "Nexus Healthcare Systems", "industry": "Healthcare & Biotech", "contract_tier": "Enterprise Tier", "annual_contract_value": 180000.0, "account_executive": "Maya Lin", "status": "ACTIVE", "health_score": 98, "primary_contact": "Dr. Robert Vance, CIO"},
    {"customer_code": "CUST-1002", "company_name": "Vertex FinTech Corp", "industry": "Financial Services", "contract_tier": "Enterprise Tier", "annual_contract_value": 130000.0, "account_executive": "Maya Lin", "status": "ACTIVE", "health_score": 92, "primary_contact": "Claire Chen, Head of Trading Tech"},
    {"customer_code": "CUST-1003", "company_name": "Quantum Dynamics Logistics", "industry": "Supply Chain", "contract_tier": "Mid-Market Tier", "annual_contract_value": 75000.0, "account_executive": "Jessica Alba-Ruiz", "status": "ACTIVE", "health_score": 88, "primary_contact": "Thomas Hardy, VP Ops"},
    {"customer_code": "CUST-1004", "company_name": "FinEdge Global Capital", "industry": "Banking & Investment", "contract_tier": "Enterprise Tier", "annual_contract_value": 210000.0, "account_executive": "Jessica Alba-Ruiz", "status": "ACTIVE", "health_score": 99, "primary_contact": "Jonathan Ross, CTO"},
    {"customer_code": "CUST-1005", "company_name": "OmniMedia Digital Group", "industry": "Media & Entertainment", "contract_tier": "Mid-Market Tier", "annual_contract_value": 60000.0, "account_executive": "Maya Lin", "status": "ACTIVE", "health_score": 91, "primary_contact": "Sarah Connor, Lead Arch"},
    {"customer_code": "CUST-1006", "company_name": "BioHealth Diagnostics", "industry": "Biotech & Genomics", "contract_tier": "Enterprise Tier", "annual_contract_value": 145000.0, "account_executive": "Christian Cole", "status": "ACTIVE", "health_score": 95, "primary_contact": "Dr. Angela Merkel, VP Research"},
    {"customer_code": "CUST-1007", "company_name": "Nova Retail Solutions", "industry": "Retail & E-Commerce", "contract_tier": "Mid-Market Tier", "annual_contract_value": 90000.0, "account_executive": "Sofia Reyes", "status": "ACTIVE", "health_score": 86, "primary_contact": "Marcus Aurelius, COO"},
    {"customer_code": "CUST-1008", "company_name": "Vanguard Asset Management", "industry": "Wealth & Asset Mgmt", "contract_tier": "Enterprise Tier", "annual_contract_value": 340000.0, "account_executive": "Christian Cole", "status": "ACTIVE", "health_score": 99, "primary_contact": "Alexander Hamilton, CIO"},
    {"customer_code": "CUST-1009", "company_name": "Horizon Telecommunications", "industry": "Telecom & 5G", "contract_tier": "Enterprise Tier", "annual_contract_value": 220000.0, "account_executive": "Jessica Alba-Ruiz", "status": "ACTIVE", "health_score": 94, "primary_contact": "Elena Rostova, VP Network Ops"},
    {"customer_code": "CUST-1010", "company_name": "Stellar Mobility Labs", "industry": "Autonomous Vehicles", "contract_tier": "Mid-Market Tier", "annual_contract_value": 85000.0, "account_executive": "Sofia Reyes", "status": "ACTIVE", "health_score": 89, "primary_contact": "Elon T. Vance, Head of Autonomy"},
    {"customer_code": "CUST-1011", "company_name": "Aether Dynamics Aerospace", "industry": "Aerospace & Defense", "contract_tier": "Enterprise Tier", "annual_contract_value": 290000.0, "account_executive": "Christian Cole", "status": "ACTIVE", "health_score": 97, "primary_contact": "Gen. James Holden, Director Tech"},
    {"customer_code": "CUST-1012", "company_name": "Pacific Rim Maritime Group", "industry": "Global Shipping", "contract_tier": "Mid-Market Tier", "annual_contract_value": 95000.0, "account_executive": "Daphne Blake", "status": "ACTIVE", "health_score": 90, "primary_contact": "Captain Naomi Nagata, Fleet VP"},
    {"customer_code": "CUST-1013", "company_name": "Crestline Insurance Services", "industry": "Insurance & InsurTech", "contract_tier": "Enterprise Tier", "annual_contract_value": 165000.0, "account_executive": "Maya Lin", "status": "ACTIVE", "health_score": 93, "primary_contact": "Amos Burton, Claims Director"},
    {"customer_code": "CUST-1014", "company_name": "Summit Energy Partners", "industry": "Renewable Energy", "contract_tier": "Enterprise Tier", "annual_contract_value": 140000.0, "account_executive": "Jessica Alba-Ruiz", "status": "ACTIVE", "health_score": 91, "primary_contact": "Camina Drummer, VP Infrastructure"},
    {"customer_code": "CUST-1015", "company_name": "Kodiak Robotics Research", "industry": "Robotics & Automation", "contract_tier": "Mid-Market Tier", "annual_contract_value": 115000.0, "account_executive": "Sofia Reyes", "status": "ACTIVE", "health_score": 94, "primary_contact": "Dr. Alex Kamal, Navigation Lead"},
]

# -------------------------------------------------------------
# 9. SALES DEALS PIPELINE (15 Deals in ONE Master Table)
# -------------------------------------------------------------
DEALS_DATA = [
    {"deal_name": "Apex Global AI Renewal & Expansion", "customer_name": "Apex Logistics Ltd", "stage": "Negotiation", "deal_value": 95000.0, "close_date": "2026-11-15", "probability_pct": 85},
    {"deal_name": "Nexus Healthcare AI Automation Add-On", "customer_name": "Nexus Healthcare Systems", "stage": "Proposal", "deal_value": 60000.0, "close_date": "2026-11-30", "probability_pct": 70},
    {"deal_name": "Vertex FinTech Core Platform Multi-Year", "customer_name": "Vertex FinTech Corp", "stage": "Closed Won", "deal_value": 260000.0, "close_date": "2026-09-28", "probability_pct": 100},
    {"deal_name": "FinEdge High-Frequency Ingestion Module", "customer_name": "FinEdge Global Capital", "stage": "Qualification", "deal_value": 120000.0, "close_date": "2026-12-15", "probability_pct": 50},
    {"deal_name": "BioHealth Automated Genomics Workflow", "customer_name": "BioHealth Diagnostics", "stage": "Proposal", "deal_value": 110000.0, "close_date": "2026-11-20", "probability_pct": 65},
    {"deal_name": "Vanguard Private Cloud Hosting Tier", "customer_name": "Vanguard Asset Management", "stage": "Negotiation", "deal_value": 280000.0, "close_date": "2026-11-05", "probability_pct": 90},
    {"deal_name": "Horizon 5G Edge Network Orchestrator", "customer_name": "Horizon Telecommunications", "stage": "Proposal", "deal_value": 175000.0, "close_date": "2026-12-01", "probability_pct": 60},
    {"deal_name": "Aether Dynamics Spacecraft Telemetry Agent", "customer_name": "Aether Dynamics Aerospace", "stage": "Negotiation", "deal_value": 240000.0, "close_date": "2026-11-18", "probability_pct": 80},
    {"deal_name": "Pacific Rim Maritime Vessel Automated Pilot", "customer_name": "Pacific Rim Maritime Group", "stage": "Qualification", "deal_value": 85000.0, "close_date": "2026-12-20", "probability_pct": 45},
    {"deal_name": "Crestline InsurTech Adjudication Expansion", "customer_name": "Crestline Insurance Services", "stage": "Proposal", "deal_value": 130000.0, "close_date": "2026-11-28", "probability_pct": 75},
]

# -------------------------------------------------------------
# 10. PURCHASE ORDERS (14 Orders in ONE Master Table)
# -------------------------------------------------------------
PURCHASE_ORDERS_DATA = [
    {"po_number": "PO-2026-301", "supplier": "Apple Enterprise Direct", "items_summary": "5x MacBook Pro 14\" M3", "total_cost": 9995.00, "status": "DELIVERED", "created_at": "2026-09-10 10:00:00", "delivery_expected": "2026-09-18"},
    {"po_number": "PO-2026-302", "supplier": "Dell Enterprise Store", "items_summary": "8x Dell UltraSharp 32\" Monitors", "total_cost": 5200.00, "status": "ISSUED", "created_at": "2026-10-02 11:30:00", "delivery_expected": "2026-10-12"},
    {"po_number": "PO-2026-303", "supplier": "Acme Supplies Co", "items_summary": "6x Herman Miller Ergonomic Chairs", "total_cost": 7170.00, "status": "ISSUED", "created_at": "2026-10-04 15:45:00", "delivery_expected": "2026-10-20"},
    {"po_number": "PO-2026-304", "supplier": "Cisco Systems", "items_summary": "2x Cisco Catalyst 24-Port PoE Switch", "total_cost": 2400.00, "status": "DELIVERED", "created_at": "2026-09-15 09:30:00", "delivery_expected": "2026-09-22"},
    {"po_number": "PO-2026-305", "supplier": "PNY Commercial", "items_summary": "1x NVIDIA RTX 6000 Ada GPU", "total_cost": 6800.00, "status": "IN_TRANSIT", "created_at": "2026-10-01 14:00:00", "delivery_expected": "2026-10-08"},
    {"po_number": "PO-2026-306", "supplier": "OfficeMax Pro", "items_summary": "20x Cat6A Shielded Ethernet Cable 10-Packs", "total_cost": 900.00, "status": "DELIVERED", "created_at": "2026-09-12 11:00:00", "delivery_expected": "2026-09-16"},
    {"po_number": "PO-2026-307", "supplier": "Yubico Direct", "items_summary": "5x YubiKey 5C NFC Security Key 50-Packs", "total_cost": 10500.00, "status": "ISSUED", "created_at": "2026-10-03 13:15:00", "delivery_expected": "2026-10-15"},
    {"po_number": "PO-2026-308", "supplier": "Dell Enterprise Store", "items_summary": "2x Dell PowerEdge R760 2U Rackmount Server", "total_cost": 16900.00, "status": "IN_TRANSIT", "created_at": "2026-09-28 09:00:00", "delivery_expected": "2026-10-10"},
]

def export_to_csv_and_json(data_list, filename_prefix):
    """Exports any table list to both a master CSV file and a JSON file."""
    if not data_list:
        return
    csv_path = os.path.join(TABLES_DIR, f"{filename_prefix}.csv")
    json_path = os.path.join(TABLES_DIR, f"{filename_prefix}.json")

    # CSV
    fieldnames = list(data_list[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_list)

    # JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data_list, f, indent=2)

    print(f"Generated single-file table: {csv_path} ({len(data_list)} records)")
    print(f"Generated single-file table: {json_path}")

def generate_all_single_file_tables():
    """Generates consolidated single-file master tables for all domains."""
    ensure_directories()
    print("\n--- Generating Consolidated Master Table Files in data/enterprise_tables/ ---")
    
    # 1. Invoices Master Table (ALL invoices for all people/vendors in ONE file)
    export_to_csv_and_json(INVOICES_DATA, "invoices_master_table")

    # 2. Employees Master Table (ALL employees in ONE file)
    export_to_csv_and_json(EMPLOYEES_DATA, "employees_master_table")

    # 3. Leave Requests Master Table
    export_to_csv_and_json(LEAVE_REQUESTS_DATA, "leave_requests_master_table")

    # 4. Support Tickets Master Table
    export_to_csv_and_json(SUPPORT_TICKETS_DATA, "support_tickets_master_table")

    # 5. Inventory Master Table
    export_to_csv_and_json(INVENTORY_DATA, "inventory_master_table")

    # 6. Expenses Master Table
    export_to_csv_and_json(EXPENSES_DATA, "expenses_master_table")

    # 7. Customers CRM Master Table
    export_to_csv_and_json(CUSTOMERS_DATA, "customers_crm_master_table")

    # 8. Sales Deals Master Table
    export_to_csv_and_json(DEALS_DATA, "deals_master_table")

    # 9. Departments Master Table
    export_to_csv_and_json(DEPARTMENTS_DATA, "departments_master_table")

    # 10. Purchase Orders Master Table
    export_to_csv_and_json(PURCHASE_ORDERS_DATA, "purchase_orders_master_table")

def generate_unified_enterprise_dataset():
    """Combines ALL enterprise tables into a single unified JSON file."""
    master_dataset = {
        "metadata": {
            "company_name": "CentrAlign Technologies Inc.",
            "dataset_version": "2.0-ENTERPRISE-BIGDATA",
            "generated_at": datetime.now().isoformat(),
            "total_domains": 10,
            "description": "Consolidated single-file master enterprise dataset across all corporate departments, ledgers, workflows, and operations."
        },
        "domains": {
            "departments": DEPARTMENTS_DATA,
            "employees": EMPLOYEES_DATA,
            "leave_requests": LEAVE_REQUESTS_DATA,
            "invoices": INVOICES_DATA,
            "support_tickets": SUPPORT_TICKETS_DATA,
            "inventory": INVENTORY_DATA,
            "expense_reports": EXPENSES_DATA,
            "customers": CUSTOMERS_DATA,
            "deals": DEALS_DATA,
            "purchase_orders": PURCHASE_ORDERS_DATA
        },
        "statistics": {
            "total_departments": len(DEPARTMENTS_DATA),
            "total_employees": len(EMPLOYEES_DATA),
            "total_leave_requests": len(LEAVE_REQUESTS_DATA),
            "total_invoices": len(INVOICES_DATA),
            "total_support_tickets": len(SUPPORT_TICKETS_DATA),
            "total_inventory_items": len(INVENTORY_DATA),
            "total_expenses": len(EXPENSES_DATA),
            "total_customers": len(CUSTOMERS_DATA),
            "total_deals": len(DEALS_DATA),
            "total_purchase_orders": len(PURCHASE_ORDERS_DATA),
            "total_invoice_payable_volume_usd": sum(i["amount"] for i in INVOICES_DATA if i["invoice_type"] == "PAYABLE"),
            "total_invoice_receivable_volume_usd": sum(i["amount"] for i in INVOICES_DATA if i["invoice_type"] == "RECEIVABLE"),
        }
    }

    unified_path = os.path.join(TABLES_DIR, "ALL_DOMAINS_ENTERPRISE_MASTER_DATASET.json")
    with open(unified_path, "w", encoding="utf-8") as f:
        json.dump(master_dataset, f, indent=2)
    print(f"\n[SUCCESS] Generated Complete Multi-Domain Master File:\n -> {unified_path}")

    # Also create a Markdown Dataset Summary
    summary_md_path = os.path.join(TABLES_DIR, "README_DATASETS.md")
    with open(summary_md_path, "w", encoding="utf-8") as f:
        f.write("# CentrAlign Enterprise Big Dataset — Single-File Catalog\n\n")
        f.write("This directory contains consolidated, single-file tabular datasets for each corporate domain, as well as a unified master file covering all domains.\n\n")
        f.write("| Domain | File (CSV) | File (JSON) | Record Count | Description |\n")
        f.write("| :--- | :--- | :--- | :---: | :--- |\n")
        f.write(f"| **Invoices** | [`invoices_master_table.csv`](invoices_master_table.csv) | [`invoices_master_table.json`](invoices_master_table.json) | {len(INVOICES_DATA)} | Master accounts payable & receivable table for all vendors, clients & staff |\n")
        f.write(f"| **Employees** | [`employees_master_table.csv`](employees_master_table.csv) | [`employees_master_table.json`](employees_master_table.json) | {len(EMPLOYEES_DATA)} | Complete enterprise staff directory across 10 departments |\n")
        f.write(f"| **Leave Requests** | [`leave_requests_master_table.csv`](leave_requests_master_table.csv) | [`leave_requests_master_table.json`](leave_requests_master_table.json) | {len(LEAVE_REQUESTS_DATA)} | PTO vacation, sick, and personal leave claims |\n")
        f.write(f"| **ITSM Tickets** | [`support_tickets_master_table.csv`](support_tickets_master_table.csv) | [`support_tickets_master_table.json`](support_tickets_master_table.json) | {len(SUPPORT_TICKETS_DATA)} | Helpdesk tickets with SLAs, priorities P1-P4, assignees |\n")
        f.write(f"| **Inventory** | [`inventory_master_table.csv`](inventory_master_table.csv) | [`inventory_master_table.json`](inventory_master_table.json) | {len(INVENTORY_DATA)} | Hardware, server, network, and office asset catalog |\n")
        f.write(f"| **Expenses** | [`expenses_master_table.csv`](expenses_master_table.csv) | [`expenses_master_table.json`](expenses_master_table.json) | {len(EXPENSES_DATA)} | Corporate reimbursement claims & supervisor approval tiers |\n")
        f.write(f"| **CRM Accounts** | [`customers_crm_master_table.csv`](customers_crm_master_table.csv) | [`customers_crm_master_table.json`](customers_crm_master_table.json) | {len(CUSTOMERS_DATA)} | Enterprise clients, ARR contracts, health scores |\n")
        f.write(f"| **Sales Pipeline** | [`deals_master_table.csv`](deals_master_table.csv) | [`deals_master_table.json`](deals_master_table.json) | {len(DEALS_DATA)} | Active and closed sales opportunities |\n")
        f.write(f"| **Departments** | [`departments_master_table.csv`](departments_master_table.csv) | [`departments_master_table.json`](departments_master_table.json) | {len(DEPARTMENTS_DATA)} | Department heads, Q3 budgets, and spent amounts |\n")
        f.write(f"| **Purchase Orders** | [`purchase_orders_master_table.csv`](purchase_orders_master_table.csv) | [`purchase_orders_master_table.json`](purchase_orders_master_table.json) | {len(PURCHASE_ORDERS_DATA)} | Procurement orders issued to preferred suppliers |\n\n")
        f.write("### Single-File Master Package\n")
        f.write("The complete dataset is also bundled into a single unified JSON file:\n")
        f.write("- **[`ALL_DOMAINS_ENTERPRISE_MASTER_DATASET.json`](ALL_DOMAINS_ENTERPRISE_MASTER_DATASET.json)**\n")
    print(f"Generated Catalog Summary: {summary_md_path}")

def generate_master_invoices_document():
    """Generates a comprehensive, formatted multi-page master PDF and TXT report tabling all invoices in one file."""
    txt_path = os.path.join(INVOICES_DIR, "Master_Invoices_Register.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 110 + "\n")
        f.write("                       CENTRALIGN TECHNOLOGIES INC. — MASTER INVOICES REGISTER\n")
        f.write("                          Comprehensive Accounts Payable & Receivable Ledger\n")
        f.write("=" * 110 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Invoices Recorded: {len(INVOICES_DATA)}\n")
        f.write("-" * 110 + "\n")
        f.write(f"{'INVOICE #':<18} {'VENDOR / CLIENT / PERSON':<32} {'TYPE':<12} {'AMOUNT (USD)':<15} {'DUE DATE':<12} {'STATUS':<15}\n")
        f.write("-" * 110 + "\n")
        for inv in INVOICES_DATA:
            amt_str = f"${inv['amount']:,.2f}"
            f.write(f"{inv['invoice_number']:<18} {inv['vendor_name']:<32} {inv['invoice_type']:<12} {amt_str:<15} {inv['due_date']:<12} {inv['status']:<15}\n")
        f.write("=" * 110 + "\n")
        tot_pay = sum(i["amount"] for i in INVOICES_DATA if i["invoice_type"] == "PAYABLE")
        tot_rec = sum(i["amount"] for i in INVOICES_DATA if i["invoice_type"] == "RECEIVABLE")
        f.write(f"TOTAL PAYABLE (Accounts Payable):   ${tot_pay:,.2f} USD\n")
        f.write(f"TOTAL RECEIVABLE (Client Billings): ${tot_rec:,.2f} USD\n")
        f.write("=" * 110 + "\n")
    print(f"Generated Consolidated Master Invoice Text Report: {txt_path}")

    # Generate ReportLab PDF
    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        pdf_path = os.path.join(INVOICES_DIR, "Master_Invoices_Register.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0F172A'), spaceAfter=4)
        sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748B'), spaceAfter=10)
        cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#1E293B'))
        header_cell = ParagraphStyle('HCell', parent=styles['Normal'], fontSize=8.5, leading=11, fontName='Helvetica-Bold', textColor=colors.white)

        story.append(Paragraph("<b>CentrAlign Technologies Inc. — Master Invoices Register</b>", title_style))
        story.append(Paragraph(f"Comprehensive General Accounts Payable & Receivable Ledger | As of {datetime.now().strftime('%B %d, %Y')}", sub_style))

        # Build table data
        table_rows = [
            [
                Paragraph("<b>Invoice #</b>", header_cell),
                Paragraph("<b>Vendor / Client / Counterparty</b>", header_cell),
                Paragraph("<b>Type</b>", header_cell),
                Paragraph("<b>Amount (USD)</b>", header_cell),
                Paragraph("<b>Due Date</b>", header_cell),
                Paragraph("<b>Status</b>", header_cell),
                Paragraph("<b>Description / Notes</b>", header_cell),
            ]
        ]

        for inv in INVOICES_DATA:
            amt_str = f"${inv['amount']:,.2f}"
            note_str = inv['notes'][:45] + ("..." if len(inv['notes']) > 45 else "")
            table_rows.append([
                Paragraph(inv['invoice_number'], cell_style),
                Paragraph(inv['vendor_name'], cell_style),
                Paragraph(inv['invoice_type'], cell_style),
                Paragraph(amt_str, cell_style),
                Paragraph(inv['due_date'], cell_style),
                Paragraph(inv['status'], cell_style),
                Paragraph(note_str, cell_style),
            ])

        col_widths = [95, 150, 65, 75, 70, 95, 170]
        t = Table(table_rows, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        doc.build(story)
        print(f"Generated Consolidated Master Invoice PDF Report: {pdf_path}")
    except Exception as e:
        print(f"Master Invoices PDF generation skipped: {e}")

def seed_big_dataset_to_sqlite():
    """Populates the SQLite database with the full big dataset."""
    from mock_erp.database import init_db, get_connection
    init_db()

    conn = get_connection()
    cursor = conn.cursor()

    print("\n--- Seeding Enterprise SQLite Database (mock_erp/erp.db) with Big Dataset ---")

    # 1. Departments
    for d in DEPARTMENTS_DATA:
        cursor.execute("SELECT id FROM departments WHERE name = ?", (d["name"],))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE departments SET head_of_dept = ?, budget_q3 = ?, spent_q3 = ?, headcount = ? WHERE name = ?
            """, (d["head_of_dept"], d["budget_q3"], d["spent_q3"], d["headcount"], d["name"]))
        else:
            cursor.execute("""
                INSERT INTO departments (name, head_of_dept, budget_q3, spent_q3, headcount)
                VALUES (?, ?, ?, ?, ?)
            """, (d["name"], d["head_of_dept"], d["budget_q3"], d["spent_q3"], d["headcount"]))

    # 2. Employees
    for e in EMPLOYEES_DATA:
        cursor.execute("SELECT id FROM employees WHERE emp_code = ?", (e["emp_code"],))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE employees SET name=?, email=?, department=?, title=?, manager_name=?, hire_date=?, salary=?, status=?, leave_balance=?, phone=?, emergency_contact=?, performance_rating=?
                WHERE emp_code=?
            """, (e["name"], e["email"], e["department"], e["title"], e["manager_name"], e["hire_date"], e["salary"], e["status"], e["leave_balance"], e["phone"], e["emergency_contact"], e["performance_rating"], e["emp_code"]))
        else:
            cursor.execute("""
                INSERT INTO employees (emp_code, name, email, department, title, manager_name, hire_date, salary, status, leave_balance, phone, emergency_contact, performance_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (e["emp_code"], e["name"], e["email"], e["department"], e["title"], e["manager_name"], e["hire_date"], e["salary"], e["status"], e["leave_balance"], e["phone"], e["emergency_contact"], e["performance_rating"]))

    # 3. Leave Requests
    for r in LEAVE_REQUESTS_DATA:
        cursor.execute("SELECT id FROM leave_requests WHERE req_code = ?", (r["req_code"],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO leave_requests (req_code, emp_name, leave_type, start_date, end_date, days_requested, reason, status, approver_notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (r["req_code"], r["emp_name"], r["leave_type"], r["start_date"], r["end_date"], r["days_requested"], r["reason"], r["status"], r["approver_notes"], r["created_at"]))

    # 4. Invoices
    for inv in INVOICES_DATA:
        cursor.execute("SELECT id FROM invoices WHERE invoice_number = ?", (inv["invoice_number"],))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE invoices SET vendor_name=?, invoice_type=?, amount=?, currency=?, due_date=?, status=?, notes=?, created_at=?
                WHERE invoice_number=?
            """, (inv["vendor_name"], inv["invoice_type"], inv["amount"], inv["currency"], inv["due_date"], inv["status"], inv["notes"], inv["created_at"], inv["invoice_number"]))
        else:
            cursor.execute("""
                INSERT INTO invoices (invoice_number, vendor_name, invoice_type, amount, currency, due_date, status, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (inv["invoice_number"], inv["vendor_name"], inv["invoice_type"], inv["amount"], inv["currency"], inv["due_date"], inv["status"], inv["notes"], inv["created_at"]))

    # 5. Support Tickets
    for t in SUPPORT_TICKETS_DATA:
        cursor.execute("SELECT id FROM support_tickets WHERE ticket_number = ?", (t["ticket_number"],))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE support_tickets SET customer_name=?, requester_email=?, category=?, priority=?, subject=?, description=?, status=?, assignee=?, resolution_notes=?, created_at=?, sla_due=?
                WHERE ticket_number=?
            """, (t["customer_name"], t["requester_email"], t["category"], t["priority"], t["subject"], t["description"], t["status"], t["assignee"], t["resolution_notes"], t["created_at"], t["sla_due"], t["ticket_number"]))
        else:
            cursor.execute("""
                INSERT INTO support_tickets (ticket_number, customer_name, requester_email, category, priority, subject, description, status, assignee, resolution_notes, created_at, sla_due)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (t["ticket_number"], t["customer_name"], t["requester_email"], t["category"], t["priority"], t["subject"], t["description"], t["status"], t["assignee"], t["resolution_notes"], t["created_at"], t["sla_due"]))

    # 6. Inventory
    for it in INVENTORY_DATA:
        cursor.execute("SELECT id FROM inventory WHERE sku = ?", (it["sku"],))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE inventory SET item_name=?, category=?, stock_on_hand=?, reorder_threshold=?, target_reorder_qty=?, unit_cost=?, supplier=?, warehouse_location=?
                WHERE sku=?
            """, (it["item_name"], it["category"], it["stock_on_hand"], it["reorder_threshold"], it["target_reorder_qty"], it["unit_cost"], it["supplier"], it["warehouse_location"], it["sku"]))
        else:
            cursor.execute("""
                INSERT INTO inventory (sku, item_name, category, stock_on_hand, reorder_threshold, target_reorder_qty, unit_cost, supplier, warehouse_location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (it["sku"], it["item_name"], it["category"], it["stock_on_hand"], it["reorder_threshold"], it["target_reorder_qty"], it["unit_cost"], it["supplier"], it["warehouse_location"]))

    # 7. Expense Reports
    for exp in EXPENSES_DATA:
        cursor.execute("SELECT id FROM expense_reports WHERE report_number = ?", (exp["report_number"],))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE expense_reports SET employee_name=?, department=?, category=?, amount=?, merchant=?, expense_date=?, status=?, notes=?, receipt_ref=?
                WHERE report_number=?
            """, (exp["employee_name"], exp["department"], exp["category"], exp["amount"], exp["merchant"], exp["expense_date"], exp["status"], exp["notes"], exp["receipt_ref"], exp["report_number"]))
        else:
            cursor.execute("""
                INSERT INTO expense_reports (report_number, employee_name, department, category, amount, merchant, expense_date, status, notes, receipt_ref)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (exp["report_number"], exp["employee_name"], exp["department"], exp["category"], exp["amount"], exp["merchant"], exp["expense_date"], exp["status"], exp["notes"], exp["receipt_ref"]))

    # 8. Customers CRM
    for c in CUSTOMERS_DATA:
        cursor.execute("SELECT id FROM customers WHERE customer_code = ?", (c["customer_code"],))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE customers SET company_name=?, industry=?, contract_tier=?, annual_contract_value=?, account_executive=?, status=?, health_score=?, primary_contact=?
                WHERE customer_code=?
            """, (c["company_name"], c["industry"], c["contract_tier"], c["annual_contract_value"], c["account_executive"], c["status"], c["health_score"], c["primary_contact"], c["customer_code"]))
        else:
            cursor.execute("""
                INSERT INTO customers (customer_code, company_name, industry, contract_tier, annual_contract_value, account_executive, status, health_score, primary_contact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (c["customer_code"], c["company_name"], c["industry"], c["contract_tier"], c["annual_contract_value"], c["account_executive"], c["status"], c["health_score"], c["primary_contact"]))

    # 9. Deals
    for dl in DEALS_DATA:
        cursor.execute("SELECT id FROM deals WHERE deal_name = ?", (dl["deal_name"],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO deals (deal_name, customer_name, stage, deal_value, close_date, probability_pct)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (dl["deal_name"], dl["customer_name"], dl["stage"], dl["deal_value"], dl["close_date"], dl["probability_pct"]))

    # 10. Purchase Orders
    for po in PURCHASE_ORDERS_DATA:
        cursor.execute("SELECT id FROM purchase_orders WHERE po_number = ?", (po["po_number"],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO purchase_orders (po_number, supplier, items_summary, total_cost, status, created_at, delivery_expected)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (po["po_number"], po["supplier"], po["items_summary"], po["total_cost"], po["status"], po["created_at"], po["delivery_expected"]))

    conn.commit()

    # Print summary counts from DB
    counts = {}
    for tbl in ["departments", "employees", "leave_requests", "invoices", "support_tickets", "inventory", "expense_reports", "customers", "deals", "purchase_orders"]:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
        counts[tbl] = cursor.fetchone()[0]

    conn.close()

    print("\n[SUCCESS] SQLite Database successfully populated with Big Dataset:")
    for tbl, cnt in counts.items():
        print(f"  - {tbl:<20}: {cnt} records")

def main():
    print("=================================================================")
    print("CENTRALIGN TECHNOLOGIES — BIG ENTERPRISE DATASET CREATION")
    print("=================================================================")
    generate_all_single_file_tables()
    generate_unified_enterprise_dataset()
    generate_master_invoices_document()
    seed_big_dataset_to_sqlite()
    print("\n=================================================================")
    print("BIG DATASET GENERATION COMPLETED SUCCESSFULLY FOR ALL DOMAINS!")
    print("=================================================================")

if __name__ == "__main__":
    main()
