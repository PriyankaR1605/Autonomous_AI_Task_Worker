import os
import sys
import asyncio

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mock_erp.database import init_db, reset_test_records, get_all_invoices, get_connection
from scripts.generate_sample_invoices import main as generate_invoices
from worker.agent import AutonomousWorker
from worker.state import TaskStatus

async def run_integration_test():
    print("\n--- [1/4] Initializing Mock ERP Database ---")
    init_db()
    reset_test_records()
    print("Database initialized & test records reset.")

    print("\n--- [2/4] Generating Sample Invoices ---")
    generate_invoices()
    print("Invoices generated.")

    prompt = "Find the latest invoice from Company X, extract the amount and due date, enter it into our internal system, and tell me once it is done."
    print(f"\n--- [3/4] Launching Autonomous Worker with Goal: '{prompt}' ---")
    
    # We run with use_browser=False for instant headless API-driven verification during test,
    # or use_browser=True if playwright browser is installed.
    worker = AutonomousWorker(
        user_prompt=prompt,
        use_browser=False  # Direct API pathway for continuous integration testing
    )

    state = await worker.run()

    print("\n--- [4/4] Verifying Worker Execution Results ---")
    print(f"Task ID: {state.task_id}")
    print(f"Final Status: {state.status.value}")
    print(f"Final Summary:\n{state.final_summary}\n")

    assert state.status == TaskStatus.COMPLETED, f"Expected COMPLETED status, got {state.status}"
    assert state.working_memory.get("vendor_name") == "Company X"
    assert state.working_memory.get("amount") == 4850.00
    assert state.working_memory.get("due_date") == "2026-11-15"
    assert state.verification is not None
    assert state.verification.verified is True, "Independent verification check failed!"
    assert state.evidence_report_path is not None
    print("[SUCCESS] ALL INTEGRATION ASSERTIONS PASSED PERFECTLY!")

if __name__ == "__main__":
    asyncio.run(run_integration_test())
