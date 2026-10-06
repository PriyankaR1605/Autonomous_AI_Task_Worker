import os
import sys
import asyncio

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mock_erp.database import init_db, reset_test_records
from worker.config import settings
from worker.agent import AutonomousWorker
from worker.state import TaskStatus

# Set fast execution pace for tests
settings.STEP_DELAY_SECONDS = 0.2

async def run_all_enterprise_domain_tests():
    print("=" * 70)
    print("RUNNING CENTRALIGN ENTERPRISE MULTI-DOMAIN AUTONOMOUS WORKER TEST SUITE")
    print("=" * 70)

    init_db()
    reset_test_records()

    test_cases = [
        {
            "domain": "INVOICES & ACCOUNTS PAYABLE",
            "prompt": "Find the latest invoice from Company X, extract the amount and due date, enter it into our internal system, and tell me once it is done.",
            "expected_domain": "invoice",
            "verify_key": "amount",
            "verify_val": 4850.00
        },
        {
            "domain": "HR & EMPLOYEE LEAVE APPROVAL",
            "prompt": "Find employee Sarah Jenkins, check her remaining annual leave balance, approve her pending vacation request, and update the HR system.",
            "expected_domain": "hr_leave",
            "verify_key": "employee_name",
            "verify_val": "Sarah Jenkins"
        },
        {
            "domain": "IT & CUSTOMER SUPPORT HELPDESK",
            "prompt": "Scan all open customer support tickets, identify any CRITICAL priority tickets, reassign them to Senior Engineer Alex Wong, and mark them IN_PROGRESS.",
            "expected_domain": "ticket",
            "verify_key": "expected_assignee",
            "verify_val": "Alex Wong"
        },
        {
            "domain": "INVENTORY & REORDER PURCHASE ORDERS",
            "prompt": "Audit our inventory warehouse for all items below the reorder threshold, calculate restock requirements, and generate a purchase order to the preferred supplier.",
            "expected_domain": "inventory",
            "verify_key": "supplier",
            "verify_val": "Dell Enterprise Store"
        },
        {
            "domain": "EMPLOYEE EXPENSE POLICY AUDITING",
            "prompt": "Audit recent employee expense reports against our company travel and procurement policy, flag any unapproved expenses over $1,000, and request approval.",
            "expected_domain": "expense",
            "verify_key": "report_number",
            "verify_val": "EXP-2026-101"
        },
        {
            "domain": "DEPARTMENT BUDGET & FINANCIAL ANALYTICS",
            "prompt": "Calculate the total Q3 marketing expenditure, compare it against the allocated department budget, and report budget variance.",
            "expected_domain": "budget",
            "verify_key": "department",
            "verify_val": "Marketing & Growth"
        }
    ]

    passed_count = 0

    for idx, tc in enumerate(test_cases, 1):
        print(f"\n[{idx}/6] TESTING DOMAIN: {tc['domain']}")
        print(f"Goal: \"{tc['prompt']}\"")
        
        worker = AutonomousWorker(
            user_prompt=tc["prompt"],
            use_browser=False  # Headless API/DB pathway for CI speed
        )

        state = await worker.run()

        print(f"-> Task ID: {state.task_id}")
        print(f"-> Status: {state.status.value}")
        print(f"-> Milestones Completed: {sum(1 for m in state.milestones if m.status.value == 'SUCCESS')}/{len(state.milestones)}")
        print(f"-> Discovered Domain: {state.working_memory.get('domain')}")
        print(f"-> Verification: {'PASSED' if (state.verification and state.verification.verified) else 'FAILED'}")
        print(f"-> Evidence Dossier: {os.path.basename(state.evidence_report_path or '')}")

        assert state.status == TaskStatus.COMPLETED, f"Expected COMPLETED, got {state.status}"
        assert state.verification is not None and state.verification.verified is True, "Verification failed!"
        assert state.evidence_report_path is not None and os.path.exists(state.evidence_report_path), "Evidence dossier not generated!"
        
        passed_count += 1
        print(f"-> Result: PASS")

    print("\n" + "=" * 70)
    print(f"ALL {passed_count}/{len(test_cases)} ENTERPRISE DOMAIN TESTS COMPLETED AND VERIFIED PERFECTLY!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_all_enterprise_domain_tests())
