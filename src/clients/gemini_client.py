from google import genai
from src.config import GEMINI_API_KEY


class GeminiClient:
    def __init__(self, model: str = "gemini-flash-latest"):
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set")

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = model

    def explain(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text
