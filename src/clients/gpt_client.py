from openai import OpenAI
from src.config import OPENAI_API_KEY


class GPTClient:
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.3):
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set")

        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.temperature = temperature

    def explain(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": "You are a cybersecurity analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature
        )

        return response.output_text
