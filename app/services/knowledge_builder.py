from app.services.gemini_client import GeminiClient
import json


class KnowledgeBuilder:
    """Processes raw buyer form input into structured negotiation context."""

    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client

    def build_context(self, raw_form_input: str) -> dict:
        """Convert raw buyer requirements to structured context.
        
        Args:
            raw_form_input: Raw text from buyer's form (e.g., "Budget: ₹6500, Deadline: 3 days")
        
        Returns:
            Structured dict with budget, target_price, deadline, priority
        """
        prompt = f"""
        Convert the following buyer requirements into valid JSON with keys:
        - budget (int, extract numeric value)
        - target_price (int, 5% lower than budget)
        - deadline (str)
        - priority (str: cost/speed/quality)
        
        Input: {raw_form_input}
        Output only JSON:
        """
        raw_response = self.gemini_client.generate(prompt)
        # Mock parsing for scaffold (real impl would parse LLM JSON response)
        try:
            return json.loads(raw_response)
        except:
            # Fallback to example structure
            return {
                "budget": 6500,
                "target_price": 6000,
                "deadline": "3 days",
                "priority": "cost"
            }
