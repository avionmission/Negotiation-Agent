from typing import Any

import google.generativeai as genai
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("integrations.gemini")


class GeminiRequest(BaseModel):
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 2048


class GeminiResponse(BaseModel):
    text: str
    model: str
    finish_reason: str | None = None


class GeminiClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: genai.GenerativeModel | None = None

        if self.settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=self.settings.GEMINI_API_KEY)
                self._client = genai.GenerativeModel(self.settings.GEMINI_MODEL)
                logger.info(
                    f"Gemini client initialized with model: {self.settings.GEMINI_MODEL}"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Gemini client: {e}. Using mock fallback."
                )

    def generate(self, request: GeminiRequest) -> GeminiResponse:
        if not self._client:
            return self._mock_response(request.prompt)

        try:
            response = self._client.generate_content(
                request.prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=request.temperature,
                    max_output_tokens=request.max_tokens,
                ),
            )

            return GeminiResponse(
                text=response.text,
                model=self.settings.GEMINI_MODEL,
                finish_reason=response.finish_reason.name
                if response.finish_reason
                else None,
            )
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._mock_response(request.prompt)

    def _mock_response(self, prompt: str) -> GeminiResponse:
        prompt_lower = prompt.lower()

        if "initial offer" in prompt_lower or "first offer" in prompt_lower:
            text = "Based on your requirements and budget, I'm pleased to offer a starting price that aligns with market rates. Let me know if this meets your expectations."
        elif (
            "counter" in prompt_lower
            or "respond" in prompt_lower
            or "supplier" in prompt_lower
        ):
            text = "Thank you for your response. I've considered your proposal and would like to present a revised offer that balances both our interests. What's your final decision?"
        elif "accept" in prompt_lower or "deal" in prompt_lower:
            text = "Excellent! I'm glad we reached an agreement. I'll prepare the formal deal summary for your approval."
        else:
            text = "I understand your position. Let me analyze this and provide a structured response to continue our negotiation."

        return GeminiResponse(
            text=text,
            model="mock-fallback",
            finish_reason="STOP",
        )


gemini_client = GeminiClient()
