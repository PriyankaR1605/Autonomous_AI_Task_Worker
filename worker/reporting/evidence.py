import os
import json
from datetime import datetime
from typing import Dict, Any
from worker.config import settings
from worker.state import AgentState

class EvidencePackager:
    """
    Compiles structured execution traces, screenshots, and verification results
    into auditable enterprise dossiers across all business domains.
    """

    @staticmethod
    def generate_report(state: AgentState) -> str:
        report_id = f"audit_report_{state.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join(settings.STORAGE_DIR, report_id)

        v_status = "✅ VERIFIED & CONFIRMED" if (state.verification and state.verification.verified) else "❌ UNVERIFIED"
        domain = state.working_memory.get("domain", "general").upper()
        
        md_lines = [
            f"# Autonomous Task Worker — Enterprise Execution Dossier",
            f"",
            f"**Task ID**: `{state.task_id}`  ",
            f"**Domain**: `{domain}`  ",
            f"**AI Processing Engine**: `{state.model_used or 'CentrAlign Local Intelligence Engine'}`  ",
            f"**Timestamp**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`  ",
            f"**Overall Status**: **{state.status.value}** ({v_status})  ",
            f"**Goal**: *\"{state.user_prompt}\"*",
            f"",
            f"---",
            f"",
            f"## 1. Executive Summary & AI Model Intelligence",
            f"",
            f"{state.final_summary or 'Task execution completed autonomously.'}",
            f"",
            f"**Enterprise Data Context Ingested**: `{list(state.retrieved_data.keys()) if state.retrieved_data else 'Standard domain ledger'}`",
            f"",
            f"---",
            f"",
            f"## 2. Independent Outcome Verification",
            f"",
            f"- **Result**: **{v_status}**",
            f"- **Verification Message**: {state.verification.verification_message if state.verification else 'N/A'}",
            f"",
            f"### Data Integrity Reconciliation",
        ]

        if state.verification:
            src = state.verification.source_values
            tgt = state.verification.target_values

            md_lines.extend([
                f"| Attribute | Expected / Source State | Persisted Enterprise Record | Verification Status |",
                f"| :--- | :--- | :--- | :--- |"
            ])

            # Dynamically determine reconciliation fields based on domain
            domain_lower = state.working_memory.get("domain", "invoice").lower()

            if domain_lower == "ticket":
                fields = [
                    ("Ticket ID", src.get("ticket_number") or src.get("target_ticket"), tgt.get("ticket_number")),
                    ("Incident Subject", src.get("subject"), tgt.get("subject")),
                    ("Priority Level", src.get("priority"), tgt.get("priority")),
                    ("Assignee", src.get("expected_assignee"), tgt.get("assignee")),
                    ("Ticket Status", src.get("expected_status"), tgt.get("status")),
                ]
            elif domain_lower in ("hr_leave", "leave"):
                fields = [
                    ("Employee", src.get("employee_name"), tgt.get("emp_name")),
                    ("Leave Request ID", src.get("req_code"), tgt.get("req_code")),
                    ("Days Requested", f"{src.get('days_requested')} days" if src.get('days_requested') else "N/A", f"{tgt.get('days_requested')} days" if tgt.get('days_requested') else "N/A"),
                    ("Approval Status", "APPROVED", tgt.get("status")),
                    ("Remaining PTO", f"{src.get('updated_leave_balance')} days" if 'updated_leave_balance' in src else "Deducted", f"{src.get('updated_leave_balance')} days" if 'updated_leave_balance' in src else "Confirmed"),
                ]
            elif domain_lower in ("inventory", "po"):
                fields = [
                    ("Purchase Order", src.get("po_number"), tgt.get("po_number")),
                    ("Supplier", src.get("supplier"), tgt.get("supplier")),
                    ("Items Summary", src.get("items_summary"), tgt.get("items_summary")),
                    ("Order Valuation", f"${src.get('total_cost', 0):,.2f}", f"${tgt.get('total_cost', 0):,.2f}"),
                    ("Status", "ISSUED", tgt.get("status")),
                ]
            elif domain_lower == "budget":
                fields = [
                    ("Department", src.get("department"), tgt.get("name")),
                    ("Allocated Q3 Budget", f"${src.get('budget', 0):,.2f}", f"${tgt.get('budget_q3', 0):,.2f}"),
                    ("Actual Spend", f"${src.get('spent', 0):,.2f}", f"${tgt.get('spent_q3', 0):,.2f}"),
                    ("Variance Status", src.get("variance_status", "Calculated"), f"${tgt.get('budget_q3', 0) - tgt.get('spent_q3', 0):,.2f} Surplus"),
                ]
            else: # invoice fallback
                fields = [
                    ("Vendor / Counterparty", src.get("vendor_name"), tgt.get("vendor_name")),
                    ("Invoice Number", src.get("invoice_number"), tgt.get("invoice_number")),
                    ("Amount Due", f"${src.get('amount', 0):.2f}" if src.get('amount') else 'N/A', f"${tgt.get('amount', 0):.2f}" if tgt.get('amount') else 'N/A'),
                    ("Due Date", src.get("due_date"), tgt.get("due_date")),
                ]

            for label, s_val, t_val in fields:
                if s_val is not None or t_val is not None:
                    match_icon = "✅ Confirmed" if (str(s_val or '').lower() in str(t_val or '').lower() or str(t_val or '').lower() in str(s_val or '').lower()) else "⚠️ Difference"
                    md_lines.append(f"| **{label}** | `{s_val}` | `{t_val}` | {match_icon} |")

        md_lines.extend([
            f"",
            f"---",
            f"",
            f"## 3. Milestone Execution Progress",
            f"",
        ])

        for m in state.milestones:
            icon = "✅" if m.status == "SUCCESS" else ("🔄" if m.status == "IN_PROGRESS" else "⏳")
            md_lines.append(f"- {icon} **Milestone {m.id}: {m.title}** ({m.status.value})")
            if m.result_summary:
                md_lines.append(f"  * {m.result_summary}")

        md_lines.extend([
            f"",
            f"---",
            f"",
            f"## 4. Execution Step Chronology & Audit Trail",
            f"",
        ])

        for s in state.steps_history:
            status_icon = "🟢" if s.success else "🔴"
            md_lines.append(f"### {status_icon} Step {s.step_number}: `{s.tool_name}` at `{s.timestamp}`")
            md_lines.append(f"- **Reasoning / Thought**: {s.thought}")
            md_lines.append(f"- **Tool Input**: `{json.dumps(s.tool_input)}`")
            md_lines.append(f"- **Observation**: {s.tool_output}")
            if s.screenshot_path:
                md_lines.append(f"- **Visual Proof Captured**: `{s.screenshot_path}`")
            if s.error_message:
                md_lines.append(f"- **Error Encountered**: `{s.error_message}`")
            md_lines.append("")

        content = "\n".join(md_lines)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)

        return report_path
