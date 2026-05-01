from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import suppliers, negotiations, chat

app = FastAPI(title="AI Procurement Negotiation System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(suppliers.router, prefix="/api")
app.include_router(negotiations.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "AI Procurement Negotiation System API"}
