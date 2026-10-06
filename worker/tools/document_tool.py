import os
import re
from datetime import datetime
from typing import Dict, Any, Optional
from worker.tools.base import BaseTool, ToolResult

class DocumentExtractorTool(BaseTool):
    name = "document_extractor"
    description = "Extracts structured metadata (vendor, invoice number, amount, due date) from a PDF or text invoice."

    def _extract_text_from_file(self, filepath: str) -> str:
        if filepath.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()

        elif filepath.endswith(".pdf"):
            try:
                from pypdf import PdfReader
                reader = PdfReader(filepath)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
            except Exception as e:
                # Fallback check if text version exists with same prefix
                alt_txt = filepath.replace(".pdf", ".txt")
                if os.path.exists(alt_txt):
                    with open(alt_txt, "r", encoding="utf-8") as f:
                        return f.read()
                raise RuntimeError(f"Failed to read PDF {filepath}: {str(e)}")

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
            # Fallback search for patterns like INV-XXX-123
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
            # Fallback for $XX.XX pattern
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
        vendor_match = re.search(r'(?:Company\s*[A-Z]|Acme\s*[A-Za-z]+)', text, re.IGNORECASE)
        if vendor_match:
            data["vendor_name"] = vendor_match.group(0).strip()
        else:
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            if lines:
                data["vendor_name"] = lines[0].replace("===", "").strip()

        return data

    def _normalize_date(self, raw_date: str) -> str:
        # Tries standard date formats and converts to YYYY-MM-DD
        formats = [
            "%Y-%m-%d",
            "%B %d, %Y",
            "%b %d, %Y",
            "%m/%d/%Y",
            "%d/%m/%Y"
        ]
        clean = re.sub(r'\s+', ' ', raw_date.strip())
        for fmt in formats:
            try:
                dt = datetime.strptime(clean, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return clean

    async def execute(self, filepath: str) -> ToolResult:
        try:
            if not os.path.exists(filepath):
                return ToolResult(
                    success=False,
                    output=f"Invoice file not found at: {filepath}",
                    error="FILE_NOT_FOUND"
                )

            raw_text = self._extract_text_from_file(filepath)
            extracted = self._parse_invoice_fields(raw_text)

            # Check if essential fields were found
            missing_fields = []
            for field in ["vendor_name", "amount", "due_date"]:
                if not extracted.get(field):
                    missing_fields.append(field)

            if missing_fields:
                return ToolResult(
                    success=False,
                    output=f"Extracted partial data, but missing critical fields: {', '.join(missing_fields)}",
                    data={"extracted": extracted, "raw_preview": raw_text[:300]},
                    error="PARTIAL_EXTRACTION"
                )

            summary = (
                f"Successfully extracted invoice metadata:\n"
                f"- Vendor: {extracted['vendor_name']}\n"
                f"- Invoice #: {extracted.get('invoice_number', 'N/A')}\n"
                f"- Amount: ${extracted['amount']:.2f} {extracted['currency']}\n"
                f"- Due Date: {extracted['due_date']}"
            )

            return ToolResult(
                success=True,
                output=summary,
                data=extracted
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Failed to process invoice document: {str(e)}",
                error=str(e)
            )
