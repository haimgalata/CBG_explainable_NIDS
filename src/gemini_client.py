from google import genai


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(
            api_key="***************"
        )

        self.model = "gemini-flash-latest"

    def explain(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text
