"""
Incremental saving and resume support for experiment runs.

- JSONL: append one result per flow (survives crashes)
- Checkpoint: last completed flow index (enables resume)
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CHECKPOINT_FILENAME = "checkpoint.json"
RESULTS_JSONL_FILENAME = "results.jsonl"


def get_checkpoint_path(run_dir: Path) -> Path:
    return run_dir / CHECKPOINT_FILENAME


def get_jsonl_path(run_dir: Path) -> Path:
    return run_dir / RESULTS_JSONL_FILENAME


def load_checkpoint(run_dir: Path) -> dict | None:
    """Load checkpoint if it exists. Returns None if no checkpoint."""
    path = get_checkpoint_path(run_dir)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info("Loaded checkpoint: %s", data)
        return data
    except (json.JSONDecodeError, IOError) as e:
        logger.warning("Failed to load checkpoint: %s", e)
        return None


def save_checkpoint(run_dir: Path, last_completed_index: int, total: int, meta: dict) -> None:
    """Save checkpoint after each flow."""
    run_dir.mkdir(parents=True, exist_ok=True)
    path = get_checkpoint_path(run_dir)
    data = {
        "last_completed_index": last_completed_index,
        "total": total,
        "meta": meta,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logger.debug("Saved checkpoint: index=%s/%s", last_completed_index, total)


def append_result_jsonl(run_dir: Path, result: dict) -> None:
    """Append a single result to JSONL file (one line per flow)."""
    run_dir.mkdir(parents=True, exist_ok=True)
    path = get_jsonl_path(run_dir)
    with open(path, "a", encoding="utf-8") as f:
        line = json.dumps(result, ensure_ascii=False) + "\n"
        f.write(line)
    logger.debug("Appended result for flow_index=%s", result.get("flow_index"))


def load_results_from_jsonl(run_dir: Path) -> list[dict]:
    """Load all results from JSONL (for final aggregation)."""
    path = get_jsonl_path(run_dir)
    if not path.exists():
        return []
    results = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as e:
                logger.warning("Skipping invalid JSONL line: %s", e)
    return results


def get_resumable_indices(run_dir: Path, total_rows: int) -> tuple[int, list[int]]:
    """
    If checkpoint exists, return (start_index, indices_to_run).
    Otherwise return (0, list(range(total_rows))).

    start_index: index in the *original* rows array to resume from (1-based flow_index).
    indices_to_run: 0-based indices into rows to process.
    """
    cp = load_checkpoint(run_dir)
    if cp is None:
        return 0, list(range(total_rows))

    last = cp["last_completed_index"]  # 1-based flow_index
    total = cp["total"]
    if total != total_rows:
        logger.warning(
            "Checkpoint total (%s) != current rows (%s). Starting fresh.",
            total,
            total_rows,
        )
        return 0, list(range(total_rows))

    start = last  # next to run is last+1
    if start >= total:
        logger.info("Checkpoint indicates run complete. Nothing to resume.")
        return total, []

    indices = list(range(start, total))
    logger.info("Resuming from flow_index=%s (%s flows remaining)", start + 1, len(indices))
    return start, indices


def clear_checkpoint(run_dir: Path) -> None:
    """Remove checkpoint (e.g. when starting a fresh run with --no-resume)."""
    path = get_checkpoint_path(run_dir)
    if path.exists():
        path.unlink()
        logger.info("Cleared checkpoint")


def is_complete(run_dir: Path, total_rows: int) -> bool:
    """True if checkpoint says all flows are done."""
    cp = load_checkpoint(run_dir)
    if cp is None:
        return False
    return cp.get("last_completed_index", -1) >= total_rows - 1
