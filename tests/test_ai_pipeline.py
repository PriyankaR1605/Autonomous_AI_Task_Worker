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

from mock_erp.database import init_db, reset_test_records
from worker.agent import AutonomousWorker
from worker.state import TaskStatus
from worker.context_retriever import EnterpriseContextRetriever

async def test_hr_data_retrieval_and_ai_processing():
    print("\n--- TEST: HR Query & Task Data Feeding into AI Model ---")
    init_db()
    reset_test_records()

    prompt = "Find employee Sarah Jenkins, check her remaining annual leave balance, approve her pending vacation request, and update the HR system."
    worker = AutonomousWorker(
        user_prompt=prompt,
        use_browser=False
    )

    state = await worker.run()

    # Assertions
    assert state.status == TaskStatus.COMPLETED, f"Expected COMPLETED, got {state.status}"
    assert state.retrieved_data is not None, "Enterprise data was not retrieved!"
    assert "employees" in state.retrieved_data, "Employees not in retrieved HR data!"
    assert "leave_requests" in state.retrieved_data, "Leave requests not in retrieved HR data!"
    assert state.verification is not None and state.verification.verified is True, "Outcome verification failed!"
    assert "Sarah Jenkins" in state.final_summary, "Target employee missing from final summary!"
    assert state.model_used is not None, "Model used was not recorded!"

    print("-> Retrieved Data Keys:", list(state.retrieved_data.keys()))
    print(f"-> Total Employees Supplied to AI: {len(state.retrieved_data['employees'])}")
    print(f"-> AI Processing Engine: {state.model_used}")
    print(f"-> Verification: PASSED")
    print("\n[SUCCESS] HR Task & Data AI Processing Verified Perfectly!\n")

async def test_direct_context_retriever():
    print("\n--- TEST: Context Retriever Across All Domains ---")
    domains = ["hr", "invoice", "ticket", "inventory", "expense", "budget", "general"]
    for d in domains:
        data = EnterpriseContextRetriever.retrieve(d)
        assert data is not None, f"Failed to retrieve data for domain: {d}"
        assert "domain" in data, f"Missing domain label in data for: {d}"
        print(f"-> Domain: {d} -> Successfully loaded {len(data)} fields: {list(data.keys())[:4]}")
    print("\n[SUCCESS] All Domain Data Retrieval Verified Perfectly!\n")

async def main():
    await test_hr_data_retrieval_and_ai_processing()
    await test_direct_context_retriever()

if __name__ == "__main__":
    asyncio.run(main())
