import re
import tiktoken


def extract_llm_likelihood(text: str):
    """
    Extract likelihood value from LLM output.
    Supports formats like:
    - Likelihood (0–1): 0.85
    - **Likelihood (0–1):** 0.85
    - Likelihood (0–1):
      0.85
    """

    if not text:
        return None

    pattern = r"Likelihood.*?:\s*\**\s*([01](?:\.\d+)?)"

    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

    if match:
        value = float(match.group(1))

        if 0 <= value <= 1:
            return value

    return None


def count_llm_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens in LLM output using tiktoken.
    """

    if not text:
        return 0

    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)

    return len(tokens)


# simple test
if __name__ == "__main__":
    print(extract_llm_likelihood("1. **1. HHK887 Malicious likelihood (0–1): 0.85"))
