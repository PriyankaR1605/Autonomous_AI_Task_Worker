import os
import json
from datetime import datetime
from typing import Dict, Any
from worker.config import settings
from worker.state import AgentState

class EvidencePackager:
    """
    Compiles structured execution traces, screenshots, and verification results into auditable reports.
    """

    @staticmethod
    def generate_report(state: AgentState) -> str:
        report_id = f"audit_report_{state.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join(settings.STORAGE_DIR, report_id)

        v_status = "✅ VERIFIED & CONFIRMED" if (state.verification and state.verification.verified) else "❌ UNVERIFIED"
        
        md_lines = [
            f"# Autonomous Task Worker — Execution & Verification Dossier",
            f"",
            f"**Task ID**: `{state.task_id}`  ",
            f"**Execution Timestamp**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`  ",
            f"**Overall Status**: **{state.status.value}** ({v_status})  ",
            f"**User Prompt**: *\"{state.user_prompt}\"*",
            f"",
            f"---",
            f"",
            f"## 1. Executive Summary",
            f"",
            f"{state.final_summary or 'Task execution completed autonomously.'}",
            f"",
            f"---",
            f"",
            f"## 2. Independent Outcome Verification",
            f"",
            f"- **Result**: **{v_status}**",
            f"- **Verification Message**: {state.verification.verification_message if state.verification else 'N/A'}",
            f"",
            f"### Data Integrity Reconciliation",
            f"| Field | Extracted from Source Invoice | Confirmed in Enterprise ERP | Match Status |",
            f"| :--- | :--- | :--- | :--- |",
        ]

        if state.verification:
            src = state.verification.source_values
            tgt = state.verification.target_values

            fields = [
                ("Vendor", src.get("vendor_name"), tgt.get("vendor_name")),
                ("Invoice Number", src.get("invoice_number"), tgt.get("invoice_number")),
                ("Amount Due", f"${src.get('amount', 0):.2f}" if src.get('amount') else 'N/A', f"${tgt.get('amount', 0):.2f}" if tgt.get('amount') else 'N/A'),
                ("Due Date", src.get("due_date"), tgt.get("due_date")),
            ]

            for label, s_val, t_val in fields:
                match_icon = "✅ Match" if (str(s_val).strip() == str(t_val).strip() or (label == "Amount Due" and s_val == t_val)) else "⚠️ Diff"
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
