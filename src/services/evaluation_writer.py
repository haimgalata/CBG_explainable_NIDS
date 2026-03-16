import csv
import re
from pathlib import Path
from src.utils.llm_utils import extract_llm_likelihood


HEADER = [
    "ID",
    "Layer",
    "Mode",
    "Score_Autoencoder",
    "LLM_Prediction",
    "Label",
    "IP_Reputation_Found",
    "Latency_Total",
    "Tokens_Total",
    "Length_Total"
]


def normalize_result(r: dict, layer: str, mode: str) -> dict:

    flow_id = r["observable_features"]["ID"]

    score_autoencoder = r["observable_features"]["score_Autoencoder"]

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

    # -------------------------
    # Latency
    # -------------------------

    latency = r.get("total_llm_latency_seconds")

    if latency is None:

        latency = (
            r.get("llm_latency_seconds")
            or (
                r.get("latency_attack", 0)
                + r.get("latency_benign", 0)
                + r.get("latency_judge", 0)
            )
        )

    # -------------------------
    # Tokens
    # -------------------------

    tokens = r.get("total_llm_response_tokens")

    if tokens is None:

        tokens = (
            r.get("llm_response_tokens")
            or r.get("Decision_llm_response_tokens")
            or 0
        )

    # -------------------------
    # Length
    # -------------------------

    length = r.get("total_llm_response_length")

    if length is None:

        length = (
            r.get("llm_response_length")
            or r.get("Decision_llm_response_length")
            or 0
        )

    return {
        "ID": flow_id,
        "Layer": layer,
        "Mode": mode,
        "Score_Autoencoder": score_autoencoder,
        "LLM_Prediction": likelihood,
        "IP_Reputation_Found": r.get("ip_reputation_found", 0),
        "Latency_Total": latency,
        "Tokens_Total": tokens,
        "Length_Total": length
    }


def ensure_csv_exists(csv_path: Path):

    if not csv_path.exists() or csv_path.stat().st_size == 0:

        csv_path.parent.mkdir(parents=True, exist_ok=True)

        with open(csv_path, "w", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)
            writer.writerow(HEADER)


def append_results(results, rows, layer, mode, csv_path):

    ensure_csv_exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        for r, row_df in zip(results, rows):

            true_label = int(row_df["Label"])

            row = normalize_result(r, layer, mode)

            writer.writerow([
                row["ID"],
                row["Layer"],
                row["Mode"],
                row["Score_Autoencoder"],
                row["LLM_Prediction"],
                true_label,
                row["IP_Reputation_Found"],
                row["Latency_Total"],
                row["Tokens_Total"],
                row["Length_Total"]
            ])