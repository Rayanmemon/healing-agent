# 📡 API Documentation

Base URL: `http://localhost:5000`

---

## Endpoints

### Health Check

**`GET /api/health`**

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Backend API is running"
}
```

---

### Ticket Management

**`GET /api/tickets`**

Get all loaded support tickets.

**Response:**
```json
{
  "success": true,
  "data": [ /* array of ticket objects */ ],
  "count": 10
}
```

---

**`GET /api/ticket/<ticket_id>`**

Get a single ticket by its ID.

**Response:**
```json
{
  "success": true,
  "data": {
    "ticket_id": "TKT-001",
    "merchant_id": "MERCH-123",
    "issue": "...",
    "..."
  }
}
```

---

**`POST /api/generate-tickets`**

Generate new synthetic tickets for testing.

**Request Body:**
```json
{
  "count": 10,
  "force_patterns": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Generated 10 new tickets",
  "data": [ /* array of ticket objects */ ],
  "count": 10
}
```

---

### Agent Loop Endpoints

**`POST /api/observe`**

Run the OBSERVE phase on loaded tickets. Detects patterns.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_tickets": 10,
    "error_patterns": { "WebhookError": 3, "..." },
    "critical_count": 2
  }
}
```

---

**`POST /api/analyze`**

Run the REASON phase for a single ticket.

**Request Body:**
```json
{
  "ticket": { /* ticket object */ },
  "patterns": { /* patterns from /observe */ }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "root_cause": "webhook_configuration",
    "confidence": 85,
    "is_pattern": false,
    "assumptions": ["..."]
  }
}
```

---

**`POST /api/decide`**

Run the DECIDE phase for a ticket.

**Request Body:**
```json
{
  "ticket": { /* ticket object */ },
  "analysis": { /* analysis from /analyze */ }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "action": "send_webhook_configuration_guide",
    "risk_level": "low",
    "requires_approval": false,
    "reasoning": "..."
  }
}
```

---

**`POST /api/execute`**

Run the ACT phase for a decision.

**Request Body:**
```json
{
  "decision": { /* decision from /decide */ }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "executed",
    "action_details": { "..." }
  }
}
```

---

**`POST /api/process-all`**

Run the **full OODA loop** on all loaded tickets at once.

**Response:**
```json
{
  "success": true,
  "data": [ /* array of { ticket, analysis, decision, action_result } */ ],
  "count": 10
}
```

---

### Human-in-the-Loop (HITL)

**`POST /api/approve`**

Approve and execute a pending high-risk action.

**Request Body:**
```json
{
  "ticket_id": "TKT-001"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Action for TKT-001 approved and executed",
  "data": {
    "status": "executed",
    "action_details": { "..." }
  }
}
```

**Response (Not Found):**
```json
{
  "success": false,
  "error": "No pending approval found for ticket TKT-001"
}
```

---

### Audit Log

**`GET /api/audit-log`**

Get the persistent log of all agent actions.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-01-31T22:00:00.000000",
      "ticket_id": "TKT-001",
      "action": "send_webhook_configuration_guide",
      "status": "executed",
      "triggered_by": "auto"
    }
  ],
  "count": 5
}
```

---

**`POST /api/clear-audit-log`**

Clear the audit log (for testing/development).

**Response:**
```json
{
  "success": true,
  "message": "Audit log cleared"
}
```
