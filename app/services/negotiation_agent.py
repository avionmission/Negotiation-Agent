from app.services.gemini_client import GeminiClient
from app.utils.prompt_builder import build_prompt


class NegotiationAgent:
    """AI agent that generates replies during negotiations."""

    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client

    def generate_reply(self, system_prompt: str, negotiation, supplier, history) -> str:
        """Generate a reply based on negotiation context and history."""
        prompt = build_prompt(system_prompt, negotiation, supplier, history)
        return self.gemini_client.generate(prompt)
