import streamlit as st
import json
from agent import HealingAgent
import pandas as pd
from collections import Counter

st.set_page_config(
    page_title="Self-Healing Support Agent", 
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Self-Healing Support Agent Dashboard")
st.markdown("**Agentic AI System for E-commerce Headless Migration Support**")
st.markdown("---")

# Initialize agent in session state
if 'agent' not in st.session_state:
    st.session_state.agent = HealingAgent()
    st.session_state.results = None
    st.session_state.processing = False

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Agent Controls")
    
    st.markdown("""
    This agent demonstrates a complete **OBSERVE → REASON → DECIDE → ACT** loop for handling support tickets during platform migration.
    """)
    
    st.markdown("---")
    
    if st.button("🚀 Run Agent Analysis", type="primary", use_container_width=True):
        st.session_state.processing = True
        with st.spinner("🤖 Agent is analyzing tickets..."):
            try:
                st.session_state.results = st.session_state.agent.process_all_tickets()
                st.session_state.processing = False
                st.success("✅ Analysis Complete!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.processing = False
    
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.results = None
        st.session_state.agent = HealingAgent()
        st.rerun()
    
    st.markdown("---")
    
    # Stats sidebar
    if st.session_state.results:
        st.markdown("### 📊 Quick Stats")
        results = st.session_state.results
        
        st.metric("Tickets Processed", len(results))
        
        auto_resolved = sum(1 for r in results if r['action_result']['status'] == 'executed')
        st.metric("Auto-Resolved", auto_resolved, delta=f"{auto_resolved/len(results)*100:.0f}%")
        
        needs_approval = sum(1 for r in results if r['action_result']['status'] == 'pending_approval')
        st.metric("Needs Approval", needs_approval)
        
        avg_confidence = sum(r['analysis'].get('confidence', 0) for r in results) / len(results)
        st.metric("Avg Confidence", f"{avg_confidence:.0f}%")
    
    st.markdown("---")
    st.markdown("### 🎯 Agent Capabilities")
    st.markdown("""
    - ✅ Pattern Detection
    - ✅ Root Cause Analysis
    - ✅ Risk Assessment
    - ✅ Auto-Execution
    - ✅ Human Oversight
    - ✅ Full Explainability
    """)

# Main content area
if st.session_state.results is None:
    # Show sample data before processing
    st.info("👈 Click **'Run Agent Analysis'** in the sidebar to start the self-healing process")
    
    st.subheader("📋 Sample Support Tickets Loaded")
    st.markdown("These are simulated tickets from merchants experiencing issues during headless migration:")
    
    try:
        agent = st.session_state.agent
        tickets = agent.load_tickets()
        
        if tickets:
            # Create DataFrame for display
            df_display = pd.DataFrame([{
                'Ticket ID': t['ticket_id'],
                'Merchant': t['merchant_id'],
                'Issue': t['issue'][:50] + '...' if len(t['issue']) > 50 else t['issue'],
                'Severity': t['severity'],
                'Migration Stage': t['migration_stage'],
                'Checkout Failures': t.get('checkout_failures', 0)
            } for t in tickets])
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Show example ticket detail
            with st.expander("🔍 View Example Ticket Details"):
                example = tickets[0]
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Ticket Information**")
                    st.json({
                        'ticket_id': example['ticket_id'],
                        'merchant_id': example['merchant_id'],
                        'severity': example['severity'],
                        'migration_stage': example['migration_stage']
                    })
                
                with col2:
                    st.markdown("**Merchant Message**")
                    st.info(example['merchant_message'])
                    st.markdown("**Error Log**")
                    st.code(example['error_log'])
        else:
            st.warning("⚠️ No tickets found. Please run data_generator.py first!")
            
    except Exception as e:
        st.error(f"Error loading tickets: {str(e)}")
        st.info("Please run: `python data_generator.py` first")

else:
    # Display agent results
    results = st.session_state.results
    
    # Top metrics
    st.subheader("📊 Analysis Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Tickets", len(results))
    
    with col2:
        patterns_detected = sum(1 for r in results if r['analysis'].get('is_pattern', False))
        st.metric("Patterns Detected", patterns_detected)
    
    with col3:
        avg_conf = sum(r['analysis'].get('confidence', 0) for r in results) / len(results) if results else 0
        st.metric("Avg Confidence", f"{avg_conf:.0f}%")
    
    with col4:
        critical = sum(1 for r in results if r['ticket']['severity'] == 'critical')
        st.metric("Critical Issues", critical)
    
    with col5:
        auto_resolved = sum(1 for r in results if r['action_result']['status'] == 'executed')
        st.metric("Auto-Resolved", auto_resolved)
    
    st.markdown("---")
    
    # Summary charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Actions Taken")
        actions = [r['decision']['action'].replace('_', ' ').title() for r in results]
        action_counts = Counter(actions)
        st.bar_chart(action_counts)
    
    with col2:
        st.subheader("🔍 Root Causes")
        causes = [r['analysis']['root_cause'].replace('_', ' ').title() for r in results]
        cause_counts = Counter(causes)
        st.bar_chart(cause_counts)
    
    st.markdown("---")
    
    # Detailed ticket analysis
    st.subheader("🔍 Detailed Ticket Analysis")
    
    for idx, result in enumerate(results):
        ticket = result['ticket']
        analysis = result['analysis']
        decision = result['decision']
        action = result['action_result']
        
        # Expandable section for each ticket
        with st.expander(
            f"{'🔴' if ticket['severity'] == 'critical' else '🟡' if ticket['severity'] == 'high' else '🟢'} "
            f"{ticket['ticket_id']}: {ticket['issue']}", 
            expanded=(idx == 0)
        ):
            
            # Ticket details
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 🎫 Ticket Information")
                st.write(f"**Merchant:** {ticket['merchant_id']}")
                st.write(f"**Severity:** `{ticket['severity'].upper()}`")
                st.write(f"**Migration Stage:** {ticket['migration_stage']}")
                st.write(f"**Checkout Failures:** {ticket.get('checkout_failures', 0)}")
                st.write(f"**Customers Affected:** {ticket.get('affected_customers', 0)}")
                
                st.markdown("**Error Log:**")
                st.code(ticket['error_log'], language='text')
            
            with col2:
                st.markdown("#### 💬 Merchant Message")
                st.info(ticket['merchant_message'])
            
            st.markdown("---")
            
            # Agent Analysis
            st.markdown("#### 🧠 Agent Analysis (REASON Phase)")
            
            # Confidence visualization
            confidence = analysis.get('confidence', 0)
            
            col1, col2, col3 = st.columns([1, 2, 2])
            
            with col1:
                # Confidence gauge
                if confidence >= 80:
                    conf_color = "🟢"
                    conf_label = "HIGH"
                elif confidence >= 60:
                    conf_color = "🟡"
                    conf_label = "MEDIUM"
                else:
                    conf_color = "🔴"
                    conf_label = "LOW"
                
                st.markdown(f"### {conf_color} {confidence}%")
                st.caption(f"Confidence: {conf_label}")
            
            with col2:
                st.markdown("**Root Cause:**")
                st.success(f"{analysis.get('root_cause', 'unknown').replace('_', ' ').title()}")
                
                if analysis.get('is_pattern'):
                    st.warning(f"⚠️ **PATTERN DETECTED** - Affects {analysis.get('affected_merchants', 'multiple')} merchants")
            
            with col3:
                st.markdown("**Priority:**")
                priority = analysis.get('recommended_priority', 'medium')
                st.write(f"`{priority.upper()}`")
            
            # Explanation
            st.markdown("**Analysis Explanation:**")
            st.write(analysis.get('root_cause_explanation', 'No explanation provided'))
            
            # Pattern details
            if analysis.get('is_pattern') and analysis.get('pattern_details'):
                st.markdown("**Pattern Details:**")
                st.warning(analysis.get('pattern_details'))
            
            # Assumptions
            if 'assumptions' in analysis and analysis['assumptions']:
                st.markdown("**Assumptions Made:**")
                for assumption in analysis['assumptions']:
                    st.write(f"• {assumption}")
            
            st.markdown("---")
            
            # Decision
            st.markdown("#### 🎯 Recommended Action (DECIDE Phase)")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Risk level indicator
                risk_colors = {
                    'low': ('🟢', 'success'),
                    'medium': ('🟡', 'warning'),
                    'high': ('🔴', 'error')
                }
                
                risk_icon, risk_type = risk_colors.get(decision['risk_level'], ('⚪', 'info'))
                
                st.markdown(f"**Action:** {decision['action'].replace('_', ' ').title()}")
                st.markdown(f"**Risk Level:** {risk_icon} `{decision['risk_level'].upper()}`")
                st.markdown(f"**Estimated Impact:** {decision['estimated_impact']}")
            
            with col2:
                st.markdown("**Reasoning:**")
                st.info(decision['reasoning'])
            
            st.markdown("---")
            
            # Action execution
            st.markdown("#### ⚡ Action Execution (ACT Phase)")
            
            if decision['requires_approval']:
                # Check if this action was already approved in this session
                approval_key = f"approved_{ticket['ticket_id']}"
                
                if st.session_state.get(approval_key):
                    # Already approved - show execution details
                    st.success("✅ **APPROVED & EXECUTED** - Human approved this action")
                    if st.session_state.get(f"execution_details_{ticket['ticket_id']}"):
                        st.markdown("**Execution Details:**")
                        details = st.session_state.get(f"execution_details_{ticket['ticket_id']}")
                        for key, value in details.items():
                            if isinstance(value, str):
                                st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                else:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.warning("⚠️ **HIGH RISK - Requires Human Approval**")
                        st.write("This action requires manual review before execution due to potential impact.")
                    
                    with col2:
                        if st.button(f"✅ Approve & Execute", key=f"approve_{ticket['ticket_id']}", type="primary"):
                            # Actually execute the approved action
                            agent = st.session_state.agent
                            exec_result = agent.execute_approved_action(ticket['ticket_id'])
                            
                            if exec_result.get('success'):
                                st.session_state[approval_key] = True
                                st.session_state[f"execution_details_{ticket['ticket_id']}"] = exec_result.get('action_details', {})
                                # Update the result in session state
                                result['action_result']['status'] = 'executed'
                                result['action_result']['action_details'] = exec_result.get('action_details', {})
                                st.success("✅ Action Approved and Executed!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"Failed to execute: {exec_result.get('error', 'Unknown error')}")
                        
                        if st.button(f"❌ Reject", key=f"reject_{ticket['ticket_id']}"):
                            st.session_state[f"rejected_{ticket['ticket_id']}"] = True
                            st.error("Action rejected. Ticket assigned to human agent.")
            
            else:
                st.success("✅ **AUTO-EXECUTED** - Low risk, executed automatically")
            
            # Action details
            if 'action_details' in action:
                st.markdown("**Execution Details:**")
                
                details = action['action_details']
                
                # Format details nicely
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    for key, value in list(details.items())[:len(details)//2 + 1]:
                        if isinstance(value, str):
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                
                with detail_col2:
                    for key, value in list(details.items())[len(details)//2 + 1:]:
                        if isinstance(value, str):
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    st.markdown("---")
    
    # Final summary
    st.subheader("📝 Executive Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🎯 Actions Summary**")
        actions_list = [r['decision']['action'].replace('_', ' ').title() for r in results]
        for action, count in Counter(actions_list).most_common():
            st.write(f"• {action}: **{count}**")
    
    with col2:
        st.markdown("**🔍 Root Causes Found**")
        causes_list = [r['analysis']['root_cause'].replace('_', ' ').title() for r in results]
        for cause, count in Counter(causes_list).most_common():
            st.write(f"• {cause}: **{count}**")
    
    with col3:
        st.markdown("**📊 Key Insights**")
        patterns = sum(1 for r in results if r['analysis'].get('is_pattern', False))
        if patterns > 0:
            st.write(f"• **{patterns}** systemic patterns detected")
        
        high_conf = sum(1 for r in results if r['analysis'].get('confidence', 0) >= 80)
        st.write(f"• **{high_conf}** high-confidence diagnoses")
        
        total_failures = sum(r['ticket'].get('checkout_failures', 0) for r in results)
        st.write(f"• **{total_failures}** total checkout failures prevented")
    
    # Audit Log Section
    st.markdown("---")
    st.subheader("📜 Action Audit Log")
    
    audit_log = st.session_state.agent.get_audit_log()
    
    if audit_log:
        # Create DataFrame for display
        audit_df = pd.DataFrame([{
            'Timestamp': entry['timestamp'][:19].replace('T', ' '),
            'Ticket': entry['ticket_id'],
            'Action': entry['action'].replace('_', ' ').title(),
            'Status': entry['status'].replace('_', ' ').title(),
            'Risk': entry.get('risk_level', 'N/A').upper(),
            'Triggered By': entry['triggered_by'].title()
        } for entry in reversed(audit_log)])  # Most recent first
        
        st.dataframe(audit_df, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🗑️ Clear Audit Log", type="secondary"):
                st.session_state.agent.clear_audit_log()
                st.success("Audit log cleared!")
                st.rerun()
    else:
        st.info("No actions logged yet. Run the agent analysis to see the audit trail.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 Self-Healing Support Agent | Powered by Google Gemini AI | Built for E-commerce Migration Support</p>
</div>
""", unsafe_allow_html=True)