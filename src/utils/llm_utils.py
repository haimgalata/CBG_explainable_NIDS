import logging
import re
import tiktoken
import time

logger = logging.getLogger(__name__)


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
    except (ValueError, TypeError) as e:
        logger.debug("Could not parse confidence: %s", e)

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
    Retry wrapper for LLM calls (handles rate limits like 429, 503, timeouts).
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            return call_function()
        except Exception as e:
            last_error = e
            error_str = str(e)
            is_retryable = (
                "429" in error_str
                or "rate limit" in error_str.lower()
                or "503" in error_str
                or "timeout" in error_str.lower()
            )
            if is_retryable and attempt < max_retries - 1:
                wait_time = min(2 ** attempt, 60)
                logger.warning(
                    "LLM call failed (attempt %s/%s): %s. Retrying in %ss...",
                    attempt + 1,
                    max_retries,
                    error_str[:100],
                    wait_time,
                )
                time.sleep(wait_time)
            else:
                logger.error("LLM call failed: %s", e)
                raise

    logger.error("Max retries reached. Last error: %s", last_error)
    return None

# simple test
if __name__ == "__main__":
    print(extract_llm_confidence(". confidence (0–1): \n\n0.85"))
