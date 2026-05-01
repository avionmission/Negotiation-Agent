from app.services.gemini_client import GeminiClient
from app.utils.prompt_builder import build_prompt


class NegotiationAgent:
    """AI agent that handles the negotiation loop: Interpret → Strategy → Respond."""

    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client

    def interpret_message(self, message: str) -> dict:
        """Extract structured data (price, terms) from supplier message."""
        prompt = f"""
        Extract structured data from this supplier message as JSON:
        Message: {message}
        Output JSON with keys: price (int or null), terms (str or null)
        """
        response = self.gemini_client.generate(prompt)
        # Mock parsing for scaffold
        if "₹7000" in message or "7000" in message:
            return {"price": 7000, "terms": None}
        return {"price": None, "terms": None}

    def update_memory(self, negotiation, price: int | None):
        """Update negotiation state with new offer info."""
        negotiation.round_number += 1
        if price:
            negotiation.last_offer = price

    def decide_strategy(self, negotiation, supplier_offer: int | None) -> str:
        """Decide action based on budget, target price, and history."""
        if not supplier_offer:
            return "ask_for_price"
        
        if supplier_offer <= negotiation.target_price:
            return "accept"
        elif supplier_offer <= negotiation.buyer_budget:
            return "counter"
        else:
            return "reject"

    def generate_response(self, strategy: str, negotiation, supplier, history) -> str:
        """Generate response based on decided strategy."""
        system_prompt = negotiation.system_prompt or "You are a procurement negotiator."
        prompt = build_prompt(system_prompt, negotiation, supplier, history)
        return self.gemini_client.generate(prompt)
