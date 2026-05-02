from app.integrations.gemini_client import GeminiClient, GeminiRequest
from .models import AgentDecision, AgentAction

class ResponseGenerator:
    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini

    def generate(self, decision: AgentDecision, context: str) -> str:
        # STEP 6: Generate professional response based on decision
        
        # Map internal enum values to the professional prompt's terminology
        action_map = {
            "SEND_COUNTER": "COUNTER",
            "SEND_ACCEPTANCE": "ACCEPT",
            "SEND_REJECTION": "REJECT",
            "ASK_CLARIFICATION": "QUERY"
        }
        display_action = action_map.get(decision.action.value if hasattr(decision.action, 'value') else decision.action, "REJECT")

        prompt = f"""
        You are an AI negotiation agent representing a buyer in a B2B procurement scenario.
        Your role is to communicate professionally with a supplier and execute negotiation decisions.

        ## ⚙️ BEHAVIOR RULES
        * You MUST strictly follow the provided action and offer.
        * Do NOT make independent pricing decisions.
        * Sound like a professional procurement manager: confident, polite, and concise (2-5 lines).
        * Justify offers using market conditions, project constraints, or timeline urgency.

        ## 📥 CURRENT DECISION
        - Action: {display_action}
        - Target Price: {f'${decision.suggested_price}' if decision.suggested_price else "N/A"}
        - Reasoning: {decision.strategy_note}
        
        ## 📋 CONTEXT
        {context}

        Generate the response message now. Do not include any internal reasoning or meta-text in your output.
        """
        
        response = self.gemini.generate(GeminiRequest(prompt=prompt))
        return response.text
