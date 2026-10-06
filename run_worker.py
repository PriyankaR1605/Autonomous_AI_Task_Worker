import sys
import asyncio

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from worker.agent import AutonomousWorker
from worker.state import ApprovalRequest

def human_approval_prompt(req: ApprovalRequest) -> bool:
    print("\n" + "=" * 65)
    print("[!] HUMAN-IN-THE-LOOP APPROVAL REQUIRED")
    print(f"Reason: {req.reason}")
    print(f"Proposed Action: {req.proposed_action}")
    print(f"Details: {req.details}")
    print("=" * 65)
    
    # In interactive CLI mode:
    try:
        choice = input("Approve this action? (y/n) [default: y]: ").strip().lower()
        return choice in ("", "y", "yes")
    except EOFError:
        # Non-interactive CLI fallback
        print("Non-interactive session detected. Auto-approving under supervisor policy.")
        return True

async def main():
    default_prompt = "Find the latest invoice from Company X, extract the amount and due date, enter it into our internal system, and tell me once it is done."
    prompt = sys.argv[1] if len(sys.argv) > 1 else default_prompt

    print("=" * 65)
    print("[AI] CENTRALIGN AUTONOMOUS AI TASK WORKER")
    print(f"Target Goal: \"{prompt}\"")
    print("=" * 65)

    worker = AutonomousWorker(
        user_prompt=prompt,
        approval_callback=human_approval_prompt,
        use_browser=True
    )

    state = await worker.run()

    print("\n" + "=" * 65)
    print("[REPORT] FINAL EXECUTION SUMMARY & VERIFICATION DOSSIER")
    print(f"Status: {state.status.value}")
    print(state.final_summary)
    if state.evidence_report_path:
        print(f"\nAudit Report: {state.evidence_report_path}")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(main())
