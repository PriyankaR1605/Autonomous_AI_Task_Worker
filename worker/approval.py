from typing import Dict, Any, Optional
from worker.config import settings
from worker.state import ApprovalRequest

class ApprovalGate:
    """
    Evaluates proposed actions against safety guardrails and triggers
    Human-in-the-Loop (HITL) checkpoints before executing sensitive operations.
    """

    @staticmethod
    def evaluate_financial_risk(data: Dict[str, Any], context_label: str = "Invoice") -> ApprovalRequest:
        amount = float(data.get("amount") or data.get("total_cost") or 0.0)
        threshold = settings.HIGH_RISK_AMOUNT_THRESHOLD
        vendor = data.get("vendor_name") or data.get("supplier") or "Enterprise Counterparty"

        if amount > threshold:
            return ApprovalRequest(
                required=True,
                reason=f"High Financial Exposure: {context_label} value (${amount:,.2f} USD) exceeds autonomous approval limit of ${threshold:,.2f} USD.",
                proposed_action=f"Execute {context_label.lower()} transaction with {vendor} for ${amount:,.2f} USD into general ledger.",
                details={
                    "type": context_label,
                    "party": vendor,
                    "amount": amount,
                    "threshold": threshold,
                    "data": data
                }
            )

        return ApprovalRequest(
            required=False,
            reason=f"Financial value (${amount:,.2f}) is within autonomous safety limit (${threshold:,.2f}).",
            proposed_action=f"Proceed automatically with {context_label.lower()} recording.",
            details={"amount": amount, "threshold": threshold}
        )

    @staticmethod
    def evaluate_hr_risk(data: Dict[str, Any]) -> ApprovalRequest:
        emp_name = data.get("name") or data.get("emp_name") or "Employee"
        
        # Check if salary modification is proposed
        if "salary" in data:
            new_salary = float(data["salary"])
            return ApprovalRequest(
                required=True,
                reason=f"Sensitive HR Modification: Altering compensation package for {emp_name} to ${new_salary:,.2f} requires executive sign-off.",
                proposed_action=f"Update payroll record for {emp_name} to annual salary of ${new_salary:,.2f}.",
                details={"employee": emp_name, "new_salary": new_salary}
            )

        if "status" in data and data["status"].upper() in ("TERMINATED", "SUSPENDED"):
            return ApprovalRequest(
                required=True,
                reason=f"Critical HR Action: Modifying employment status of {emp_name} to '{data['status']}' requires VP of People approval.",
                proposed_action=f"Change employment status for {emp_name}.",
                details={"employee": emp_name, "status": data["status"]}
            )

        return ApprovalRequest(
            required=False,
            reason="Routine HR operation within policy guidelines.",
            proposed_action="Proceed automatically",
            details={}
        )

    @staticmethod
    def evaluate_generic_action(action_name: str, payload: Dict[str, Any]) -> ApprovalRequest:
        """Universal policy evaluator routing to domain-specific guards."""
        if any(k in payload for k in ("amount", "total_cost")):
            return ApprovalGate.evaluate_financial_risk(payload, context_label=action_name)
        if any(k in payload for k in ("salary", "performance_rating")):
            return ApprovalGate.evaluate_hr_risk(payload)
        return ApprovalRequest(required=False, reason="Action cleared under standard autonomous policy.", proposed_action="Execute", details={})
