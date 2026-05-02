from app.core.logging import get_logger
from app.integrations.gemini_client import GeminiClient, GeminiRequest, GeminiResponse

logger = get_logger("services.agent")


class AgentService:
    def __init__(self, gemini_client: GeminiClient) -> None:
        self.gemini = gemini_client

    def generate_initial_offer(
        self,
        buyer_name: str,
        budget: float,
        requirements: str | None,
        knowledge_base: str | None,
    ) -> str:
        prompt = self._build_initial_offer_prompt(
            buyer_name=buyer_name,
            budget=budget,
            requirements=requirements,
            knowledge_base=knowledge_base,
        )

        response = self.gemini.generate(GeminiRequest(prompt=prompt))
        return response.text

    def process_supplier_response(
        self,
        supplier_message: str,
        current_offer: float,
        budget: float,
        negotiation_round: int,
        max_rounds: int,
        conversation_history: list[str],
    ) -> tuple[str, float, bool]:
        prompt = self._build_negotiation_prompt(
            supplier_message=supplier_message,
            current_offer=current_offer,
            budget=budget,
            negotiation_round=negotiation_round,
            conversation_history=conversation_history,
        )

        response = self.gemini.generate(GeminiRequest(prompt=prompt))

        new_offer = self._parse_offer_response(response.text, current_offer)
        is_final = (
            negotiation_round >= max_rounds or "accept" in response.text.lower()[:50]
        )

        return response.text, new_offer, is_final

    def evaluate_acceptance(
        self,
        response_text: str,
        offer_price: float,
        budget: float,
    ) -> str:
        response_lower = response_text.lower()

        if (
            "accept" in response_lower
            or "agree" in response_lower
            or "deal" in response_lower
        ):
            return "ACCEPT"

        if offer_price <= budget * 1.1:
            return "ACCEPT"

        if "reject" in response_lower or "no" in response_lower[:10]:
            return "REJECT"

        return "CONTINUE"

    def generate_counter_offer(
        self,
        supplier_counter: float,
        budget: float,
        requirements: str | None,
        is_within_budget: bool,
    ) -> str:
        prompt = self._build_counter_offer_prompt(
            supplier_counter=supplier_counter,
            budget=budget,
            requirements=requirements,
            is_within_budget=is_within_budget,
        )

        response = self.gemini.generate(GeminiRequest(prompt=prompt))
        return response.text

    def generate_deal_summary(
        self,
        final_price: float,
        buyer_name: str,
        supplier_name: str,
        terms: str | None,
    ) -> str:
        prompt = f"""
Generate a formal deal summary for the following negotiation:

Buyer: {buyer_name}
Supplier: {supplier_name}
Final Price: ${final_price}
Terms: {terms or "Standard terms apply"}

Provide a structured summary with all key details.
"""

        response = self.gemini.generate(GeminiRequest(prompt=prompt))
        return response.text

    def _build_initial_offer_prompt(
        self,
        buyer_name: str,
        budget: float,
        requirements: str | None,
        knowledge_base: str | None,
    ) -> str:
        prompt = f"""You are an AI procurement agent representing {buyer_name}.

Your task is to generate an initial offer for a procurement negotiation.

Budget: ${budget}
Requirements: {requirements or "Not specified"}
Knowledge Base: {knowledge_base or "No additional context"}

Generate a professional initial offer message. Keep it concise, clear, and negotiation-oriented.
"""
        return prompt

    def _build_negotiation_prompt(
        self,
        supplier_message: str,
        current_offer: float,
        budget: float,
        negotiation_round: int,
        conversation_history: list[str],
    ) -> str:
        history = "\n".join(f"- {h}" for h in conversation_history[-5:])

        prompt = f"""You are an AI procurement agent negotiating on behalf of the buyer.

Current offer: ${current_offer}
Budget: ${budget}
Negotiation round: {negotiation_round}

Supplier's latest message: {supplier_message}

Recent conversation history:
{history}

Analyze the supplier's response and generate an appropriate counter-offer or acceptance message.
If the supplier's offer is within 10% of budget, consider accepting.
"""
        return prompt

    def _build_counter_offer_prompt(
        self,
        supplier_counter: float,
        budget: float,
        requirements: str | None,
        is_within_budget: bool,
    ) -> str:
        prompt = f"""Generate a counter-offer response.

Supplier's counter: ${supplier_counter}
Your budget: ${budget}
Requirements: {requirements or "Not specified"}

Is within budget: {"Yes" if is_within_budget else "No"}

Generate an appropriate response: accept if reasonable, counter if needed, or explain your position.
"""
        return prompt

    def _parse_offer_response(self, response_text: str, fallback: float) -> float:
        import re

        matches = re.findall(r"\$?(\d+(?:,\d{3})*(?:\.\d{2})?)", response_text)

        for match in reversed(matches):
            try:
                value = float(match.replace(",", ""))
                if value > 0:
                    return value
            except ValueError:
                continue

        return fallback


agent_service = AgentService(gemini_client=None)


def get_agent_service() -> AgentService:
    from app.integrations.gemini_client import gemini_client

    return AgentService(gemini_client)
