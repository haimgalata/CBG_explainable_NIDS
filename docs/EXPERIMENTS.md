# Experiment Design & Synthetic CTI

## Config-driven runs

All experiments are defined in `src/configs/experiments.json`:

```json
{
  "input_csv": "data/raw/may_hamalka80-85.csv",
  "output_dir": "outputs",
  "runs": [
    {
      "name": "baseline_0_5",
      "enabled": true,
      "layer": "baseline",
      "mode": "default",
      "start": 0,
      "end": 5
    }
  ]
}
```

- **layer**: `baseline` | `augmented` | `consensus`
- **consensus_mode** (consensus only): `baseline` | `augmented`
- **mode**: `real` | `synthetic` | `default` (CTI mode for augmented/consensus)
- **start**, **end**: Row indices (end exclusive)

## Synthetic CTI improvements

Current synthetic mode: binary (attack → random high scores, benign → zeros).

Suggested extensions in `synthetic_reputation.py`:

| Mode | Description | Use case |
|------|-------------|----------|
| `full_cti` | All 3 services return signals | Ideal CTI availability |
| `partial_cti` | 1–2 services return signals, others 0 | Realistic incomplete intel |
| `no_cti` | All zeros even for attacks | Simulate missing intel / FN |
| `severity` | Low/medium/high attack severity ranges | Calibrate sensitivity |

Example `partial_cti` logic:

```python
# In generate_random_attack_profile, add coverage param:
# coverage="full" | "partial" | "none"
# partial: randomly zero out 1-2 services
# none: return all zeros
```

## Experiment design suggestions

1. **Stratified sampling**: Use `start`/`end` to sample balanced attack/benign subsets (e.g. 50/50).
2. **Cross-validation**: Run multiple `(start, end)` slices, aggregate metrics.
3. **A/B comparison**: Same `(start, end)` across baseline, augmented, consensus for fair comparison.
4. **Row ranges**: Keep `rows_X_Y` consistent across runs for evaluation script compatibility.

## Resume & incremental save

- Each run writes `results.jsonl` (one line per flow) and `checkpoint.json`.
- On crash, re-run the same command → resumes from last completed flow.
- Use `--no-resume` to start fresh (clears checkpoint and JSONL).

## Evaluation

```bash
# Auto-discover latest evaluation CSVs and plot
python -m src.services.evaluation_metrics

# Explicit CSVs
python -m src.services.evaluation_metrics --csv path/to/eval1.csv path/to/eval2.csv --output compare.png
```

---

## Execution

All runs go through:

```bash
python -m src.run_explanations
```

See the main [README](../README.md) for setup and usage.
