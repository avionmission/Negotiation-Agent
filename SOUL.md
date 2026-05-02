
You are a senior backend engineer tasked with designing a production-grade scaffold for an agentic negotiation system.

## Objective

Explain the system clearly and generate a working backend scaffold using:

* FastAPI (Python)
* Gemini API (LLM integration)
* SQLite (initial database, designed to be swappable with Postgres)

The scaffold must:

* Run immediately without errors
* Include clear structure, typing, and separation of concerns
* Allow easy extension of routes, services, and agent logic

---

## System Overview

We are building a **buyer-driven agentic negotiation platform**:

### Core Concepts

1. **Buyer**

   * Creates an "Agent" representing a procurement task
   * Defines constraints: budget, requirements, deadline, pricing structure
   * Invites suppliers via email

2. **Agent (Core System Actor)**

   * Stateful entity
   * Holds:

     * Buyer preferences
     * Constraints (budget, pricing breakdown, deadline)
     * Knowledge base (optional context)
   * Conducts negotiations autonomously via chat
   * Generates:

     * Offers
     * Counter-offers (bounded rounds)
     * Summaries

3. **Supplier**

   * Accesses system via secure tokenized link
   * Only interacts through a chat interface with the agent
   * Cannot see internal constraints or summaries

---

## Functional Flow

1. Buyer creates Agent
2. Buyer adds Suppliers (email + secure link)
3. Supplier accesses chat via token
4. Agent:

   * Sends initial offer
   * Receives supplier response
   * Evaluates using constraints + knowledge base
   * Sends optimized counter-offer (max 2–3 rounds)
5. Outcomes:

   * Accept → generate deal summary → buyer approval → finalize
   * Reject / no response → mark inactive
   * Renegotiate loop (bounded)
6. Buyer can:

   * View all chats
   * View private summaries

---

## Technical Requirements

### 1. Project Structure

Design a clean, production-ready layout, for example:

* app/

  * main.py
  * api/ (routers)
  * core/ (config, settings)
  * models/ (SQLAlchemy models)
  * schemas/ (Pydantic)
  * services/ (business logic, agent logic)
  * db/ (session, base)
  * integrations/

    * gemini_client.py
  * utils/

Include:

* Dependency injection
* Environment-based config
* Logging setup

---

### 2. Database Design (SQLite initially)

Define models for:

* Buyer
* Agent
* Supplier
* Conversation
* Message
* DealSummary

Include:

* Proper relationships
* Timestamps
* Status fields (e.g., ACTIVE, INACTIVE, ACCEPTED)

---

### 3. API Design (FastAPI)

Create stubbed but working endpoints:

* POST /agents
* GET /agents/{id}
* POST /agents/{id}/suppliers
* GET /agents/{id}/conversations
* POST /chat/{conversation_id}/message
* GET /summaries/{agent_id}

Endpoints should:

* Validate input
* Return structured responses
* Not contain full logic yet (use service layer)

---

### 4. Agent Logic Layer

Create a service that:

* Generates initial offers
* Handles supplier messages
* Produces counter-offers
* Calls Gemini API (stubbed but wired)

Do NOT fully implement intelligence—just scaffold:

* Clear interfaces
* Placeholder methods

---

### 5. Gemini Integration

* Create a wrapper client
* Include:

  * prompt interface
  * error handling
  * timeout handling
* Mock response fallback if API key not present

---

### 6. Authentication (Lightweight for now)

* Token-based supplier access
* Simple placeholder (no full auth system required yet)

---

### 7. Execution Requirements

* Must run with:
  uvicorn app.main:app --reload

* No runtime errors

* Include:

  * requirements.txt or pyproject.toml
  * minimal README with setup instructions

---

## Output Expectations

1. First: a concise explanation of the system architecture in engineering terms
2. Then: full project scaffold (files + code)
3. Code must be:

   * Clean
   * Typed
   * Modular
   * Immediately runnable

Avoid overengineering, but follow best practices expected of a senior backend engineer.

Do not skip wiring—everything should connect end-to-end, even if logic is stubbed.
