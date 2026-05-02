import json
import re
from app.integrations.gemini_client import GeminiClient, GeminiRequest
from .models import ParsedMessage, Intent

class MessageInterpreter:
    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini

    def interpret(self, message: str) -> ParsedMessage:
        prompt = f"""
        Analyze the following supplier message in a procurement negotiation.
        Extract the INTENT and the OFFERED PRICE (if any).

        Message: "{message}"

        Return ONLY a JSON object with this format:
        {{
            "intent": "COUNTER" | "ACCEPT" | "REJECT" | "QUERY" | "GREETING",
            "offered_price": float or null,
            "reasoning": "short explanation"
        }}
        """
        
        response = self.gemini.generate(GeminiRequest(prompt=prompt))
        
        try:
            # Simple JSON extraction from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return ParsedMessage(**data)
        except Exception:
            pass
            
        # FALLBACK: If Gemini fails, use Regex to find a price
        price_match = re.search(r'\$(\d+(?:\.\d+)?)', message)
        if price_match:
            return ParsedMessage(
                intent=Intent.COUNTER, 
                offered_price=float(price_match.group(1)),
                reasoning="Extracted price via regex fallback."
            )

        # Final Fallback
        return ParsedMessage(intent=Intent.QUERY, reasoning="Could not parse supplier response clearly.")
