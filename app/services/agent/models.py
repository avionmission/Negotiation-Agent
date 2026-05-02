from pydantic import BaseModel
from enum import Enum
from typing import Optional, List

class Intent(str, Enum):
    COUNTER = "COUNTER"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    QUERY = "QUERY"
    GREETING = "GREETING"

class ParsedMessage(BaseModel):
    intent: Intent
    offered_price: Optional[float] = None
    reasoning: Optional[str] = None

class AgentAction(str, Enum):
    SEND_COUNTER = "SEND_COUNTER"
    SEND_ACCEPTANCE = "SEND_ACCEPTANCE"
    SEND_REJECTION = "SEND_REJECTION"
    ASK_CLARIFICATION = "ASK_CLARIFICATION"

class AgentDecision(BaseModel):
    action: AgentAction
    suggested_price: Optional[float] = None
    strategy_note: str
