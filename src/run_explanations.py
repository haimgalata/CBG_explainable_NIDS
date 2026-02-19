import argparse
import json
from pathlib import Path
from datetime import datetime

from src.load_data import load_netflow_csv
from src.layers.baseline import run_basic_layer
from src.layers.augmented import run_enriched_layer


RUN_ID = datetime.now().strftime("%Y-%m-%d_%H-%M")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "may_hamalka80-85.csv"
BASE_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "runs"


def main():
    parser = argparse.ArgumentParser(
        description="Run selected explanation layer"
    )

    parser.add_argument(
        "--layer",
        type=str,
        required=True,
        choices=["basic", "enriched"],
        help="Select which explanation layer to run"
    )

    parser.add_argument(
        "--start",
        type=int,
        default=397,
        help="Start index in dataset"
    )

    parser.add_argument(
        "--end",
        type=int,
        default=398,
        help="End index in dataset (exclusive)"
    )

    args = parser.parse_args()

    # ---- Create run directory BEFORE running layer ----
    run_output_dir = BASE_OUTPUT_DIR / f"{RUN_ID}_{args.layer}"
    run_output_dir.mkdir(parents=True, exist_ok=True)

    # ---- Load data ----
    df = load_netflow_csv(CSV_PATH)
    rows_to_explain = [df.iloc[i] for i in range(args.start, args.end)]

    print(f"\nRunning layer: {args.layer}")
    print(f"Flows: {args.start} → {args.end - 1}")
    print(f"Run ID: {RUN_ID}\n")

    # ---- Layer dispatch ----
    if args.layer == "basic":
        results = run_basic_layer(rows_to_explain, run_output_dir)

    elif args.layer == "enriched":
        results = run_enriched_layer(rows_to_explain, run_output_dir)

    else:
        raise ValueError("Invalid layer selected")

    # ---- Save results ----
    output_file = run_output_dir / "results.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_file}")
    print("Done.\n")


if __name__ == "__main__":
    main()
