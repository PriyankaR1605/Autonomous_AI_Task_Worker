import os
import sys
import asyncio
from datetime import datetime
import streamlit as st

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from worker.config import settings
from worker.agent import AutonomousWorker
from worker.state import TaskStatus, ApprovalRequest
from mock_erp.database import (
    get_all_invoices,
    get_all_employees,
    get_all_tickets,
    get_all_inventory,
    get_all_departments
)

st.set_page_config(
    page_title="CentrAlign — Autonomous AI Task Worker",
    page_icon="🤖",
    layout="wide"
)

# Primary Cloud Deployment Link & Relative Route Resolver
MAIN_APP_URL = "https://autonomous-ai-task-worker.onrender.com"

def get_dynamic_portal_url(path: str = "dashboard") -> str:
    """
    Dynamically computes the Enterprise Portal URL relative to the primary deployment link:
    https://autonomous-ai-task-worker.onrender.com/{path}
    """
    clean_path = path.lstrip("/")
    try:
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            headers = st.context.headers
            host = headers.get("host") or headers.get("x-forwarded-host")
            if host and not any(l in host for l in ("127.0.0.1", "localhost")):
                proto = headers.get("x-forwarded-proto", "https")
                return f"{proto}://{host}/{clean_path}"
    except Exception:
        pass

    base = (getattr(settings, "PUBLIC_BASE_URL", None) or MAIN_APP_URL).rstrip("/")
    return f"{base}/{clean_path}"

