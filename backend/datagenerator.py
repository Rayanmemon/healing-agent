import json
import os
import random
from datetime import datetime, timedelta

class TicketGenerator:
    """Generate realistic support tickets dynamically"""
    
    def __init__(self):
        self.error_templates = {
            'webhook_timeout': {
                'issue_templates': [
                    "Checkout page shows 'Webhook timeout' error",
                    "Orders not processing - webhook timeout",
                    "Webhook timeout on checkout - URGENT",
                    "Payment processing stuck - webhook error",
                    "Customers can't complete orders - webhook failure"
                ],
                'merchant_messages': [
                    "My customers can't complete purchases! Getting webhook timeout on order.created event. This started right after migration.",
                    "Checkout completely broken! Same webhook error as before. Losing sales every minute!",
                    "This is the third time today! Webhook keeps timing out. Is this a platform issue?",
                    "Orders failing at checkout. Webhook timeout error keeps appearing. Help urgently needed!",
                    "Critical issue - webhook not responding. All transactions failing since migration."
                ],
                'error_log': "WebhookTimeout: order.created webhook failed after 30s - endpoint unreachable",
                'severity': 'critical',
                'checkout_failures_range': (40, 100),
                'affected_customers_range': (20, 50)
            },
            'image_404': {
                'issue_templates': [
                    "Product images not loading on frontend",
                    "All images showing 404 errors",
                    "Broken product images after migration",
                    "Image URLs returning 404",
                    "Product gallery not displaying"
                ],
                'merchant_messages': [
                    "After migration, all my product images are broken. Customers see placeholder images. Getting 404 errors on image URLs.",
                    "Product pages look terrible - no images loading. Everything was fine before migration.",
                    "Image CDN seems broken. All product photos returning 404. This is affecting sales!",
                    "Customer complaints about missing product images. Getting 404 on all image requests.",
                    "Product catalog completely broken - no images loading anywhere on site."
                ],
                'error_log': "404 Not Found: /api/v2/products/images/ - path structure changed in headless",
                'severity': 'high',
                'checkout_failures_range': (0, 15),
                'affected_customers_range': (0, 10)
            },
            'auth_failure': {
                'issue_templates': [
                    "API authentication failing after migration",
                    "Getting 401 errors on all API calls",
                    "API credentials not working",
                    "Authentication broken post-migration",
                    "Unable to connect to API - auth errors"
                ],
                'merchant_messages': [
                    "Getting 401 errors on all API calls. My app can't connect anymore. Migration guide wasn't clear about new auth format.",
                    "API authentication completely broken. Our mobile app can't access any endpoints.",
                    "All API requests failing with 401. Used to work fine before migration. Need urgent help!",
                    "Integration with our POS system broken - invalid credentials error. What changed?",
                    "API keys not working anymore. Getting unauthorized errors on every request."
                ],
                'error_log': "401 Unauthorized: Invalid API credentials format - expecting Bearer token",
                'severity': 'critical',
                'checkout_failures_range': (0, 5),
                'affected_customers_range': (0, 0)
            },
            'shipping_calculation': {
                'issue_templates': [
                    "Shipping rates not calculating correctly",
                    "Wrong shipping prices at checkout",
                    "Free shipping not working",
                    "Shipping cost calculation broken",
                    "Incorrect delivery charges"
                ],
                'merchant_messages': [
                    "Free shipping isn't working anymore. Customers being charged when they shouldn't be.",
                    "Shipping calculator broken - showing wrong rates. Some orders charged $0, others too much.",
                    "International shipping rates completely wrong after migration. Losing international customers.",
                    "Free shipping threshold not working. Orders over $50 still being charged shipping.",
                    "Shipping rules from old platform didn't migrate properly. Need to reconfigure everything?"
                ],
                'error_log': "ShippingError: Legacy shipping rules not migrated to new format",
                'severity': 'medium',
                'checkout_failures_range': (5, 25),
                'affected_customers_range': (3, 15)
            },
            'cart_persistence': {
                'issue_templates': [
                    "Shopping carts not persisting",
                    "Cart items disappearing",
                    "Cart resets after page refresh",
                    "Lost cart sessions",
                    "Cart not saving between pages"
                ],
                'merchant_messages': [
                    "Customers complaining that cart items disappear when they navigate away. Cart persistence broken.",
                    "Shopping cart resets randomly. Customers have to re-add products. Very frustrating!",
                    "Cart session management not working. Items vanish after refresh. Is this a cookie issue?",
                    "Lost sales because carts don't persist. Customers give up and shop elsewhere.",
                    "Cart abandonment way up - items keep disappearing from carts during checkout."
                ],
                'error_log': "SessionError: Cart session cookie format incompatible with headless architecture",
                'severity': 'high',
                'checkout_failures_range': (30, 70),
                'affected_customers_range': (20, 40)
            },
            'inventory_sync': {
                'issue_templates': [
                    "Inventory counts not syncing",
                    "Stock levels incorrect",
                    "Out of stock items showing available",
                    "Inventory data mismatch",
                    "Product availability wrong"
                ],
                'merchant_messages': [
                    "Inventory not syncing between systems. Selling items that are out of stock!",
                    "Stock levels completely wrong. Shows 0 for products we have hundreds of.",
                    "Overselling products because inventory sync broken. Customers angry about cancellations.",
                    "Real-time inventory updates not working. Have to manually sync every hour.",
                    "Inventory webhooks not firing. Stock counts frozen at migration snapshot."
                ],
                'error_log': "InventorySyncError: Webhook inventory.updated not triggering - legacy polling disabled",
                'severity': 'critical',
                'checkout_failures_range': (10, 40),
                'affected_customers_range': (5, 20)
            },
            'payment_gateway': {
                'issue_templates': [
                    "Payment gateway connection failing",
                    "Card processing not working",
                    "Payment declined errors",
                    "Gateway timeout at checkout",
                    "Payment integration broken"
                ],
                'merchant_messages': [
                    "Payment processor keeps timing out. Valid cards being declined. Losing sales!",
                    "Stripe integration broken after migration. All payments failing with generic error.",
                    "Payment gateway not responding. Customers can't complete transactions.",
                    "Card tokenization failing. Payment API returns 500 errors on checkout.",
                    "PayPal integration completely broken. Redirect loop when customers try to pay."
                ],
                'error_log': "PaymentGatewayError: Connection timeout to payment processor - SSL cert mismatch",
                'severity': 'critical',
                'checkout_failures_range': (60, 120),
                'affected_customers_range': (30, 60)
            }
        }
        
        self.migration_stages = [
            'pre-migration',
            'migration-in-progress',
            'post-migration-day-1',
            'post-migration-day-2',
            'post-migration-day-3',
            'post-migration-day-5',
            'post-migration-week-1',
            'post-migration-week-2'
        ]
    
    def generate_tickets(self, count=10, force_patterns=True):
        """
        Generate random realistic tickets
        
        Args:
            count: Number of tickets to generate
            force_patterns: If True, ensures some error types repeat (creates patterns)
        """
        tickets = []
        error_types = list(self.error_templates.keys())
        
        # If forcing patterns, ensure at least 3 tickets share same error
        if force_patterns and count >= 6:
            # Pick 1-2 error types to create patterns
            pattern_errors = random.sample(error_types, k=random.randint(1, 2))
            pattern_count = random.randint(3, min(5, count // 2))
            
            # Generate pattern tickets
            for i in range(pattern_count):
                error_type = pattern_errors[i % len(pattern_errors)]
                tickets.append(self._generate_ticket(
                    ticket_id=f"T{str(i+1).zfill(3)}",
                    merchant_id=f"M{random.randint(100, 999)}",
                    error_type=error_type,
                    timestamp=datetime.now() - timedelta(minutes=random.randint(5, 60))
                ))
            
            # Generate remaining random tickets
            for i in range(pattern_count, count):
                error_type = random.choice(error_types)
                tickets.append(self._generate_ticket(
                    ticket_id=f"T{str(i+1).zfill(3)}",
                    merchant_id=f"M{random.randint(100, 999)}",
                    error_type=error_type,
                    timestamp=datetime.now() - timedelta(minutes=random.randint(5, 120))
                ))
        else:
            # Fully random generation
            for i in range(count):
                error_type = random.choice(error_types)
                tickets.append(self._generate_ticket(
                    ticket_id=f"T{str(i+1).zfill(3)}",
                    merchant_id=f"M{random.randint(100, 999)}",
                    error_type=error_type,
                    timestamp=datetime.now() - timedelta(minutes=random.randint(5, 120))
                ))
        
        # Sort by timestamp
        tickets.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return tickets
    
    def _generate_ticket(self, ticket_id, merchant_id, error_type, timestamp):
        """Generate a single ticket"""
        template = self.error_templates[error_type]
        
        checkout_failures = random.randint(*template['checkout_failures_range'])
        affected_customers = random.randint(*template['affected_customers_range'])
        
        return {
            'ticket_id': ticket_id,
            'merchant_id': merchant_id,
            'timestamp': timestamp.isoformat() + 'Z',
            'issue': random.choice(template['issue_templates']),
            'merchant_message': random.choice(template['merchant_messages']),
            'migration_stage': random.choice(self.migration_stages),
            'error_log': template['error_log'],
            'severity': template['severity'],
            'checkout_failures': checkout_failures,
            'affected_customers': affected_customers,
            'error_type': error_type  # Hidden metadata for testing
        }
    
    def save_to_file(self, tickets, filename=None):
        """Save tickets to JSON file inside the data folder"""
        # Always save to data/tickets.json inside healing-agent
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        if filename is None:
            filename = os.path.join(data_dir, 'tickets.json')
        else:
            # If a filename is provided, ensure it's inside the data folder
            filename = os.path.join(data_dir, os.path.basename(filename))

        # Remove metadata before saving
        clean_tickets = []
        for ticket in tickets:
            clean_ticket = {k: v for k, v in ticket.items() if k != 'error_type'}
            clean_tickets.append(clean_ticket)

        with open(filename, 'w') as f:
            json.dump(clean_tickets, f, indent=2)

        return filename

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate realistic support tickets')
    parser.add_argument('--count', type=int, default=5, help='Number of tickets to generate')
    parser.add_argument('--no-patterns', action='store_true', help='Disable forced patterns')
    parser.add_argument('--output', type=str, default='data/tickets.json', help='Output file path')
    
    args = parser.parse_args()
    
    generator = TicketGenerator()
    tickets = generator.generate_tickets(
        count=args.count,
        force_patterns=not args.no_patterns
    )
    
    filename = generator.save_to_file(tickets, args.output)
    
    print(f"✅ Generated {len(tickets)} tickets")
    print(f"📁 Saved to: {filename}")
    print(f"\n📊 Ticket Summary:")
    print(f"   - Critical: {sum(1 for t in tickets if t['severity'] == 'critical')}")
    print(f"   - High: {sum(1 for t in tickets if t['severity'] == 'high')}")
    print(f"   - Medium: {sum(1 for t in tickets if t['severity'] == 'medium')}")
    print(f"   - Total checkout failures: {sum(t['checkout_failures'] for t in tickets)}")
    print(f"   - Total affected customers: {sum(t['affected_customers'] for t in tickets)}")
    
    # Show error type distribution
    from collections import Counter
    error_counts = Counter([t['error_type'] for t in tickets])
    print(f"\n🔍 Error Distribution:")
    for error_type, count in error_counts.most_common():
        print(f"   - {error_type}: {count}")
        if count >= 3:
            print(f"     ⚠️ PATTERN DETECTED!")