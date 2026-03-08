import csv
import re
from pathlib import Path


EVAL_FILE = Path("outputs/evaluation.csv")

HEADER = [
    "ID",
    "Actual_Label",
    "LLM_Prediction",
    "Label",
    "IP_Reputation_Found",
    "Latency",
    "Tokens",
    "Length"
]


def extract_llm_likelihood(text: str) -> float | None:
    """
    Extract likelihood value from LLM explanation text.
    Works when the number appears on the next line.
    """

    match = re.search(
        r'Likelihood.*?\n\s*[*]*\s*([0-9]*\.?[0-9]+)',
        text,
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    return None


def normalize_result(r: dict) -> dict:
    """
    Convert result from any layer (baseline / augmented / consensus)
    into a standard structure for CSV.
    """

    # -------- Flow ID --------
    flow_id = r["observable_features"]["ID"]

    # -------- Autoencoder score --------
    actual_label = r["observable_features"]["score_Autoencoder"]

    # -------- Likelihood --------
    likelihood = r.get("llm_likelihood")

    if likelihood is None:
        likelihood = r.get("Decision_llm_likelihood")

    if likelihood is None:
        text = (
            r.get("explanation")
            or r.get("final_decision")
            or r.get("expert_attack")
            or ""
        )
        likelihood = extract_llm_likelihood(text)

    # -------- Binary label --------
    label = 1 if likelihood and likelihood >= 0.5 else 0

    # -------- Latency --------
    latency = r.get("llm_latency_seconds")

    if latency is None:
        latency = (
            r.get("latency_attack", 0)
            + r.get("latency_benign", 0)
            + r.get("latency_judge", 0)
        )

    # -------- Tokens --------
    tokens = (
        r.get("llm_response_tokens")
        or r.get("Decision_llm_response_tokens")
        or 0
    )

    # -------- Explanation length --------
    length = (
        r.get("llm_response_length")
        or r.get("Decision_llm_response_length")
        or 0
    )

    return {
        "id": flow_id,
        "actual_label": actual_label,
        "llm_prediction": likelihood,
        "label": label,
        "ip_reputation_found": r.get("ip_reputation_found", 0),
        "latency": latency,
        "tokens": tokens,
        "length": length
    }


def ensure_csv_exists():
    """
    Create evaluation CSV with header if it does not exist.
    """

    if not EVAL_FILE.exists() or EVAL_FILE.stat().st_size == 0:

        EVAL_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(EVAL_FILE, "w", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)

            writer.writerow(HEADER)


def append_results(results):
    """
    Append results from LLM run to evaluation CSV.
    """

    ensure_csv_exists()

    with open(EVAL_FILE, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        for r in results:

            row = normalize_result(r)

            writer.writerow([
                row["id"],
                row["actual_label"],
                row["llm_prediction"],
                row["label"],
                row["ip_reputation_found"],
                row["latency"],
                row["tokens"],
                row["length"]
            ])