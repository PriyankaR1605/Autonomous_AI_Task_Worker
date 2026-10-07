import os
import sys
import asyncio

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from mock_erp.database import init_db
from worker.config import settings
from worker.agent import AutonomousWorker

settings.STEP_DELAY_SECONDS = 0.05

async def test_no_data_found_scenarios():
    print("=" * 70)
    print("VERIFYING 'NO DATA FOUND' RESPONSES FOR NON-EXISTENT ENTERPRISE ENTITIES")
    print("=" * 70)

    init_db()

    test_queries = [
        {
            "name": "Non-existent Employee",
            "domain": "hr_leave",
            "prompt": "Find employee Zlatan Nonexistent, check his remaining annual leave balance, and approve his pending request."
        },
        {
            "name": "Non-existent Vendor Invoice",
            "domain": "invoice",
            "prompt": "Find the latest invoice from Ghost Enterprise Ltd, extract amount and due date, and enter it into our ERP."
        },
        {
            "name": "Non-existent Ticket ID",
            "domain": "ticket",
            "prompt": "Check incident ticket TCK-99999 and reassign to Alex Wong."
        },
        {
            "name": "Non-existent Inventory SKU",
            "domain": "inventory",
            "prompt": "Check inventory warehouse stock for SKU-999-DOESNOTEXIST and calculate restock requirements."
        },
        {
            "name": "Non-existent Department Budget",
            "domain": "budget",
            "prompt": "Calculate Q3 expenditure and variance for Quantum Physics Department."
        },
        {
            "name": "Non-existent Expense Claim",
            "domain": "expense",
            "prompt": "Audit expense report EXP-99999 against travel policy and approve."
        }
    ]

    all_passed = True

    for idx, tc in enumerate(test_queries, 1):
        print(f"\n[{idx}/{len(test_queries)}] Testing: {tc['name']}")
        print(f"Query: \"{tc['prompt']}\"")

        worker = AutonomousWorker(
            user_prompt=tc["prompt"],
            domain=tc["domain"],
            use_browser=False
        )

        state = await worker.run()

        summary = state.final_summary or ""
        print(f"Summary excerpt: {summary[:120]}...")

        # Assert that 'No Data Found' is present in summary or working_memory
        has_no_data = (
            "no data found" in summary.lower() or
            state.working_memory.get("not_found") is True or
            state.retrieved_data.get("entity_found") is False or
            state.retrieved_data.get("search_status") == "NO_DATA_FOUND"
        )

        if has_no_data:
            print(f"-> Result: PASS ('No data found' verified)")
        else:
            print(f"-> Result: FAIL (Expected 'No data found', got: {summary[:200]})")
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("ALL 'NO DATA FOUND' TESTS PASSED PERFECTLY!")
    else:
        print("SOME TESTS FAILED.")
    print("=" * 70)
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(test_no_data_found_scenarios())
    sys.exit(0 if success else 1)
