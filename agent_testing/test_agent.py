import sys
import os

# Add the project root to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.agent.orchestrator import AgentOrchestrator
from app.integrations.gemini_client import GeminiClient

def run_test():
    # 1. Initialize Gemini Client (will use Mock if no API key)
    client = GeminiClient()
    
    # 2. Initialize the Orchestrator (The 8-step brain)
    agent = AgentOrchestrator(gemini=client)

    print("="*60)
    print("      PROFESSIONAL MODULAR AGENT: 8-STEP PIPELINE TEST")
    print("="*60)
    
    # DUMMY DATA (Matching the UI screenshot)
    agent_data = {
        "name": "GPU Server Procurement",
        "domain": "Technology",
        "subdomain": "Hardware",
        "description": "Urgent requirement for 10x RTX 4090 GPUs for a deep learning project. Delivery needed within 7 days.",
        "base_price": 4500.0,
        "budget": 5000.0,
        "max_negotiation_rounds": 3
    }
    
    # SIMULATE A CONVERSATION
    messages = [
        "Hi, we can provide the GPUs. Our price is $6000 per unit.",
        "That's too high. We can only do $5200.",
        "Okay, fine. We accept your offer of $5000."
    ]

    for i, msg in enumerate(messages):
        print(f"\n--- ROUND {i+1} ---")
        print(f"SUPPLIER: {msg}")
        
        # RUN THE PIPELINE (Using the new agent_data object)
        response, price, is_final = agent.process_step(
            message=msg,
            agent_data=agent_data,
            current_round=i+1
        )
        
        print(f"AGENT RESPONSE: {response}")
        print(f"DECIDED PRICE: ${price}")
        print(f"IS FINAL DEAL?: {is_final}")
        
        if is_final:
            print("\n>>> NEGOTIATION CONCLUDED.")
            break

if __name__ == "__main__":
    run_test()
