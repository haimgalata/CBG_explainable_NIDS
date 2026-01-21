from pathlib import Path
import pandas as pd

from src.load_data import load_netflow_csv
from src.prompt_builder import extract_observable_features, build_explanation_prompt
from src.gpt_client import GPTClient


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "may_hamalka80-85.csv"


def explain_flows(rows: list[pd.Series]) -> list[str]:
    """
    Receives a list of NetFlow rows and returns GPT explanations.
    """
    gpt = GPTClient()
    explanations = []

    for idx, row in enumerate(rows, start=1):
        observable = extract_observable_features(row)
        prompt = build_explanation_prompt(observable)

        print(f"\n--- FLOW {idx} PROMPT ---\n")
        print(prompt)

        explanation = gpt.explain(prompt)
        explanations.append(explanation)

        print(f"\n--- FLOW {idx} GPT EXPLANATION ---\n")
        print(explanation)

    return explanations


def main():
    df = load_netflow_csv(CSV_PATH)

    rows_to_explain = [df.iloc[i] for i in range(10)]

    explain_flows(rows_to_explain)


if __name__ == "__main__":
    main()