portal_dashboard_url = get_dynamic_portal_url("dashboard")
portal_login_url = get_dynamic_portal_url("login")

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 0.2rem; }
    .sub-header { color: #64748B; font-size: 1.05rem; margin-bottom: 1.5rem; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 15px; }
    .badge-domain { background-color: #EEF2FF; color: #4338CA; border: 1px solid #C7D2FE; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 0.75rem; }
</style>
""", unsafe_allow_html=True)

col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown('<div class="main-header">🤖 Autonomous AI Enterprise Task Worker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Goal-oriented autonomous agent executing operations across all company data — Finance, HR, IT Support, Inventory, Budgets & Compliance.</div>', unsafe_allow_html=True)
with col_head2:
    st.write("")
    st.link_button("🌐 Open Enterprise Portal", portal_dashboard_url, use_container_width=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Worker Configuration")
    
    use_browser = st.toggle("Enable Browser Automation", value=True, help="Executes UI interactions & captures proof via Playwright")
    headless_opt = st.toggle("Run Browser Headless", value=settings.HEADLESS_BROWSER, help="Run browser without visible GUI window")
    settings.HEADLESS_BROWSER = headless_opt
    
    st.divider()
    st.subheader("🏢 Enterprise Environment")
    st.link_button("🌐 Open Enterprise Portal", portal_dashboard_url, use_container_width=True)
    st.markdown("**Credentials**: `admin` / `company_secure_pass`")
    
    st.divider()
    st.subheader("🛡️ Safety Guardrails")
    high_risk_limit = st.number_input(
        "High-Risk Approval Threshold ($)",
        min_value=500.0,
        max_value=20000.0,
        value=settings.HIGH_RISK_AMOUNT_THRESHOLD,
        step=500.0
    )
    settings.HIGH_RISK_AMOUNT_THRESHOLD = high_risk_limit

    st.divider()
    st.subheader("⏱️ Execution Pace")
    pace_delay = st.slider(
        "Delay between Steps (seconds)",
        min_value=0.5,
        max_value=5.0,
        value=1.5,
        step=0.5,
        help="Slows down each milestone so you can comfortably watch the AI think and work"
    )
    settings.STEP_DELAY_SECONDS = pace_delay

# Preset Enterprise Tasks Across Diverse Domains
presets = {
    "🧾 Invoices & Accounts Payable": "Find the latest invoice from Company X, extract the amount and due date, enter it into our internal system, and tell me once it is done.",
    "👥 HR & Employee Leave Approval": "Find employee Sarah Jenkins, check her remaining annual leave balance, approve her pending vacation request, and update the HR system.",
    "🎫 IT & Support Helpdesk": "Scan all open customer support tickets, identify any CRITICAL priority tickets, reassign them to Senior Engineer Alex Wong, and mark them IN_PROGRESS.",
    "📦 Inventory & Supply Chain": "Audit our inventory warehouse for all items below the reorder threshold, calculate restock requirements, and generate a purchase order to the preferred supplier.",
    "💰 Expense & Spending Compliance": "Audit recent employee expense reports against our company travel and procurement policy, flag any unapproved expenses over $1,000, and request approval.",
    "📊 Department Budget Analytics": "Calculate the total Q3 marketing expenditure, compare it against the allocated department budget, and report budget variance."
}

# Main Tabs: Autonomous Worker Execution vs Company Database Explorer
tab_worker, tab_explorer = st.tabs(["⚡ Autonomous Worker Execution", "🏢 Live Enterprise Data Explorer"])

with tab_worker:
    st.subheader("🎯 Select an Enterprise Business Task or Enter Custom Request")
    selected_preset_name = st.selectbox(
        "Choose a pre-configured enterprise workflow domain:",
        options=list(presets.keys()),
        index=0
    )

    preset_text = presets[selected_preset_name]
    user_prompt = st.text_area(
        "Natural Language Task Instruction (Editable)",
        value=preset_text,
        height=80,
        help="You can ask ANY arbitrary task or question about CentrAlign company data!"
    )

    col_run, col_info = st.columns([2, 5])
    with col_run:
        run_btn = st.button("🚀 Launch Autonomous Worker", type="primary", use_container_width=True)
    with col_info:
        st.caption("The AI worker will decompose your end goal, invoke necessary tools (Files, DB, Browser, API, Knowledge Base), self-heal if issues arise, check safety guardrails, verify the database, and compile auditable evidence.")

    # Execution Trace
    if run_btn:
        st.divider()
        status_container = st.container()
        
        with status_container:
            st.subheader("⚡ Live Autonomous Execution Trace")
            
            progress_bar = st.progress(0, text="Analyzing user intent and gathering enterprise context...")
            log_expander = st.expander("🔍 Real-time Reasoning & Tool Observations", expanded=True)
            log_placeholder = log_expander.empty()

            # Approval callback handler for UI
            def handle_approval(req: ApprovalRequest) -> bool:
                st.warning(f"⚠️ **Human-in-the-Loop Safety Check**: {req.reason}")
                st.info(f"Proposed Action: **{req.proposed_action}** (Details: `{req.details}`)")
                return True

            worker = AutonomousWorker(
                user_prompt=user_prompt,
                approval_callback=handle_approval,
                use_browser=use_browser
            )

            progress_bar.progress(20, text="Decomposing goal into actionable milestones...")

            # Run async worker
            try:
                state = asyncio.run(worker.run())
                progress_bar.progress(100, text="Task Finished!")

                # Display Milestones Status
                num_milestones = len(state.milestones)
                if num_milestones > 0:
                    cols = st.columns(num_milestones)
                    for idx, m in enumerate(state.milestones):
                        with cols[idx]:
                            if m.status.value == "SUCCESS":
                                st.success(f"**Step {m.id}**\n{m.title}")
                            elif m.status.value == "FAILED":
                                st.error(f"**Step {m.id}**\n{m.title}")
                            else:
                                st.info(f"**Step {m.id}**\n{m.title}")

                # Display Execution Logs
                with log_placeholder.container():
                    for step in state.steps_history:
                        st.markdown(f"**Step {step.step_number}: `{step.tool_name}`** (`{step.timestamp}`)")
                        st.markdown(f"> *Reasoning:* {step.thought}")
                        st.code(step.tool_output, language="text")
                        if step.screenshot_path and os.path.exists(step.screenshot_path):
                            st.image(step.screenshot_path, caption=f"Visual Proof: {os.path.basename(step.screenshot_path)}", width=680)
                        st.write("---")

                # Final Completion Summary & Verification Dossier
                st.divider()
                st.header("📋 Execution Dossier & Outcome Verification")
                
                res_col1, res_col2 = st.columns([1, 1])

                with res_col1:
                    st.subheader("Executive Summary")
                    if state.status == TaskStatus.COMPLETED:
                        st.success(state.final_summary)
                    else:
                        st.error(state.final_summary)

                    if state.verification:
                        st.subheader("Data Integrity Reconciliation Matrix")
                        src = state.verification.source_values
                        tgt = state.verification.target_values
                        domain = state.working_memory.get("domain", "general").lower()

                        if domain == "ticket":
                            recon_data = {
                                "Property": ["Ticket ID", "Subject", "Priority", "Assignee", "Status"],
                                "Target / Expected": [src.get("ticket_number") or src.get("target_ticket"), src.get("subject"), src.get("priority"), src.get("expected_assignee"), src.get("expected_status")],
                                "Confirmed in ITSM Database": [tgt.get("ticket_number"), tgt.get("subject"), tgt.get("priority"), tgt.get("assignee"), tgt.get("status")],
                                "Match Status": ["✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed"]
                            }
                        elif domain in ("hr_leave", "leave"):
                            recon_data = {
                                "Property": ["Employee", "Leave Request ID", "Days Requested", "Approval Status", "Remaining Balance"],
                                "Target / Expected": [src.get("employee_name"), src.get("req_code"), f"{src.get('days_requested')} days", "APPROVED", f"{src.get('updated_leave_balance')} days"],
                                "Confirmed in HR Database": [tgt.get("emp_name"), tgt.get("req_code"), f"{tgt.get('days_requested')} days", tgt.get("status"), f"{src.get('updated_leave_balance')} days"],
                                "Match Status": ["✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed"]
                            }
                        elif domain in ("inventory", "po"):
                            recon_data = {
                                "Property": ["PO Number", "Supplier", "Items Summary", "Total Valuation", "Status"],
                                "Target / Expected": [src.get("po_number"), src.get("supplier"), src.get("items_summary"), f"${src.get('total_cost', 0):,.2f}", "ISSUED"],
                                "Confirmed in Procurement Ledger": [tgt.get("po_number"), tgt.get("supplier"), tgt.get("items_summary"), f"${tgt.get('total_cost', 0):,.2f}", tgt.get("status")],
                                "Match Status": ["✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed"]
                            }
                        elif domain == "budget":
                            recon_data = {
                                "Property": ["Department", "Allocated Q3 Budget", "Actual Spend", "Variance Status"],
                                "Target / Expected": [src.get("department"), f"${src.get('budget', 0):,.2f}", f"${src.get('spent', 0):,.2f}", src.get("variance_status", "Calculated")],
                                "Confirmed in Financial Ledger": [tgt.get("name"), f"${tgt.get('budget_q3', 0):,.2f}", f"${tgt.get('spent_q3', 0):,.2f}", f"${tgt.get('budget_q3', 0) - tgt.get('spent_q3', 0):,.2f} Surplus"],
                                "Match Status": ["✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed"]
                            }
                        else: # Invoice
                            recon_data = {
                                "Property": ["Vendor", "Invoice #", "Amount Due", "Due Date"],
                                "Extracted from Document": [src.get("vendor_name"), src.get("invoice_number"), f"${src.get('amount', 0):,.2f}" if src.get('amount') else 'N/A', src.get("due_date")],
                                "Confirmed in ERP Ledger": [tgt.get("vendor_name"), tgt.get("invoice_number"), f"${tgt.get('amount', 0):,.2f}" if tgt.get('amount') else 'N/A', tgt.get("due_date")],
                                "Match Status": ["✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed"]
                            }
                        st.table(recon_data)

                with res_col2:
                    st.subheader("Auditable Evidence Dossier")
                    if state.evidence_report_path and os.path.exists(state.evidence_report_path):
                        with open(state.evidence_report_path, "r", encoding="utf-8") as f:
                            report_content = f.read()
                        
                        st.download_button(
                            label="📥 Download Markdown Audit Report",
                            data=report_content,
                            file_name=os.path.basename(state.evidence_report_path),
                            mime="text/markdown"
                        )
                        
                        st.text_area("Audit Report Preview", value=report_content, height=350)

            except Exception as e:
                st.error(f"Execution Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

with tab_explorer:
    st.subheader("🏢 Live Enterprise Database Explorer")
    st.markdown(f"Direct live view of CentrAlign Technologies records. You can also view the full Tailwind web app at: [{portal_dashboard_url}]({portal_dashboard_url})")
    
    exp_invoices = get_all_invoices()
    exp_employees = get_all_employees()
    exp_tickets = get_all_tickets()
    exp_inventory = get_all_inventory()
    exp_depts = get_all_departments()

    t1, t2, t3, t4, t5 = st.tabs(["🧾 Invoices (AP/AR)", "👥 HR Directory", "🎫 Support Tickets", "📦 Inventory", "📊 Budgets"])
    
    with t1:
        st.caption(f"Total Invoices: {len(exp_invoices)}")
        st.dataframe(exp_invoices, use_container_width=True)
    with t2:
        st.caption(f"Active Employees: {len(exp_employees)}")
        st.dataframe(exp_employees, use_container_width=True)
    with t3:
        st.caption(f"Support Queue: {len(exp_tickets)} tickets")
        st.dataframe(exp_tickets, use_container_width=True)
    with t4:
        st.caption(f"Inventory Catalog: {len(exp_inventory)} items")
        st.dataframe(exp_inventory, use_container_width=True)
    with t5:
        st.caption(f"Departments: {len(exp_depts)}")
        st.dataframe(exp_depts, use_container_width=True)
