"""
Single entry point for explainable NIDS experiments.

All configuration comes from experiments.json. Run with:
  python -m src.run_explanations
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

from src.core.pipeline import run_single_experiment

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "src" / "configs" / "experiments.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _resolve_path(path_str: str, base: Path) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = base / p
    return p.resolve()


def main():
    parser = argparse.ArgumentParser(
        description="Run explainable NIDS experiments (config-driven)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to experiments JSON config",
    )
    parser.add_argument(
        "--only",
        type=str,
        default=None,
        help="Run only the experiment with this name",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start fresh, do not resume from checkpoint",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and print what would run, without executing",
    )
    args = parser.parse_args()

    config_path = args.config
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path

    if not config_path.exists():
        logger.error("Config file not found: %s", config_path)
        return 1

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    input_csv = config.get("input_csv", "data/raw/may_hamalka80-85.csv")
    output_dir = config.get("output_dir", "outputs")
    csv_path = _resolve_path(input_csv, PROJECT_ROOT)
    base_output = _resolve_path(output_dir, PROJECT_ROOT)

    if not csv_path.exists():
        logger.error("Input CSV not found: %s", csv_path)
        return 1

    runs = config.get("runs", [])
    if not runs:
        logger.warning("No runs in config")
        return 0

    # Filter by --only
    if args.only:
        runs = [r for r in runs if r.get("name") == args.only]
        if not runs:
            logger.error("No run named '%s' in config", args.only)
            return 1

    # Filter enabled
    runs = [r for r in runs if r.get("enabled", True)]

    if not runs:
        logger.warning("No enabled runs to execute")
        return 0

    if args.dry_run:
        logger.info("Dry run - would execute %s experiments:", len(runs))
        for r in runs:
            logger.info("  - %s: %s [%s:%s]", r.get("name"), r.get("layer"), r.get("start"), r.get("end"))
        return 0

    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M")
    resume = not args.no_resume

    runs_dir = base_output / "runs"
    experiments_dir = base_output / "experiments"

    for exp in runs:
        name = exp.get("name", "unnamed")
        layer = exp.get("layer", "baseline")
        mode = exp.get("mode", "default")
        consensus_mode = exp.get("consensus_mode", "baseline")

        if layer == "consensus" and consensus_mode == "augmented":
            run_output_dir = runs_dir / f"{run_id}_consensus_augmented_{mode}"
        elif layer == "consensus":
            run_output_dir = runs_dir / f"{run_id}_consensus_baseline"
        elif layer == "augmented":
            run_output_dir = runs_dir / f"{run_id}_{layer}_{mode}"
        else:
            run_output_dir = runs_dir / f"{run_id}_{layer}"

        run_output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Running: %s", name)
        try:
            results = run_single_experiment(
                config=exp,
                csv_path=csv_path,
                run_output_dir=run_output_dir,
                experiment_output_dir=experiments_dir,
                run_id=run_id,
                resume=resume,
            )
            # Write final results.json (aggregated from JSONL)
            with open(run_output_dir / "results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info("Completed %s: %s flows", name, len(results))
        except Exception as e:
            logger.exception("Error running %s: %s", name, e)
            # Continue with next run
            continue

    logger.info("All runs completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
