# AI Procurement Negotiation System

FastAPI backend for AI-powered procurement negotiations.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## API Docs

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Project Structure

```
app/
├── main.py           # FastAPI app
├── core/             # Config, database
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
├── repositories/     # Data access layer
├── services/         # Gemini client, negotiation agent
├── api/routes/       # API endpoints
└── utils/           # Prompt builder
```
