from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add root directory to Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Now import from root
from agent import HealingAgent
from datagenerator import TicketGenerator

# Rest stays the same...
import json

app = Flask(__name__)
CORS(app)

# Initialize
agent = HealingAgent()
ticket_generator = TicketGenerator()


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Backend API is running'
    })

@app.route('/api/generate-tickets', methods=['POST'])
def generate_new_tickets():
    """Generate fresh tickets dynamically"""
    try:
        data = request.json or {}
        count = data.get('count', 10)
        force_patterns = data.get('force_patterns', True)
        
        # Generate new tickets
        tickets = ticket_generator.generate_tickets(
            count=count,
            force_patterns=force_patterns
        )
        
        # Save to file
        ticket_generator.save_to_file(tickets)
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(tickets)} new tickets',
            'data': tickets,
            'count': len(tickets)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """Get all tickets"""
    try:
        tickets = agent.load_tickets()
        return jsonify({
            'success': True,
            'data': tickets,
            'count': len(tickets)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/observe', methods=['POST'])
def observe_patterns():
    """Observe patterns in tickets"""
    try:
        tickets = agent.load_tickets()
        patterns = agent.observe(tickets)
        return jsonify({
            'success': True,
            'data': patterns
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_ticket():
    """Analyze a single ticket"""
    try:
        data = request.json
        ticket = data.get('ticket')
        patterns = data.get('patterns', {})
        
        analysis = agent.reason(ticket, patterns)
        
        return jsonify({
            'success': True,
            'data': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/decide', methods=['POST'])
def make_decision():
    """Make decision for a ticket"""
    try:
        data = request.json
        ticket = data.get('ticket')
        analysis = data.get('analysis')
        
        decision = agent.decide(ticket, analysis)
        
        return jsonify({
            'success': True,
            'data': decision
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/execute', methods=['POST'])
def execute_action():
    """Execute an action"""
    try:
        data = request.json
        decision = data.get('decision')
        
        result = agent.act(decision)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/process-all', methods=['POST'])
def process_all_tickets():
    """Process all tickets through full agent loop"""
    try:
        results = agent.process_all_tickets()
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/approve', methods=['POST'])
def approve_action():
    """Approve and execute a pending action (Human-in-the-Loop)"""
    try:
        data = request.json
        ticket_id = data.get('ticket_id')
        
        if not ticket_id:
            return jsonify({
                'success': False,
                'error': 'ticket_id is required'
            }), 400
        
        result = agent.execute_approved_action(ticket_id)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f'Action for {ticket_id} approved and executed',
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/audit-log', methods=['GET'])
def get_audit_log():
    """Get the action audit log"""
    try:
        audit_log = agent.get_audit_log()
        return jsonify({
            'success': True,
            'data': audit_log,
            'count': len(audit_log)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ticket/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get a single ticket by ID"""
    try:
        tickets = agent.load_tickets()
        ticket = next((t for t in tickets if t['ticket_id'] == ticket_id), None)
        
        if ticket:
            return jsonify({
                'success': True,
                'data': ticket
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Ticket {ticket_id} not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/clear-audit-log', methods=['POST'])
def clear_audit_log():
    """Clear the audit log (for testing)"""
    try:
        result = agent.clear_audit_log()
        return jsonify({
            'success': True,
            'message': 'Audit log cleared'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting Backend API Server...")
    print("API running at: http://localhost:5000")
    print("Endpoints:")
    print("   - GET  /api/health")
    print("   - POST /api/generate-tickets")
    print("   - GET  /api/tickets")
    print("   - GET  /api/ticket/<id>")
    print("   - POST /api/observe")
    print("   - POST /api/analyze")
    print("   - POST /api/decide")
    print("   - POST /api/execute")
    print("   - POST /api/process-all")
    print("   - POST /api/approve")
    print("   - GET  /api/audit-log")
    print("   - POST /api/clear-audit-log")
    
    app.run(debug=True, port=5000, host='0.0.0.0')