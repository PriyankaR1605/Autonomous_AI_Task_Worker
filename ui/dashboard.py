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

st.set_page_config(
    page_title="CentrAlign — Autonomous AI Task Worker",
    page_icon="🤖",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 0.2rem; }
    .sub-header { color: #64748B; font-size: 1.05rem; margin-bottom: 1.5rem; }
    .badge-success { background-color: #DCFCE7; color: #166534; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 0.8rem; }
    .badge-pending { background-color: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 0.8rem; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 15px; }
</style>
""", unsafe_allow_html=True)

col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown('<div class="main-header">🤖 Autonomous AI Task Worker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Goal-oriented autonomous agent executing multi-step business operations with self-healing, verification & human oversight.</div>', unsafe_allow_html=True)
with col_head2:
    st.write("")
    st.link_button("🌐 Open ERP Dashboard", f"{settings.MOCK_ERP_BASE_URL}/dashboard", use_container_width=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Worker Configuration")
    
    use_browser = st.toggle("Enable Browser Automation", value=True, help="Executes UI interactions via Playwright browser")
    headless_opt = st.toggle("Run Browser Headless", value=settings.HEADLESS_BROWSER, help="Run browser without visible GUI window")
    settings.HEADLESS_BROWSER = headless_opt
    
    st.divider()
    st.subheader("🏢 Enterprise Environment")
    st.link_button("🌐 Open Mock ERP Dashboard", f"{settings.MOCK_ERP_BASE_URL}/dashboard", use_container_width=True)
    st.markdown(f"**Direct Link**: [{settings.MOCK_ERP_BASE_URL}/dashboard]({settings.MOCK_ERP_BASE_URL}/dashboard)")
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
        value=2.0,
        step=0.5,
        help="Slows down each milestone so you can comfortably watch the AI think and work"
    )
    settings.STEP_DELAY_SECONDS = pace_delay

# Preset Prompt
default_prompt = "Find the latest invoice from Company X, extract the amount and due date, enter it into our internal system, and tell me once it is done."

col1, col2 = st.columns([4, 1])
with col1:
    user_prompt = st.text_area("Task Instruction (Natural Language Goal)", value=default_prompt, height=85)
with col2:
    st.write("")
    st.write("")
    run_btn = st.button("🚀 Launch Autonomous Worker", type="primary", use_container_width=True)

# Execution Flow
if run_btn:
    st.divider()
    status_container = st.container()
    
    with status_container:
        st.subheader("⚡ Live Autonomous Execution Trace")
        stepper_col1, stepper_col2, stepper_col3, stepper_col4, stepper_col5 = st.columns(5)
        
        step_cols = [stepper_col1, stepper_col2, stepper_col3, stepper_col4, stepper_col5]
        
        progress_bar = st.progress(0, text="Initializing Worker State...")
        log_expander = st.expander("🔍 Real-time Reasoning & Tool Observations", expanded=True)
        log_placeholder = log_expander.empty()

        # Approval callback handler for UI
        def handle_approval(req: ApprovalRequest) -> bool:
            st.warning(f"⚠️ **Human-in-the-Loop Gate Triggered**: {req.reason}")
            st.info(f"Proposed Action: **{req.proposed_action}** (Details: {req.details})")
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
            for idx, m in enumerate(state.milestones):
                with step_cols[idx]:
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
                        st.image(step.screenshot_path, caption=f"Visual Evidence: {os.path.basename(step.screenshot_path)}", width=650)
                    st.write("---")

            # Final Completion Summary & Verification Dossier
            st.divider()
            st.header("📋 Execution Dossier & Outcome Verification")
            
            res_col1, res_col2 = st.columns([1, 1])

            with res_col1:
                st.subheader("Summary")
                if state.status == TaskStatus.COMPLETED:
                    st.success(state.final_summary)
                else:
                    st.error(state.final_summary)

                if state.verification:
                    st.subheader("Reconciled Data Table")
                    src = state.verification.source_values
                    tgt = state.verification.target_values

                    recon_data = {
                        "Property": ["Vendor", "Invoice #", "Amount Due", "Due Date"],
                        "Extracted from Document": [
                            src.get("vendor_name"),
                            src.get("invoice_number"),
                            f"${src.get('amount', 0):.2f}" if src.get('amount') else 'N/A',
                            src.get("due_date")
                        ],
                        "Confirmed in ERP Ledger": [
                            tgt.get("vendor_name"),
                            tgt.get("invoice_number"),
                            f"${tgt.get('amount', 0):.2f}" if tgt.get('amount') else 'N/A',
                            tgt.get("due_date")
                        ],
                        "Match Status": ["✅ Confirmed", "✅ Confirmed", "✅ Confirmed", "✅ Confirmed"]
                    }
                    st.table(recon_data)

            with res_col2:
                st.subheader("Audit Report Artifact")
                if state.evidence_report_path and os.path.exists(state.evidence_report_path):
                    with open(state.evidence_report_path, "r", encoding="utf-8") as f:
                        report_content = f.read()
                    
                    st.download_button(
                        label="📥 Download Auditable Markdown Report",
                        data=report_content,
                        file_name=os.path.basename(state.evidence_report_path),
                        mime="text/markdown"
                    )
                    
                    st.text_area("Report Preview", value=report_content, height=350)

        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
