
You are an expert backend engineer. Generate a production-grade FastAPI project scaffold for an AI-powered procurement negotiation system.

## Core Requirements

* Backend framework: FastAPI
* ORM: SQLAlchemy (sync version)
* Database: SQLite
* LLM integration: Gemini API (create placeholder client, no real API key)
* Architecture: clean separation of concerns (routes, services, repositories, models, schemas)

## Project Structure

Create the following directory and file structure:

app/
├── main.py
├── core/
│   ├── config.py
│   ├── database.py
│
├── models/
│   ├── supplier.py
│   ├── negotiation.py
│   ├── message.py
│   ├── offer.py
│
├── schemas/
│   ├── supplier.py
│   ├── negotiation.py
│   ├── message.py
│   ├── offer.py
│
├── repositories/
│   ├── base.py
│   ├── supplier_repo.py
│   ├── negotiation_repo.py
│   ├── message_repo.py
│   ├── offer_repo.py
│
├── services/
│   ├── gemini_client.py
│   ├── negotiation_agent.py
│
├── api/
│   ├── routes/
│   │   ├── suppliers.py
│   │   ├── negotiations.py
│   │   ├── chat.py
│
├── utils/
│   ├── prompt_builder.py
│
└── db/
└── sqlite.db

---

## Implementation Requirements

### 1. main.py

* Initialize FastAPI app
* Include all routers
* Setup basic middleware (CORS enabled)

---

### 2. database.py

* Create SQLAlchemy engine for SQLite
* Define SessionLocal
* Provide dependency: get_db()

---

### 3. Models (SQLAlchemy)

Define tables:

Supplier:

* id (PK)
* name
* contact_info
* category
* rating

Negotiation:

* id
* title
* system_prompt
* target_price
* max_budget
* status
* created_at

Message:

* id
* negotiation_id
* supplier_id
* sender ("agent" | "supplier")
* content
* timestamp

Offer:

* id
* negotiation_id
* supplier_id
* price
* terms
* created_at

---

### 4. Schemas (Pydantic, v2 style)

For each entity create:

* Create schema
* Response schema (with from_attributes = True)

---

### 5. Repositories

Implement repository pattern:

BaseRepository:

* add()
* commit logic

Each repo should:

* encapsulate DB queries
* avoid business logic

Important methods:

MessageRepository:

* create_message()
* get_history(limit=10)

OfferRepository:

* create_offer()
* get_best_offer()

---

### 6. Services

#### gemini_client.py

* Create class GeminiClient
* Method: generate(prompt: str) → str
* Return mock response for now (no real API call)

---

#### negotiation_agent.py

* Class NegotiationAgent
* Method: generate_reply()
* Uses prompt_builder
* No DB access inside this class

---

### 7. prompt_builder.py

* Function build_prompt(system_prompt, negotiation, supplier, history)
* Return formatted string

---

### 8. API Routes

#### suppliers.py

* POST /suppliers
* GET /suppliers

#### negotiations.py

* POST /negotiations
* POST /negotiations/{id}/run

#### chat.py

* POST /chat/{negotiation_id}/{supplier_id}
* Handles message loop:

  * save supplier message
  * generate AI reply
  * save agent reply

---

### 9. Dependency Injection

* Use Depends(get_db)
* Instantiate repositories inside routes
* Pass repositories into services

---

### 10. Code Quality Constraints

* Do NOT mix DB logic in routes
* Do NOT call LLM inside routes directly
* Use clear typing everywhere
* Add docstrings to key classes/functions
* Keep functions small and focused

---

### 11. Output Format

* Generate ALL files with full code

* Include imports

* Ensure project runs with:

  uvicorn app.main:app --reload

* No placeholders like "implement this later"

* No pseudo-code

---

### 12. Optional (if space allows)

* Add simple logging utility
* Add basic error handling

---

## Goal

Produce a clean, minimal, scalable backend scaffold suitable for building an AI negotiation agent that interacts with multiple suppliers, stores chat history, and evaluates offers.

The code should be immediately runnable and extensible.

Don't implement anything, we'll go step by step. Just create project structure we can work within. It should run without errors.
