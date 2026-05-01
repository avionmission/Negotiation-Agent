class GeminiClient:
    """Mock Gemini API client for generating LLM responses."""

    def generate(self, prompt: str) -> str:
        """Generate a response from the LLM based on the prompt."""
        return f"[Mock LLM Response] Processed prompt: {prompt[:50]}..."
