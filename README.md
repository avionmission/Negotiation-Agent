# Negotiation Agent

Buyer-driven agentic negotiation platform with FastAPI, SQLite, and Gemini API.

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```bash
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./negotiation.db
DEBUG=true
```

## Run

```bash
uvicorn app.main:app --reload
```

## API Docs

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health: http://127.0.0.1:8000/health

## API Endpoints

### Buyers

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/buyers` | Create buyer |
| GET | `/api/v1/buyers/{id}` | Get buyer |

### Agents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agents` | Create agent (DRAFT) |
| GET | `/api/v1/agents/{id}` | Get agent |
| PATCH | `/api/v1/agents/{id}` | Update agent (DRAFT only) |
| GET | `/api/v1/agents` | List agents |
| POST | `/api/v1/agents/{id}/activate` | Activate agent |
| POST | `/api/v1/agents/{id}/suppliers` | Add supplier |
| GET | `/api/v1/agents/{id}/suppliers` | List suppliers |
| POST | `/api/v1/agents/{id}/conversations` | Create conversation |
| GET | `/api/v1/agents/{id}/conversations` | List conversations |

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/conversations/{id}` | Get conversation detail |
| POST | `/api/v1/chat/{id}/message` | Send chat message |
| POST | `/api/v1/conversations/{id}/renegotiate` | Start renegotiation |

### Summaries

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/summaries/{agent_id}` | Get summaries |
| POST | `/api/v1/summaries/{id}/approve` | Approve summary |
| POST | `/api/v1/summaries/{id}/reject` | Reject summary |

## State Machine

### Agent Status
- `DRAFT` → `ACTIVE` → `COMPLETED` / `CANCELLED`

### Conversation Status
- `ACTIVE` → `NEGOTIATING` → `ACCEPTED` / `REJECTED` / `EXPIRED`

### Supplier Status  
- `INVITED` → `ACTIVE` → `WON` / `LOST`

### Deal Summary Status
- `PENDING` → `APPROVED` / `REJECTED` → `FINALIZED`

## Test Results

```
=== 1. Create Buyer ===
{"status":"DRAFT","id":"...","name":"John Doe",...}

=== 2. Create Agent (DRAFT) ===
{"status":"DRAFT",...}

=== 3. Get Agent ===
{"status":"DRAFT",...}

=== 4. Update Agent (while DRAFT) ===
{"status":"DRAFT",...} ✓

=== 5. Activate Agent ===
{"status":"ACTIVE",...}

=== 6. Update After Activation ===
{"detail":"Agent cannot be modified after activation"} ✓

=== 7-10. Add Supplier & Conversation ===
Supplier: {status:"INVITED", access_token:"..."}
Conversation: {status:"ACTIVE", negotiation_round:0}

=== 11-13. Chat Flow ===
Round 0: {negotiation_round:1, status:"NEGOTIATING"}
Round 1: {negotiation_round:2, status:"ACCEPTED", summary_id:"..."}

=== 14-16. Summary Approval ===
Summary: {status:"PENDING", is_auto_generated:true}
Approve: {status:"APPROVED"}
Agent: {status":"COMPLETED"}

=== 17-19. Final State ===
Supplier: {status":"WON"}
Agent: {status":"COMPLETED"}
```

## Project Structure

```
app/
├── main.py                # FastAPI app entry point
├── api/routes/            # API endpoints
├── core/               # Config, settings, logging
├── db/                 # Database session
├── models/             # SQLAlchemy models
├── schemas/            # Pydantic schemas
├── services/           # Business logic & agent service
└── integrations/      # Gemini client
```