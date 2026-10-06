import math
from typing import Dict, Any, List, Optional
from worker.tools.base import BaseTool, ToolResult

class AnalyticsCalculationTool(BaseTool):
    name = "analytics_calculator"
    description = (
        "Performs calculations, budget variance analysis, inventory restock quantities, "
        "and financial aggregations."
    )

    async def execute(self, operation: str, **kwargs) -> ToolResult:
        try:
            if operation == "calculate_restock":
                # items: list of dicts with stock_on_hand, target_reorder_qty, unit_cost
                items = kwargs.get("items", [])
                total_cost = 0.0
                total_units = 0
                breakdown = []
                for it in items:
                    current = int(it.get("stock_on_hand", 0))
                    target = int(it.get("target_reorder_qty", 10))
                    qty_to_order = max(0, target - current)
                    unit_price = float(it.get("unit_cost", 0.0))
                    line_cost = qty_to_order * unit_price
                    total_cost += line_cost
                    total_units += qty_to_order
                    breakdown.append(f"{qty_to_order}x {it.get('item_name', 'Item')} @ ${unit_price:.2f} = ${line_cost:.2f}")

                return ToolResult(
                    success=True,
                    output=f"Restock Calculation: Total {total_units} units needed across {len(items)} items. Total estimated cost: ${total_cost:,.2f}.\nDetails:\n" + "\n".join(breakdown),
                    data={"total_units": total_units, "total_cost": total_cost, "breakdown": breakdown}
                )

            elif operation == "budget_variance":
                allocated = float(kwargs.get("budget", 0.0))
                actual = float(kwargs.get("spent", 0.0))
                variance = allocated - actual
                pct_used = (actual / allocated * 100) if allocated > 0 else 0.0
                status = "SURPLUS (Under Budget)" if variance >= 0 else "DEFICIT (Over Budget)"
                return ToolResult(
                    success=True,
                    output=f"Budget Analysis:\n- Allocated: ${allocated:,.2f}\n- Actual Spend: ${actual:,.2f}\n- Variance: ${variance:,.2f} ({status})\n- Utilization: {pct_used:.1f}%",
                    data={"allocated": allocated, "actual": actual, "variance": variance, "utilization_pct": pct_used}
                )

            elif operation == "sum_expenses":
                expenses = kwargs.get("expenses", [])
                total = sum(float(e.get("amount", 0.0)) for e in expenses)
                return ToolResult(
                    success=True,
                    output=f"Aggregated {len(expenses)} expense claims: Total = ${total:,.2f} USD",
                    data={"total": total, "count": len(expenses)}
                )

            elif operation == "eval_math":
                expr = kwargs.get("expression", "")
                # Safe eval of pure numbers and math operators
                clean = "".join(c for c in expr if c in "0123456789+-*/.() ")
                val = eval(clean, {"__builtins__": {}})
                return ToolResult(
                    success=True,
                    output=f"Calculation Result: {clean} = {val}",
                    data={"result": val}
                )

            else:
                return ToolResult(
                    success=False,
                    output=f"Unknown calculation operation: '{operation}'",
                    error="UNKNOWN_OPERATION"
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Calculation error: {str(e)}",
                error=str(e)
            )
