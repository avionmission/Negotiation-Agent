from .models import ParsedMessage, AgentDecision, AgentAction, Intent

class NegotiationStrategist:
    def decide(self, parsed: ParsedMessage, budget: float, base_price: float, current_round: int, max_rounds: int) -> AgentDecision:
        # STEP 4 & 5: Evaluate and Decide using pure logic
        
        # 1. Handle explicit acceptance
        if parsed.intent == Intent.ACCEPT:
            return AgentDecision(
                action=AgentAction.SEND_ACCEPTANCE,
                suggested_price=parsed.offered_price,
                strategy_note="Supplier accepted the proposal."
            )

        # 2. Handle Price Evaluation
        if parsed.offered_price and parsed.offered_price > 0:
            # Stricter acceptance: only if it's less than or equal to budget
            if parsed.offered_price <= budget:
                return AgentDecision(
                    action=AgentAction.SEND_ACCEPTANCE,
                    suggested_price=parsed.offered_price,
                    strategy_note="Offer is within budget."
                )
            
            # If we are at the last round and price is still high, reject
            if current_round >= max_rounds:
                return AgentDecision(
                    action=AgentAction.SEND_REJECTION,
                    strategy_note="Max negotiation rounds reached and price is too high."
                )

            # Otherwise, counter at a price between current offer and their offer
            # For simplicity: Counter at budget
            return AgentDecision(
                action=AgentAction.SEND_COUNTER,
                suggested_price=budget,
                strategy_note=f"Countering at budget. Round {current_round}/{max_rounds}"
            )

        # 3. Default to clarification
        return AgentDecision(
            action=AgentAction.ASK_CLARIFICATION,
            strategy_note="No clear price found in supplier message."
        )
