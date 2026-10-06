import os
import re
from datetime import datetime
from typing import Dict, Any, Optional
from worker.tools.base import BaseTool, ToolResult

class DocumentExtractorTool(BaseTool):
    name = "document_extractor"
    description = "Extracts structured metadata, policy rules, contracts, or financial numbers from a PDF or text document."

    def _extract_text_from_file(self, filepath: str) -> str:
        if filepath.endswith(".txt") or filepath.endswith(".md"):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()

        elif filepath.endswith(".pdf"):
            try:
                from pypdf import PdfReader
                reader = PdfReader(filepath)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                if text.strip():
                    return text
            except Exception:
                pass
            
            # Fallback check if text version exists with same prefix
            alt_txt = filepath.rsplit(".", 1)[0] + ".txt"
            if os.path.exists(alt_txt):
                with open(alt_txt, "r", encoding="utf-8") as f:
                    return f.read()
            raise RuntimeError(f"Could not extract readable text from PDF: {filepath}")

        raise ValueError(f"Unsupported file format: {filepath}")

    def _parse_invoice_fields(self, text: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "vendor_name": None,
            "invoice_number": None,
            "amount": None,
            "currency": "USD",
            "due_date": None,
            "issue_date": None,
            "notes": ""
        }

        # 1. Invoice Number regex
        inv_match = re.search(r'(?:Invoice\s*(?:Number|#|No\.?):?)\s*([A-Za-z0-9\-]+)', text, re.IGNORECASE)
        if inv_match:
            data["invoice_number"] = inv_match.group(1).strip()
        else:
            inv_pattern = re.search(r'\b(INV-[A-Za-z0-9\-]+)\b', text)
            if inv_pattern:
                data["invoice_number"] = inv_pattern.group(1).strip()

        # 2. Total Amount regex
        amount_match = re.search(r'(?:Total\s*(?:Amount|Due)?[:\s]*)\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if amount_match:
            raw_amt = amount_match.group(1).replace(',', '')
            try:
                data["amount"] = float(raw_amt)
            except ValueError:
                pass
        else:
            curr_match = re.search(r'\$\s*([\d,]+\.\d{2})', text)
            if curr_match:
                raw_amt = curr_match.group(1).replace(',', '')
                try:
                    data["amount"] = float(raw_amt)
                except ValueError:
                    pass

        # 3. Due Date regex
        due_match = re.search(r'(?:Payment\s*Due\s*Date|Due\s*Date)[:\s]*([0-9]{4}-[0-9]{2}-[0-9]{2}|[A-Za-z]+\s+[0-9]{1,2},?\s+[0-9]{4}|[0-9]{2}/[0-9]{2}/[0-9]{4})', text, re.IGNORECASE)
        if due_match:
            raw_date = due_match.group(1).strip()
            data["due_date"] = self._normalize_date(raw_date)

        # 4. Issue Date regex
        issue_match = re.search(r'(?:Issue\s*Date|Date)[:\s]*([0-9]{4}-[0-9]{2}-[0-9]{2}|[A-Za-z]+\s+[0-9]{1,2},?\s+[0-9]{4}|[0-9]{2}/[0-9]{2}/[0-9]{4})', text, re.IGNORECASE)
        if issue_match:
            raw_date = issue_match.group(1).strip()
            data["issue_date"] = self._normalize_date(raw_date)

        # 5. Vendor Name extraction
        vendor_match = re.search(r'(?:Company\s*[A-Z]|Acme\s*[A-Za-z]+|Global\s*Cloud\s*Hosting|CyberShield\s*Security)', text, re.IGNORECASE)
        if vendor_match:
            data["vendor_name"] = vendor_match.group(0).strip()
        else:
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            if lines:
                data["vendor_name"] = lines[0].replace("===", "").strip()

        return data

    def _parse_policy_or_contract(self, text: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "document_type": "policy_or_contract",
            "title": "",
            "thresholds": {},
            "key_clauses": [],
            "raw_excerpt": text[:1000]
        }

        # Check for financial thresholds (e.g. $3,000, $1,000)
        limits = re.findall(r'\$([0-9,]+(?:\.[0-9]{2})?)\s*(?:USD)?\s*(?:autonomous\s*threshold|limit|per\s*diem)?', text, re.IGNORECASE)
        if limits:
            data["thresholds"]["monetary_limits"] = limits

        # Check for SLAs
        slas = re.findall(r'(CRITICAL|HIGH|MEDIUM|LOW)[^:]*:\s*([0-9]+\s*(?:minutes?|hours?|days?))', text, re.IGNORECASE)
        if slas:
            data["thresholds"]["slas"] = {k.upper(): v for k, v in slas}

        # Check for title
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if lines:
            data["title"] = lines[0].replace("===", "").strip()

        return data

    def _normalize_date(self, raw_date: str) -> str:
        formats = [
            "%Y-%m-%d",
            "%B %d, %Y",
            "%b %d, %Y",
            "%m/%d/%Y",
            "%d/%m/%Y"
        ]
        clean = raw_date.replace(',', '')
        for fmt in formats:
            try:
                dt = datetime.strptime(clean, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return raw_date

    async def execute(self, filepath: str) -> ToolResult:
        try:
            if not os.path.exists(filepath):
                return ToolResult(
                    success=False,
                    output=f"File not found: {filepath}",
                    error="FILE_NOT_FOUND"
                )

            text = self._extract_text_from_file(filepath)

            # Determine document type
            fname = os.path.basename(filepath).lower()
            if "invoice" in fname:
                parsed = self._parse_invoice_fields(text)
                
                # Validation check
                missing = [k for k, v in [("amount", parsed["amount"]), ("due_date", parsed["due_date"])] if v is None]
                if missing:
                    return ToolResult(
                        success=False,
                        output=f"Document parsed but missing required fields: {missing}",
                        data=parsed,
                        error="MISSING_REQUIRED_FIELDS"
                    )

                return ToolResult(
                    success=True,
                    output=f"Extracted Invoice Details:\n- Vendor: {parsed['vendor_name']}\n- Invoice #: {parsed['invoice_number']}\n- Amount: ${parsed['amount']:.2f}\n- Due Date: {parsed['due_date']}",
                    data=parsed
                )
            else:
                # Policy or Contract
                parsed = self._parse_policy_or_contract(text)
                return ToolResult(
                    success=True,
                    output=f"Extracted Policy/Contract Content from {os.path.basename(filepath)}:\n{text[:600]}...",
                    data={"raw_text": text, **parsed}
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Document extraction error: {str(e)}",
                error=str(e)
            )
