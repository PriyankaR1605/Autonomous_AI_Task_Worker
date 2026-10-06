from typing import Dict, Any, List
from worker.state import VerificationResult
from mock_erp.database import verify_invoice_record, get_invoice_by_number

class OutcomeVerifier:
    """
    Performs independent post-execution assertions to prove that the requested
    business outcome was faithfully recorded in the destination enterprise system.
    """

    @staticmethod
    def verify(source_data: Dict[str, Any]) -> VerificationResult:
        vendor = source_data.get("vendor_name", "")
        expected_amount = float(source_data.get("amount", 0.0))
        expected_due_date = source_data.get("due_date", "")
        invoice_number = source_data.get("invoice_number", "")

        discrepancies: List[str] = []

        # 1. Query target system
        record = None
        if invoice_number:
            record = get_invoice_by_number(invoice_number)
        
        if not record:
            record = verify_invoice_record(vendor, expected_amount)

        if not record:
            return VerificationResult(
                verified=False,
                source_values=source_data,
                target_values={},
                discrepancies=[f"No record found in ERP for vendor '{vendor}' with amount ${expected_amount:.2f}."],
                verification_message="Verification FAILED: Target ERP record does not exist."
            )

        # 2. Check amount match
        actual_amount = float(record.get("amount", 0.0))
        if abs(actual_amount - expected_amount) > 0.01:
            discrepancies.append(f"Amount mismatch: Source has ${expected_amount:.2f}, ERP record has ${actual_amount:.2f}")

        # 3. Check due date match if present
        actual_due_date = record.get("due_date", "")
        if expected_due_date and actual_due_date != expected_due_date:
            discrepancies.append(f"Due date mismatch: Source has '{expected_due_date}', ERP record has '{actual_due_date}'")

        # 4. Check vendor name similarity
        actual_vendor = record.get("vendor_name", "")
        if vendor.lower() not in actual_vendor.lower() and actual_vendor.lower() not in vendor.lower():
            discrepancies.append(f"Vendor mismatch: Source has '{vendor}', ERP record has '{actual_vendor}'")

        is_verified = (len(discrepancies) == 0)
        msg = (
            f"Verification PASSED: Confirmed ERP record #{record.get('invoice_number')} matches source invoice data."
            if is_verified
            else f"Verification FAILED with {len(discrepancies)} discrepancies: " + "; ".join(discrepancies)
        )

        return VerificationResult(
            verified=is_verified,
            source_values=source_data,
            target_values=record,
            discrepancies=discrepancies,
            verification_message=msg
        )
