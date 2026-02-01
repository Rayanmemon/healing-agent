import os
import json
import re
from collections import Counter
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class HealingAgent:
    def __init__(self):
        # Configure Groq client
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.model_name = 'llama-3.3-70b-versatile'  # Fast and capable
        self.tickets = []
        self.decisions = []
        
    def load_tickets(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "data", "tickets.json")

        print("Loading tickets from:", data_path)

        with open(data_path, "r", encoding="utf-8") as f:
            self.tickets = json.load(f)

        return self.tickets
    
    def observe(self, tickets):
        """OBSERVE: Detect patterns in tickets"""
        if not tickets:
            return {}
            
        # Pattern detection
        error_types = []
        for t in tickets:
            error_log = t.get('error_log', '')
            if ':' in error_log:
                error_type = error_log.split(':')[0]
            else:
                error_type = 'Unknown'
            error_types.append(error_type)
        
        error_counts = Counter(error_types)
        
        # Calculate metrics
        total_checkout_failures = sum(t.get('checkout_failures', 0) for t in tickets)
        total_affected_customers = sum(t.get('affected_customers', 0) for t in tickets)
        
        patterns = {
            'total_tickets': len(tickets),
            'error_patterns': dict(error_counts),
            'critical_count': sum(1 for t in tickets if t.get('severity') == 'critical'),
            'migration_stages': dict(Counter([t.get('migration_stage', 'unknown') for t in tickets])),
            'total_checkout_failures': total_checkout_failures,
            'total_affected_customers': total_affected_customers
        }
        
        return patterns
    
    def reason(self, ticket, patterns):
        """REASON: Use Gemini to analyze root cause"""
        
        prompt = f"""You are an expert AI support agent analyzing e-commerce platform migration issues.

TICKET INFORMATION:
- Ticket ID: {ticket['ticket_id']}
- Merchant ID: {ticket['merchant_id']}
- Issue: {ticket['issue']}
- Merchant Message: {ticket['merchant_message']}
- Error Log: {ticket['error_log']}
- Migration Stage: {ticket['migration_stage']}
- Severity: {ticket['severity']}
- Checkout Failures: {ticket.get('checkout_failures', 0)}
- Affected Customers: {ticket.get('affected_customers', 0)}

SYSTEM-WIDE PATTERNS DETECTED:
- Total tickets in system: {patterns['total_tickets']}
- Error type frequency: {patterns['error_patterns']}
- Critical severity tickets: {patterns['critical_count']}
- Migration stage distribution: {patterns['migration_stages']}
- Total checkout failures across all tickets: {patterns['total_checkout_failures']}

ANALYSIS REQUIRED:
1. ROOT CAUSE: Determine if this is:
   - "webhook_configuration" (merchant didn't update webhook URLs/endpoints)
   - "platform_bug" (platform code regression or bug)
   - "migration_issue" (data migration or process problem)
   - "documentation_gap" (unclear migration instructions)

2. PATTERN DETECTION: Is this isolated or affecting multiple merchants?

3. CONFIDENCE: Rate 0-100. Be conservative and calibrated:
   - 85-100: Error message DIRECTLY states the cause with no ambiguity
   - 70-84: Strong correlation and clear evidence, minimal assumptions
   - 55-69: Educated guess based on patterns, some assumptions made
   - 40-54: Multiple possible causes, moderate uncertainty
   - Below 40: Highly uncertain, needs more information

4. ASSUMPTIONS: What are you assuming to reach this conclusion?

Respond ONLY with valid JSON (no markdown, no code blocks):
{{
    "root_cause": "one of the four options above",
    "root_cause_explanation": "2-3 sentence detailed explanation of why you chose this root cause",
    "is_pattern": true or false,
    "pattern_details": "if pattern detected, explain what the pattern is and how many merchants affected",
    "confidence": 75,
    "assumptions": ["assumption 1", "assumption 2"],
    "affected_merchants": 1,
    "recommended_priority": "low/medium/high/critical"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert AI support agent. Always respond with valid JSON only, no markdown."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024
            )
            response_text = response.choices[0].message.content
            
            # Clean response - remove markdown code blocks if present
            response_text = response_text.strip()
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'^```\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            
            # Extract JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response_text[start:end]
                analysis = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"Warning: Error parsing Groq response for {ticket['ticket_id']}: {e}")
            # Fallback analysis
            analysis = {
                "root_cause": "unknown",
                "root_cause_explanation": f"Analysis failed: {str(e)}",
                "is_pattern": False,
                "pattern_details": "",
                "confidence": 50,
                "assumptions": ["Unable to parse AI response"],
                "affected_merchants": 1,
                "recommended_priority": ticket.get('severity', 'medium')
            }
        
        return analysis
    
    def decide(self, ticket, analysis):
        """DECIDE: Determine action based on analysis"""
        
        confidence = analysis.get('confidence', 0)
        is_pattern = analysis.get('is_pattern', False)
        severity = ticket.get('severity', 'medium')
        root_cause = analysis.get('root_cause', 'unknown')
        affected_merchants = analysis.get('affected_merchants', 1)
        
        # Decision logic with clear rules
        if is_pattern and affected_merchants >= 3:
            action = "escalate_to_engineering"
            risk_level = "high"
            requires_approval = True
            reasoning = f"PATTERN DETECTED: {affected_merchants} merchants experiencing same issue. Platform-wide problem likely."
            
        elif root_cause == "webhook_configuration" and confidence > 70:
            action = "send_webhook_configuration_guide"
            risk_level = "low"
            requires_approval = False
            reasoning = "High confidence merchant configuration error. Automated guide can resolve."
            
        elif root_cause == "documentation_gap":
            action = "update_migration_documentation"
            risk_level = "low"
            requires_approval = False
            reasoning = "Documentation unclear. Will update guide and notify affected merchants."
            
        elif root_cause == "platform_bug" or (severity == "critical" and confidence > 60):
            action = "escalate_to_engineering"
            risk_level = "high"
            requires_approval = True
            reasoning = "Potential platform bug or critical issue requiring engineering investigation."
            
        elif severity == "critical":
            action = "immediate_support_escalation"
            risk_level = "medium"
            requires_approval = True
            reasoning = "Critical severity - requires immediate human attention regardless of root cause."
            
        else:
            action = "assign_to_support_team"
            risk_level = "medium"
            requires_approval = False
            reasoning = "Standard support workflow - human agent will investigate."
        
        # Calculate estimated impact
        checkout_failures = ticket.get('checkout_failures', 0)
        affected_customers = ticket.get('affected_customers', 0)
        
        if is_pattern:
            impact = f"{affected_merchants} merchants, ~{checkout_failures * affected_merchants} failed checkouts"
        else:
            impact = f"1 merchant, {checkout_failures} failed checkouts, {affected_customers} customers affected"
        
        decision = {
            'ticket_id': ticket['ticket_id'],
            'action': action,
            'risk_level': risk_level,
            'requires_approval': requires_approval,
            'reasoning': reasoning,
            'confidence': confidence,
            'estimated_impact': impact,
            'analysis': analysis
        }
        
        return decision
    
    def act(self, decision, triggered_by='auto'):
        """ACT: Execute or recommend action"""
        
        if decision['requires_approval']:
            result = {
                'status': 'pending_approval',
                'message': f"⏳ Action '{decision['action']}' requires human approval due to {decision['risk_level']} risk",
                'decision': decision
            }
            # Log pending actions too
            self.log_audit_event(result, triggered_by='system')
        else:
            # Simulate automatic execution
            result = {
                'status': 'executed',
                'message': f"✅ Automatically executed: {decision['action']}",
                'action_details': self._execute_action(decision),
                'decision': decision
            }
            # Log auto-executed actions
            self.log_audit_event(result, triggered_by=triggered_by)
        
        return result

    
    def _execute_action(self, decision):
        """Simulate action execution with realistic details"""
        
        action_map = {
            'send_webhook_configuration_guide': {
                'type': 'automated_email',
                'to': f"merchant_{decision['ticket_id']}@example.com",
                'subject': 'Action Required: Update Webhook Configuration for Headless Migration',
                'body_preview': 'We detected your webhook endpoint is using the old URL format. Please update to: https://api.yourstore.com/webhooks/v2/...',
                'kb_article': 'https://docs.platform.com/migration/webhooks',
                'execution_time': '0.3 seconds'
            },
            'update_migration_documentation': {
                'type': 'documentation_update',
                'page': 'Headless Migration Guide',
                'section': 'Webhook Configuration',
                'change': 'Added clarification about webhook URL format changes and endpoint updates',
                'also_notify': 'All merchants in migration-in-progress stage',
                'execution_time': '1.2 seconds'
            },
            'immediate_support_escalation': {
                'type': 'support_ticket_escalation',
                'priority': 'P0 - Critical',
                'assigned_to': 'Senior Support Engineer (on-call)',
                'sla': '15 minutes response time',
                'notification_sent': 'Slack + PagerDuty',
                'execution_time': '0.5 seconds'
            },
            'escalate_to_engineering': {
                'type': 'engineering_escalation',
                'jira_ticket': f"PLATFORM-{decision['ticket_id'][-3:]}",
                'priority': 'Critical',
                'title': f"Pattern detected: {decision.get('analysis', {}).get('pattern_details', 'Multiple merchant issues')}",
                'assigned_team': 'Platform Engineering',
                'impact': decision.get('estimated_impact', 'Multiple merchants'),
                'execution_time': '0.8 seconds'
            },
            'assign_to_support_team': {
                'type': 'support_queue',
                'queue': 'Migration Support Tier 2',
                'priority': 'Normal',
                'auto_response_sent': True,
                'estimated_response': '2 hours',
                'execution_time': '0.2 seconds'
            }
        }
        
        return action_map.get(decision['action'], {
            'type': 'unknown_action',
            'message': f"Action {decision['action']} not fully implemented"
        })
    
    def log_audit_event(self, action_result, triggered_by='auto'):
        """Log action to persistent audit log"""
        from datetime import datetime
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        audit_path = os.path.join(base_dir, "data", "audit_log.json")
        
        # Load existing log or create new
        if os.path.exists(audit_path):
            with open(audit_path, 'r', encoding='utf-8') as f:
                audit_log = json.load(f)
        else:
            audit_log = []
        
        # Create audit entry
        entry = {
            'timestamp': datetime.now().isoformat(),
            'ticket_id': action_result.get('decision', {}).get('ticket_id', 'unknown'),
            'action': action_result.get('decision', {}).get('action', 'unknown'),
            'status': action_result.get('status', 'unknown'),
            'risk_level': action_result.get('decision', {}).get('risk_level', 'unknown'),
            'triggered_by': triggered_by,
            'message': action_result.get('message', '')
        }
        
        audit_log.append(entry)
        
        # Save updated log
        with open(audit_path, 'w', encoding='utf-8') as f:
            json.dump(audit_log, f, indent=2)
        
        return entry
    
    def get_audit_log(self):
        """Retrieve the audit log"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        audit_path = os.path.join(base_dir, "data", "audit_log.json")
        
        if os.path.exists(audit_path):
            with open(audit_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def execute_approved_action(self, ticket_id):
        """Execute an action that was pending approval (HITL flow)"""
        
        # Find the pending decision for this ticket
        pending_decision = None
        for d in self.decisions:
            if d.get('decision', {}).get('ticket_id') == ticket_id and d.get('status') == 'pending_approval':
                pending_decision = d
                break
        
        if not pending_decision:
            return {
                'success': False,
                'error': f'No pending approval found for ticket {ticket_id}'
            }
        
        decision = pending_decision['decision']
        
        # Execute the action
        action_details = self._execute_action(decision)
        
        result = {
            'success': True,
            'status': 'executed',
            'message': f"✅ Human approved and executed: {decision['action']}",
            'action_details': action_details,
            'decision': decision
        }
        
        # Log this human-triggered execution
        self.log_audit_event(result, triggered_by='human')
        
        # Update the stored decision status
        pending_decision['status'] = 'executed'
        pending_decision['action_details'] = action_details
        
        return result
    
    def clear_audit_log(self):
        """Clear the audit log (for testing/reset)"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        audit_path = os.path.join(base_dir, "data", "audit_log.json")
        
        with open(audit_path, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        return {'success': True, 'message': 'Audit log cleared'}
    
    def process_all_tickets(self):
        """Full agent loop: OBSERVE → REASON → DECIDE → ACT for all tickets"""
        
        tickets = self.load_tickets()
        
        if not tickets:
            return []
        
        print(f"\nAgent Processing {len(tickets)} tickets...\n")
        
        # OBSERVE phase
        patterns = self.observe(tickets)
        print(f"OBSERVE: Detected {patterns['total_tickets']} tickets")
        print(f"   - Critical: {patterns['critical_count']}")
        print(f"   - Error patterns: {patterns['error_patterns']}")
        print(f"   - Total checkout failures: {patterns['total_checkout_failures']}\n")
        
        results = []
        
        for idx, ticket in enumerate(tickets, 1):
            print(f"Processing {idx}/{len(tickets)}: {ticket['ticket_id']}...", end=" ")
            
            # REASON phase
            analysis = self.reason(ticket, patterns)
            
            # DECIDE phase
            decision = self.decide(ticket, analysis)
            
            # ACT phase
            action_result = self.act(decision)
            
            results.append({
                'ticket': ticket,
                'analysis': analysis,
                'decision': decision,
                'action_result': action_result
            })
            
            self.decisions.append(action_result)
            print(f"Done: {action_result['status']}")
        
        print(f"\nAgent processing complete!")
        return results

if __name__ == "__main__":
    print("="*60)
    print("SELF-HEALING SUPPORT AGENT")
    print("="*60)
    
    agent = HealingAgent()
    results = agent.process_all_tickets()
    
    if results:
        print(f"\nSUMMARY REPORT")
        print("="*60)
        
        auto_executed = sum(1 for r in results if r['action_result']['status'] == 'executed')
        pending_approval = sum(1 for r in results if r['action_result']['status'] == 'pending_approval')
        
        print(f"Total Tickets Processed: {len(results)}")
        print(f"Auto-Executed Actions: {auto_executed}")
        print(f"Pending Human Approval: {pending_approval}")
        
        print(f"\nACTIONS BREAKDOWN:")
        actions = [r['decision']['action'] for r in results]
        for action, count in Counter(actions).items():
            print(f"   - {action.replace('_', ' ').title()}: {count}")
        
        print(f"\nROOT CAUSES IDENTIFIED:")
        causes = [r['analysis']['root_cause'] for r in results]
        for cause, count in Counter(causes).items():
            print(f"   - {cause.replace('_', ' ').title()}: {count}")
        
        # Show detailed example
        print(f"\nDETAILED EXAMPLE - {results[0]['ticket']['ticket_id']}:")
        print(f"   Issue: {results[0]['ticket']['issue']}")
        print(f"   Root Cause: {results[0]['analysis']['root_cause']} ({results[0]['analysis']['confidence']}% confidence)")
        print(f"   Action: {results[0]['decision']['action']}")
        print(f"   Status: {results[0]['action_result']['status']}")