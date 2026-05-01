def build_prompt(system_prompt: str, negotiation, supplier, history) -> str:
    """Build a formatted prompt for the LLM based on negotiation context."""
    history_text = "\n".join([f"{m.sender}: {m.content}" for m in history]) if history else "No history yet."
    return f"""
{system_prompt}

Negotiation: {negotiation.title}
Supplier: {supplier.name}
History:
{history_text}

Generate a response:
""".strip()
