import argparse
import json
from pathlib import Path
from datetime import datetime

from src.load_data import load_netflow_csv
from src.layers.baseline import run_baseline_layer
from src.layers.augmented import run_augmented_layer
from src.layers.consensus import run_consensus_layer
from src.services.evaluation_writer import append_results

RUN_ID = datetime.now().strftime("%Y-%m-%d_%H-%M")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "may_hamalka80-85.csv"

BASE_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "runs"
EXPERIMENTS_DIR = PROJECT_ROOT / "outputs" / "experiments"


def main():
    parser = argparse.ArgumentParser(
        description="Run selected explanation layer"
    )

    parser.add_argument(
        "--layer",
        type=str,
        required=True,
        choices=["baseline", "augmented", "consensus"],
        help="Select which explanation layer to run"
    )

    parser.add_argument(
        "--consensus_mode",
        type=str,
        default="baseline",
        choices=["baseline", "augmented"],
        help="Consensus mode: baseline or augmented"
    )

    parser.add_argument(
        "--mode",
        type=str,
        default="default",
        choices=["real", "synthetic", "default"],
        help="Reputation mode for augmented layer"
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
    if args.layer == "consensus":

        if args.consensus_mode == "augmented":
            run_output_dir = BASE_OUTPUT_DIR / f"{RUN_ID}_consensus_augmented_{args.mode}"
        else:
            run_output_dir = BASE_OUTPUT_DIR / f"{RUN_ID}_consensus_baseline"

    elif args.layer == "augmented":
        run_output_dir = BASE_OUTPUT_DIR / f"{RUN_ID}_{args.layer}_{args.mode}"

    else:
        run_output_dir = BASE_OUTPUT_DIR / f"{RUN_ID}_{args.layer}"

    run_output_dir.mkdir(parents=True, exist_ok=True)

    # ---- Load data ----
    df = load_netflow_csv(CSV_PATH)
    rows_to_explain = [df.iloc[i] for i in range(args.start, args.end)]

    print(f"\nRunning layer: {args.layer}")

    if args.layer == "consensus":
        print(f"Consensus mode: {args.consensus_mode}")

    print(f"Reputation mode: {args.mode}")
    print(f"Flows: {args.start} → {args.end - 1}")
    print(f"Run ID: {RUN_ID}\n")

    # ---- Layer dispatch ----
    if args.layer == "baseline":
        results = run_baseline_layer(rows_to_explain, run_output_dir)

    elif args.layer == "augmented":
        results = run_augmented_layer(
            rows_to_explain,
            run_output_dir,
            reputation_mode=args.mode
        )

    elif args.layer == "consensus":
        results = run_consensus_layer(
            rows_to_explain,
            run_output_dir,
            use_augmentation=(args.consensus_mode == "augmented"),
            reputation_mode=args.mode
        )

    else:
        raise ValueError("Invalid layer selected")

    # ---- Save results JSON ----
    output_file = run_output_dir / "results.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # ---- Determine experiment layer label ----
    if args.layer == "consensus":
        if args.consensus_mode == "baseline":
            experiment_layer = "consensus_baseline"
        else:
            experiment_layer = "consensus_augmented"
    else:
        experiment_layer = args.layer

    # ---- Create experiments path ----
    rows_folder = f"rows_{args.start}_{args.end - 1}"

    experiment_output_dir = (
            EXPERIMENTS_DIR
            / experiment_layer
            / args.mode
            / rows_folder
    )

    experiment_output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = experiment_output_dir / f"evaluation_{RUN_ID}.csv"

    # ---- Save evaluation CSV ----
    append_results(
        results,
        rows_to_explain,
        experiment_layer,
        args.mode,
        csv_path
    )

    print(f"\nResults saved to: {output_file}")
    print(f"Evaluation CSV: {csv_path}")
    print("Done.\n")


if __name__ == "__main__":
    main()