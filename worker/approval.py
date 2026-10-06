from typing import Dict, Any, Optional
from worker.config import settings
from worker.state import ApprovalRequest

class ApprovalGate:
    """
    Evaluates actions against safety policies and triggers Human-in-the-Loop (HITL) checkpoints.
    """

    @staticmethod
    def evaluate_financial_risk(extracted_data: Dict[str, Any]) -> ApprovalRequest:
        amount = extracted_data.get("amount", 0.0)
        vendor = extracted_data.get("vendor_name", "Unknown Vendor")
        threshold = settings.HIGH_RISK_AMOUNT_THRESHOLD

        if amount > threshold:
            return ApprovalRequest(
                required=True,
                reason=f"High Financial Value: Invoice amount (${amount:,.2f}) exceeds autonomous approval limit of ${threshold:,.2f}.",
                proposed_action=f"Submit invoice #{extracted_data.get('invoice_number', 'N/A')} for {vendor} into internal ERP.",
                details={
                    "vendor": vendor,
                    "invoice_number": extracted_data.get("invoice_number"),
                    "amount": amount,
                    "due_date": extracted_data.get("due_date"),
                    "threshold": threshold
                }
            )

        return ApprovalRequest(
            required=False,
            reason="Within autonomous safety threshold.",
            proposed_action="Proceed automatically with ERP registration.",
            details={"amount": amount, "threshold": threshold}
        )

    @staticmethod
    def evaluate_file_ambiguity(matches: list) -> ApprovalRequest:
        if len(matches) > 1 and matches[0]["priority_score"] == matches[1]["priority_score"]:
            return ApprovalRequest(
                required=True,
                reason="Multiple candidate files found with identical priority score. Human clarification required.",
                proposed_action=f"Select best file among: {[m['filename'] for m in matches[:3]]}",
                details={"candidates": [m["filename"] for m in matches]}
            )
        return ApprovalRequest(required=False, reason="Unambiguous file match.", proposed_action="Proceed", details={})
