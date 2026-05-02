from app.integrations.gemini_client import GeminiClient
from .interpreter import MessageInterpreter
from .strategist import NegotiationStrategist
from .generator import ResponseGenerator
from .models import AgentDecision

class AgentOrchestrator:
    def __init__(self, gemini: GeminiClient):
        self.interpreter = MessageInterpreter(gemini)
        self.strategist = NegotiationStrategist()
        self.generator = ResponseGenerator(gemini)

    def process_step(self, message: str, agent_data: dict, current_round: int, context: str = "") -> tuple[str, float, bool]:
        # THE 8-STEP LOOP (Using Full Knowledge Base)
        
        # Extract constraints from agent_data
        budget = agent_data.get("budget", 0.0)
        base_price = agent_data.get("base_price", 0.0)
        max_rounds = agent_data.get("max_negotiation_rounds", 3)
        
        # Enhance context with Domain and Description
        full_context = f"""
        Project: {agent_data.get('name')}
        Domain: {agent_data.get('domain')} / {agent_data.get('subdomain')}
        Requirement: {agent_data.get('description')}
        Target Price: ${base_price}
        Max Budget: ${budget}
        {context}
        """
        
        # Step 2: Interpret
        parsed = self.interpreter.interpret(message)
        
        # Step 4 & 5: Evaluate & Decide (Strategist now knows the Base Price vs Budget)
        decision = self.strategist.decide(
            parsed, 
            budget=budget, 
            base_price=base_price,
            current_round=current_round, 
            max_rounds=max_rounds
        )
        
        # Step 6: Generate (Generator now has the rich Full Context)
        response_text = self.generator.generate(decision, full_context)
        
        # Determine if final
        is_final = decision.action in ["SEND_ACCEPTANCE", "SEND_REJECTION"]
        price = decision.suggested_price or 0.0
        
        return response_text, price, is_final
