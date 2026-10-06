import httpx
from typing import Optional, Dict, Any
from worker.config import settings
from worker.tools.base import BaseTool, ToolResult

class ErpApiTool(BaseTool):
    name = "erp_api"
    description = "Programmatic REST API interface for all CentrAlign enterprise modules (Invoices, Tickets, HR, Inventory, Expenses, Verification)."

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

                # INVOICES
                elif action == "create_invoice":
                    payload = {
                        "vendor_name": kwargs.get("vendor_name"),
                        "invoice_number": kwargs.get("invoice_number"),
                        "amount": float(kwargs.get("amount", 0)),
                        "due_date": kwargs.get("due_date"),
                        "currency": kwargs.get("currency", "USD"),
                        "notes": kwargs.get("notes", "Entered via AI Task Worker API"),
                        "invoice_type": kwargs.get("invoice_type", "PAYABLE")
                    }
                    resp = await client.post(f"{self.base_url}/api/invoices", json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return ToolResult(
                            success=True,
                            output=f"Successfully created invoice {payload['invoice_number']} via API.",
                            data=data
                        )
                    return ToolResult(success=False, output=f"ERP API returned error {resp.status_code}: {resp.text}", error=resp.text)

                elif action == "list_invoices":
                    resp = await client.get(f"{self.base_url}/api/invoices")
                    if resp.status_code == 200:
                        data = resp.json()
                        return ToolResult(
                            success=True,
                            output=f"Retrieved {len(data.get('invoices', []))} invoices from ERP.",
                            data=data
                        )
                    return ToolResult(success=False, output=f"Failed to list invoices: {resp.text}", error=resp.text)

                # TICKETS
                elif action == "list_tickets":
                    params = {}
                    if "status" in kwargs: params["status"] = kwargs["status"]
                    if "priority" in kwargs: params["priority"] = kwargs["priority"]
                    resp = await client.get(f"{self.base_url}/api/tickets", params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        return ToolResult(
                            success=True,
                            output=f"Retrieved {data.get('count', 0)} tickets matching filters.",
                            data=data
                        )
                    return ToolResult(success=False, output=f"Failed to fetch tickets: {resp.text}", error=resp.text)

                elif action == "update_ticket":
                    ticket_no = kwargs.get("ticket_number")
                    payload = {
                        "status": kwargs.get("status"),
                        "assignee": kwargs.get("assignee"),
                        "resolution_notes": kwargs.get("resolution_notes")
                    }
                    resp = await client.patch(f"{self.base_url}/api/tickets/{ticket_no}", json=payload)
                    if resp.status_code == 200:
                        return ToolResult(
                            success=True,
                            output=f"Successfully updated ticket {ticket_no} via API.",
                            data=resp.json()
                        )
                    return ToolResult(success=False, output=f"Failed to update ticket: {resp.text}", error=resp.text)

                # HR & EMPLOYEES
                elif action == "get_employee":
                    ident = kwargs.get("identifier") or kwargs.get("name")
                    resp = await client.get(f"{self.base_url}/api/employees/{ident}")
                    if resp.status_code == 200:
                        return ToolResult(success=True, output=f"Retrieved employee {ident}", data=resp.json())
                    return ToolResult(success=False, output=f"Employee {ident} not found", error=resp.text)

                elif action == "action_leave_request":
                    ident = kwargs.get("identifier") or kwargs.get("emp_name")
                    payload = {
                        "status": kwargs.get("status", "APPROVED"),
                        "notes": kwargs.get("notes", "Approved via Autonomous AI Worker")
                    }
                    resp = await client.post(f"{self.base_url}/api/leave-requests/{ident}/action", json=payload)
                    if resp.status_code == 200:
                        return ToolResult(success=True, output=f"Leave request updated: {resp.json()}", data=resp.json())
                    return ToolResult(success=False, output=f"Failed to update leave request: {resp.text}", error=resp.text)

                # INVENTORY
                elif action == "create_po":
                    payload = {
                        "supplier": kwargs.get("supplier"),
                        "items_summary": kwargs.get("items_summary"),
                        "total_cost": float(kwargs.get("total_cost", 0.0)),
                        "delivery_expected": kwargs.get("delivery_expected", "")
                    }
                    resp = await client.post(f"{self.base_url}/api/purchase-orders", json=payload)
                    if resp.status_code == 200:
                        return ToolResult(success=True, output=f"Purchase order created: {resp.json()}", data=resp.json())
                    return ToolResult(success=False, output=f"Failed to create PO: {resp.text}", error=resp.text)

                # UNIVERSAL VERIFY
                elif action == "verify":
                    payload = {
                        "entity_type": kwargs.get("entity_type", "invoice"),
                        "criteria": kwargs.get("criteria", {})
                    }
                    resp = await client.post(f"{self.base_url}/api/verify", json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return ToolResult(
                            success=data.get("verified", False),
                            output=data.get("message", "Verification query complete."),
                            data=data
                        )
                    return ToolResult(success=False, output=f"Verification API error: {resp.text}", error=resp.text)

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
