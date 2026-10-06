import httpx
from typing import Optional, Dict, Any
from worker.config import settings
from worker.tools.base import BaseTool, ToolResult

class ErpApiTool(BaseTool):
    name = "erp_api"
    description = "Direct programmatic REST API interface for internal enterprise ERP portal."

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.MOCK_ERP_BASE_URL).rstrip("/")

    async def execute(self, action: str, **kwargs) -> ToolResult:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if action == "health":
                    resp = await client.get(f"{self.base_url}/api/health")
                    return ToolResult(
                        success=resp.status_code == 200,
                        output=f"ERP API health status: {resp.status_code}",
                        data=resp.json() if resp.status_code == 200 else {}
                    )

                elif action == "create_invoice":
                    payload = {
                        "vendor_name": kwargs.get("vendor_name"),
                        "invoice_number": kwargs.get("invoice_number"),
                        "amount": float(kwargs.get("amount", 0)),
                        "due_date": kwargs.get("due_date"),
                        "currency": kwargs.get("currency", "USD"),
                        "notes": kwargs.get("notes", "Entered via AI Task Worker API")
                    }
                    resp = await client.post(f"{self.base_url}/api/invoices", json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return ToolResult(
                            success=True,
                            output=f"Successfully created invoice {payload['invoice_number']} via API.",
                            data=data
                        )
                    else:
                        return ToolResult(
                            success=False,
                            output=f"ERP API returned error {resp.status_code}: {resp.text}",
                            error=resp.text
                        )

                elif action == "verify_invoice":
                    vendor = kwargs.get("vendor_name")
                    amount = float(kwargs.get("amount", 0))
                    resp = await client.get(
                        f"{self.base_url}/api/invoices/verify",
                        params={"vendor": vendor, "amount": amount}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        verified = data.get("verified", False)
                        return ToolResult(
                            success=verified,
                            output=data.get("message", "Verification completed."),
                            data=data
                        )
                    return ToolResult(
                        success=False,
                        output=f"Failed to query verification endpoint: {resp.text}",
                        error=resp.text
                    )

                elif action == "list_invoices":
                    resp = await client.get(f"{self.base_url}/api/invoices")
                    if resp.status_code == 200:
                        data = resp.json()
                        return ToolResult(
                            success=True,
                            output=f"Retrieved {len(data.get('invoices', []))} invoices from ERP.",
                            data=data
                        )
                    return ToolResult(
                        success=False,
                        output=f"Failed to list invoices: {resp.text}",
                        error=resp.text
                    )

                else:
                    return ToolResult(
                        success=False,
                        output=f"Unknown ERP API action: {action}",
                        error="UNKNOWN_ACTION"
                    )

        except Exception as e:
            return ToolResult(
                success=False,
                output=f"ERP API communication error: {str(e)}",
                error=str(e)
            )
