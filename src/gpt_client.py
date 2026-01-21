from openai import OpenAI


class GPTClient:
    def __init__(self):
        self.client = OpenAI()

    def explain(self, prompt: str) -> str:
        """
        Sends a prompt to OpenAI and returns the explanation text.
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a cybersecurity analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content
