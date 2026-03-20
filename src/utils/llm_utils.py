import re
import tiktoken
import time


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


def extract_llm_confidence(response: str) -> float | None:
    try:
        match = re.search(
            r"Confidence.*?:\s*([0-1](?:\.\d+)?)",
            response,
            re.IGNORECASE
        )
        if match:
            return float(match.group(1))
    except:
        pass

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


def call_llm_with_retry(call_function, max_retries=5):
    """
    Retry wrapper for LLM calls (handles rate limits like 429).
    """

    for attempt in range(max_retries):
        try:
            return call_function()

        except Exception as e:
            error_str = str(e)

            if "429" in error_str or "rate limit" in error_str.lower():
                wait_time = 2 ** attempt
                print(f"[Retry {attempt+1}] Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[Error] {e}")
                raise e

    print("[Failed] Max retries reached.")
    return None

# simple test
if __name__ == "__main__":
    print(extract_llm_confidence(". confidence (0–1): \n\n0.85"))
