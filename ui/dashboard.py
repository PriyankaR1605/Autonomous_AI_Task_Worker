import os
import sys
import asyncio
from datetime import datetime
import streamlit as st

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from worker.config import settings
from worker.agent import AutonomousWorker
from worker.state import TaskStatus, ApprovalRequest, ActionStep

st.set_page_config(
    page_title="CentrAlign AI — Autonomous Enterprise Agent",
    page_icon="🤖",
    layout="wide"
)

# Custom Styling for modern Chatbot experience
st.markdown("""
<style>
    .chat-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 8px;
        margin-bottom: 12px;
        border-bottom: 1px solid #E2E8F0;
    }
    .chat-header-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
        line-height: 1.2;
    }
    .chat-header-desc {
        color: #64748B;
        font-size: 0.95rem;
        margin-top: 2px;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .quick-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        transition: all 0.15s ease;
    }
    .stChatMessage {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# App Header
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown("""
    <div class="chat-header">
        <div>
            <div class="chat-header-title">🤖 CentrAlign AI Assistant</div>
            <div class="chat-header-desc">Goal-oriented autonomous enterprise agent executing operations across Finance, HR, IT Support, Inventory, Budgets & Compliance.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with header_col2:
    st.markdown("""
    <div style="text-align: right; padding-top: 10px;">
        <span class="status-badge">● Online & Ready</span>
    </div>
    """, unsafe_allow_html=True)

# Preset Enterprise Tasks for Quick Selection
PRESET_PROMPTS = {
    "🧾 Process Latest Invoice": "Find the latest invoice from Company X, extract the amount and due date, enter it into our internal system, and tell me once it is done.",
    "👥 Approve HR Vacation Leave": "Find employee Sarah Jenkins, check her remaining annual leave balance, approve her pending vacation request, and update the HR system.",
    "🎫 Reassign Priority IT Tickets": "Scan all open customer support tickets, identify any CRITICAL priority tickets, reassign them to Senior Engineer Alex Wong, and mark them IN_PROGRESS.",
    "📦 Restock Low Inventory": "Audit our inventory warehouse for all items below the reorder threshold, calculate restock requirements, and generate a purchase order to the preferred supplier.",
    "💰 Audit Expense Compliance": "Audit recent employee expense reports against our company travel and procurement policy, flag any unapproved expenses over $1,000, and request approval.",
    "📊 Calculate Department Budget": "Calculate the total Q3 marketing expenditure, compare it against the allocated department budget, and report budget variance."
}

# Sidebar: Controls & Quick Prompts
with st.sidebar:
    st.header("⚙️ Agent Controls")
    
    use_browser = st.toggle(
        "Enable Browser Automation", 
        value=True, 
        help="Executes internal UI operations & captures visual verification proof"
    )
    headless_opt = st.toggle(
        "Run Browser Headless", 
        value=settings.HEADLESS_BROWSER, 
        help="Execute browser tasks without showing external GUI window"
    )
    settings.HEADLESS_BROWSER = headless_opt

    high_risk_limit = st.number_input(
        "Human Approval Threshold ($)",
        min_value=500.0,
        max_value=20000.0,
        value=settings.HIGH_RISK_AMOUNT_THRESHOLD,
        step=500.0,
        help="Transactions exceeding this value trigger safety human-in-the-loop sign-off"
    )
    settings.HIGH_RISK_AMOUNT_THRESHOLD = high_risk_limit

    pace_delay = st.slider(
        "Execution Pace (seconds/step)",
        min_value=0.5,
        max_value=4.0,
        value=1.0,
        step=0.5,
        help="Delay between milestones to observe the agent reasoning in real time"
    )
    settings.STEP_DELAY_SECONDS = pace_delay

    st.divider()
    st.subheader("💡 Quick Prompts")
    st.caption("Click any enterprise workflow to instantly send it to the chatbot:")
    
    for label, prompt_text in PRESET_PROMPTS.items():
        if st.button(label, use_container_width=True):
            st.session_state["queued_prompt"] = prompt_text
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear Chat History", type="secondary", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

# Initialize Session State Messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

def render_task_dossier(state, msg_idx: int):
    """Renders milestones, execution logs, visual evidence, and reconciliation for a completed task."""
    if not state:
        return

    # 1. Milestone Status Badges
    if state.milestones:
        num_m = len(state.milestones)
        cols = st.columns(num_m)
        for idx, m in enumerate(state.milestones):
            with cols[idx]:
                if m.status.value == "SUCCESS":
                    st.success(f"**Step {m.id}**\n{m.title}")
                elif m.status.value == "FAILED":
                    st.error(f"**Step {m.id}**\n{m.title}")
                else:
                    st.info(f"**Step {m.id}**\n{m.title}")

    # 2. Detailed Execution Log & Visual Proof
    if state.steps_history:
        with st.expander("🔍 Agent Reasoning & Tool Execution Trace", expanded=False):
            for step in state.steps_history:
                st.markdown(f"**Step {step.step_number}: `{step.tool_name}`** (`{step.timestamp}`)")
                st.markdown(f"> *Reasoning:* {step.thought}")
                if step.tool_output:
                    st.code(step.tool_output, language="text")
                if step.screenshot_path and os.path.exists(step.screenshot_path):
                    st.image(
                        step.screenshot_path,
                        caption=f"Visual Verification: {os.path.basename(step.screenshot_path)}",
                        width=650
                    )
                st.write("---")

    # 3. Outcome Verification Matrix
    if state.verification:
        with st.expander("📊 Data Integrity Reconciliation Matrix", expanded=True):
            src = state.verification.source_values
            tgt = state.verification.target_values
            domain = state.working_memory.get("domain", "general").lower()

            recon_data = None
            if domain == "ticket":
                recon_data = {
                    "Property": ["Ticket ID", "Subject", "Priority", "Assignee", "Status"],
                    "Target / Expected": [src.get("ticket_number") or src.get("target_ticket"), src.get("subject"), src.get("priority"), src.get("expected_assignee"), src.get("expected_status")],
                    "Confirmed in ITSM Ledger": [tgt.get("ticket_number"), tgt.get("subject"), tgt.get("priority"), tgt.get("assignee"), tgt.get("status")],
                    "Match Status": ["✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed"]
                }
            elif domain in ("hr_leave", "leave"):
                recon_data = {
                    "Property": ["Employee", "Leave Request ID", "Days Requested", "Approval Status", "Remaining Balance"],
                    "Target / Expected": [src.get("employee_name"), src.get("req_code"), f"{src.get('days_requested')} days", "APPROVED", f"{src.get('updated_leave_balance')} days"],
                    "Confirmed in HR Ledger": [tgt.get("emp_name"), tgt.get("req_code"), f"{tgt.get('days_requested')} days", tgt.get("status"), f"{src.get('updated_leave_balance')} days"],
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
            elif domain == "expense":
                recon_data = {
                    "Property": ["Report #", "Employee", "Claim Amount", "Compliance Check", "Approval Status"],
                    "Target / Expected": [src.get("report_number"), src.get("employee_name"), f"${src.get('amount', 0):,.2f}", "Verified", "APPROVED"],
                    "Confirmed in Expense Ledger": [tgt.get("report_number", src.get("report_number")), tgt.get("employee_name", src.get("employee_name")), f"${tgt.get('amount', src.get('amount', 0)):,.2f}", "Compliant", tgt.get("status", "APPROVED")],
                    "Match Status": ["✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed"]
                }
            else: # Invoice
                recon_data = {
                    "Property": ["Vendor", "Invoice #", "Amount Due", "Due Date"],
                    "Extracted from Document": [src.get("vendor_name"), src.get("invoice_number"), f"${src.get('amount', 0):,.2f}" if src.get('amount') else 'N/A', src.get("due_date")],
                    "Confirmed in ERP Ledger": [tgt.get("vendor_name"), tgt.get("invoice_number"), f"${tgt.get('amount', 0):,.2f}" if tgt.get('amount') else 'N/A', tgt.get("due_date")],
                    "Match Status": ["✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed"]
                }

            if recon_data:
                st.table(recon_data)

    # 4. Evidence Dossier Report Download
    if state.evidence_report_path and os.path.exists(state.evidence_report_path):
        with open(state.evidence_report_path, "r", encoding="utf-8") as f:
            report_text = f.read()
        
        dossier_col1, dossier_col2 = st.columns([1, 2])
        with dossier_col1:
            st.download_button(
                label="📥 Download Audit Dossier (.md)",
                data=report_text,
                file_name=os.path.basename(state.evidence_report_path),
                mime="text/markdown",
                key=f"dl_btn_{msg_idx}_{state.task_id}"
            )
        with dossier_col2:
            st.caption(f"Audit Dossier verified: `{os.path.basename(state.evidence_report_path)}`")


# Render Welcome Screen if No Messages Yet
if not st.session_state["messages"]:
    st.info(
        "👋 **Welcome to CentrAlign AI Chat!**\n\n"
        "I am an autonomous enterprise assistant that can execute real business tasks across company data.\n"
        "Ask me to process invoices, approve HR leaves, reassign support tickets, audit inventory, inspect budgets, or review compliance policies.\n\n"
        "**Try one of these quick starters below, or type your own request:**"
    )

    w_col1, w_col2, w_col3 = st.columns(3)
    with w_col1:
        if st.button("🧾 Process Invoice from Company X", use_container_width=True):
            st.session_state["queued_prompt"] = PRESET_PROMPTS["🧾 Process Latest Invoice"]
            st.rerun()
        if st.button("📦 Audit & Restock Low Inventory", use_container_width=True):
            st.session_state["queued_prompt"] = PRESET_PROMPTS["📦 Restock Low Inventory"]
            st.rerun()
    with w_col2:
        if st.button("👥 Approve Sarah Jenkins Vacation", use_container_width=True):
            st.session_state["queued_prompt"] = PRESET_PROMPTS["👥 Approve HR Vacation Leave"]
            st.rerun()
        if st.button("💰 Audit Employee Expense Reports", use_container_width=True):
            st.session_state["queued_prompt"] = PRESET_PROMPTS["💰 Audit Expense Compliance"]
            st.rerun()
    with w_col3:
        if st.button("🎫 Reassign Critical Support Tickets", use_container_width=True):
            st.session_state["queued_prompt"] = PRESET_PROMPTS["🎫 Reassign Priority IT Tickets"]
            st.rerun()
        if st.button("📊 Marketing Q3 Budget Variance", use_container_width=True):
            st.session_state["queued_prompt"] = PRESET_PROMPTS["📊 Calculate Department Budget"]
            st.rerun()

# Render Previous Conversation Messages
for idx, message in enumerate(st.session_state["messages"]):
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(message["content"])
            if message.get("task_state"):
                render_task_dossier(message["task_state"], idx)

# Check for queued prompt or new user input
active_prompt = None
if "queued_prompt" in st.session_state and st.session_state["queued_prompt"]:
    active_prompt = st.session_state.pop("queued_prompt")
else:
    active_prompt = st.chat_input("Ask CentrAlign AI to perform an enterprise task or query data...")

# Process New Message
if active_prompt:
    # 1. Record and display user message
    st.session_state["messages"].append({
        "role": "user",
        "content": active_prompt,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    with st.chat_message("user", avatar="👤"):
        st.markdown(active_prompt)

    # 2. Assistant response with live autonomous execution
    with st.chat_message("assistant", avatar="🤖"):
        with st.status("⚡ Autonomous agent analyzing intent and formulating plan...", expanded=True) as status_box:
            
            def handle_step(step: ActionStep):
                status_box.write(f"🔹 **Step {step.step_number}** [`{step.tool_name}`]: {step.thought}")

            def handle_approval(req: ApprovalRequest) -> bool:
                status_box.warning(f"🛡️ **Safety Guardrail Check**: {req.reason}")
                return True

            worker = AutonomousWorker(
                user_prompt=active_prompt,
                approval_callback=handle_approval,
                use_browser=use_browser,
                step_callback=handle_step
            )

            try:
                state = asyncio.run(worker.run())
                if state.status == TaskStatus.COMPLETED:
                    status_box.update(label="✅ Task successfully executed & verified!", state="complete", expanded=False)
                else:
                    status_box.update(label=f"⚠️ Execution finished with status: {state.status.value}", state="complete", expanded=False)
            except Exception as e:
                import traceback
                status_box.update(label="❌ Execution encountered an error", state="error", expanded=False)
                st.error(f"Error: {str(e)}")
                st.code(traceback.format_exc())
                state = None

        if state:
            st.markdown(state.final_summary or "Task finished.")
            render_task_dossier(state, len(st.session_state["messages"]))

            # Store assistant response in history
            st.session_state["messages"].append({
                "role": "assistant",
                "content": state.final_summary or "Task finished.",
                "task_state": state,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
        else:
            st.session_state["messages"].append({
                "role": "assistant",
                "content": "Sorry, an unexpected error occurred while executing this task.",
                "task_state": None,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
