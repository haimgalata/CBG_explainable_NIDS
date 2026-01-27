from pathlib import Path
import pandas as pd
import json

from datetime import datetime
from src.load_data import load_netflow_csv
from src.prompt_builder import extract_observable_features, build_explanation_prompt
from src.gpt_client import GPTClient
from src.gemini_client import GeminiClient
from src.md_writer import write_flow_md

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "may_hamalka80-85.csv"

OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "explanations.json"

def load_existing_explanations(path: Path) -> list:
    if path.exists() and path.stat().st_size > 0:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def explain_flows(rows: list[pd.Series]) -> list[dict]:
    gpt = GeminiClient()

    results = load_existing_explanations(OUTPUT_FILE)

    for idx, row in enumerate(rows, start=len(results) + 1):
        observable = extract_observable_features(row)
        prompt = build_explanation_prompt(observable)

        print(f"\n--- FLOW {idx} PROMPT ---\n")
        print(prompt)

        explanation = gpt.explain(prompt)

        print(f"\n--- FLOW {idx} MODEL EXPLANATION ---\n")
        print(explanation)

        write_flow_md(
            flow_id=observable["ID"],
            features=observable,
            explanation=explanation
        )

        result = {
            "flow_index": idx,
            "timestamp": datetime.now().isoformat(),
            "model": "gemini-1.5-flash",
            "observable_features": observable,
            "explanation": explanation
        }

        results.append(result)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Explanations saved to {OUTPUT_FILE}")

    return results


def main():
    df = load_netflow_csv(CSV_PATH)

    rows_to_explain = [df.iloc[i] for i in range(10)]

    explain_flows(rows_to_explain)


if __name__ == "__main__":
    main()
