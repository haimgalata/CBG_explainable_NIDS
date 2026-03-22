"""
Unified pipeline: config-driven runs with incremental save and resume.
"""

import logging
from pathlib import Path

from src.load_data import load_netflow_csv
from src.layers.baseline import run_baseline_layer
from src.layers.augmented import run_augmented_layer
from src.layers.consensus import run_consensus_layer
from src.services.evaluation_writer import append_single_result
from src.core.run_state import (
    append_result_jsonl,
    load_checkpoint,
    load_results_from_jsonl,
    save_checkpoint,
    get_resumable_indices,
    clear_checkpoint,
    get_jsonl_path,
)

logger = logging.getLogger(__name__)


def _make_on_flow_complete(
    run_output_dir: Path,
    csv_path: Path,
    experiment_layer: str,
    mode: str,
    total: int,
    meta: dict,
):
    """Build callback for incremental save after each flow."""

    def on_flow_complete(result: dict, row, idx: int) -> None:
        append_result_jsonl(run_output_dir, result)
        append_single_result(result, row, experiment_layer, mode, csv_path)
        save_checkpoint(run_output_dir, idx, total, meta)
        logger.info("Saved flow %s/%s", idx, total)

    return on_flow_complete


def run_single_experiment(
    config: dict,
    csv_path: Path,
    run_output_dir: Path,
    experiment_output_dir: Path,
    run_id: str,
    resume: bool = True,
) -> list[dict]:
    """
    Run a single experiment with incremental save and optional resume.

    config: {
        "layer": "baseline" | "augmented" | "consensus",
        "consensus_mode": "baseline" | "augmented",  # for consensus only
        "mode": "real" | "synthetic" | "default",
        "start": int,
        "end": int,
    }
    """
    layer = config["layer"]
    mode = config.get("mode", "default")
    start = config.get("start", 0)
    end = config.get("end", start + 1)
    consensus_mode = config.get("consensus_mode", "baseline")

    df = load_netflow_csv(csv_path)
    all_rows = [df.iloc[i] for i in range(start, end)]
    total_rows = len(all_rows)

    if total_rows == 0:
        logger.warning("No rows to process (start=%s, end=%s)", start, end)
        return []

    # Experiment layer label for output paths
    if layer == "consensus":
        experiment_layer = f"consensus_{consensus_mode}"
    else:
        experiment_layer = layer

    rows_folder = f"rows_{start}_{end - 1}"
    experiment_output_dir = experiment_output_dir / experiment_layer / mode / rows_folder
    experiment_output_dir.mkdir(parents=True, exist_ok=True)
    csv_path_out = experiment_output_dir / f"evaluation_{run_id}.csv"

    # Resume logic
    if resume:
        start_idx, indices_to_run = get_resumable_indices(run_output_dir, total_rows)
        if not indices_to_run:
            logger.info("Run already complete (resume). Loading results from JSONL.")
            results = load_results_from_jsonl(run_output_dir)
            return results
        rows_to_process = [all_rows[i] for i in indices_to_run]
        flow_start_index = indices_to_run[0]
    else:
        clear_checkpoint(run_output_dir)
        jsonl_path = get_jsonl_path(run_output_dir)
        if jsonl_path.exists():
            jsonl_path.unlink()
            logger.info("Cleared previous results.jsonl (no-resume)")
        rows_to_process = all_rows
        flow_start_index = 0

    meta = {
        "layer": layer,
        "mode": mode,
        "consensus_mode": consensus_mode if layer == "consensus" else None,
        "start": start,
        "end": end,
        "run_id": run_id,
    }

    on_flow_complete = _make_on_flow_complete(
        run_output_dir, csv_path_out, experiment_layer, mode, total_rows, meta
    )

    # Run layer
    if layer == "baseline":
        results = run_baseline_layer(
            rows_to_process,
            run_output_dir,
            on_flow_complete=on_flow_complete,
            start_index=flow_start_index,
        )
    elif layer == "augmented":
        results = run_augmented_layer(
            rows_to_process,
            run_output_dir,
            reputation_mode=mode,
            on_flow_complete=on_flow_complete,
            start_index=flow_start_index,
        )
    elif layer == "consensus":
        results = run_consensus_layer(
            rows_to_process,
            run_output_dir,
            use_augmentation=(consensus_mode == "augmented"),
            reputation_mode=mode,
            on_flow_complete=on_flow_complete,
            start_index=flow_start_index,
        )
    else:
        raise ValueError(f"Unknown layer: {layer}")

    # Always load full results from JSONL (single source of truth)
    results = load_results_from_jsonl(run_output_dir)
    return results
