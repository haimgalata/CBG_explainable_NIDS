# CBG Explainable NIDS

Explainable Network Intrusion Detection using LLM-based reasoning. The pipeline runs in three layers: **Baseline** → **Augmented** → **Consensus**.

---

## Quick Start

```bash
# 1. Activate environment
.venv\Scripts\activate

# 2. Run experiments (all enabled in config)
python -m src.run_explanations
```

---

## Setup

### 1. Python environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. API keys

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
# OR
GEMINI_API_KEY=...
```

At least one LLM API key is required. For augmented/consensus layers with real CTI:

```
IPQS_API_KEY=...
VT_API_KEY=...
ABUSE_IPDB_API_KEY=...
```

### 3. Input data

Place your NetFlow CSV at:

```
data/raw/may_hamalka80-85.csv
```

Required columns include `Label`, `IP_DST_ADDR`, and features used by the pipeline. See `src/prompt_builder.py` for `ALLOWED_FEATURES`.

---

## Configuration

All experiments are defined in `src/configs/experiments.json`.

### Config structure

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

### Run fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier for the run |
| `enabled` | No | `true` = run, `false` = skip (default: `true`) |
| `layer` | Yes | `baseline` \| `augmented` \| `consensus` |
| `mode` | No | `default` \| `real` \| `synthetic` (default: `default`) |
| `consensus_mode` | For consensus | `baseline` \| `augmented` |
| `start` | No | First row index (default: 0) |
| `end` | No | Last row index, exclusive (default: start + 1) |

### Layers

- **baseline** – NetFlow features only, single LLM call
- **augmented** – NetFlow + CTI (IP reputation) + autoencoder score
- **consensus** – Two experts (malicious/benign) + judge; optional CTI via `consensus_mode`

---

## Running Experiments

**Single entry point:**
```bash
python -m src.run_explanations
```

### Common commands

| Goal | Command |
|------|---------|
| Run all enabled experiments | `python -m src.run_explanations` |
| Run one experiment by name | `python -m src.run_explanations --only baseline_0_5` |
| Start fresh (ignore checkpoint) | `python -m src.run_explanations --no-resume` |
| Validate config without running | `python -m src.run_explanations --dry-run` |
| Use a different config file | `python -m src.run_explanations --config path/to/experiments.json` |

### CLI flags

| Flag | Description |
|------|-------------|
| `--only NAME` | Run only the experiment with this `name` |
| `--no-resume` | Clear checkpoint and JSONL; start from scratch |
| `--dry-run` | Print what would run, then exit |
| `--config PATH` | Path to experiments JSON (default: `src/configs/experiments.json`) |

---

## Outputs

Each run creates a directory under `outputs/runs/`:

```
outputs/runs/<RUN_ID>_<layer>/
├── results.json      # Full results (all flows)
├── results.jsonl     # One JSON object per line, per flow (incremental)
├── checkpoint.json   # Resume state (last completed flow index)
└── md/               # Per-flow markdown explanations
    └── flow_<ID>.md
```

### File roles

| File | Purpose |
|------|---------|
| **results.jsonl** | Written incrementally after each flow. Survives crashes. |
| **results.json** | Final aggregated results. Built from JSONL at the end. |
| **checkpoint.json** | Stores `last_completed_index`. Used for resume. |
| **md/** | Human-readable explanations per flow. |

### Evaluation CSVs

Evaluation metrics are written to:

```
outputs/experiments/<layer>/<mode>/rows_<start>_<end>/evaluation_<RUN_ID>.csv
```

---

## Resume Behavior

- If a run is interrupted, run the same command again.
- The pipeline loads `checkpoint.json`, skips completed flows, and continues.
- Use `--no-resume` to ignore the checkpoint and overwrite (clears `results.jsonl` and `checkpoint.json`).

---

## Evaluation

Plot precision-recall curves from evaluation CSVs:

```bash
# Auto-discover latest CSVs
python -m src.services.evaluation_metrics

# Specify CSVs
python -m src.services.evaluation_metrics --csv eval1.csv eval2.csv --output compare.png
```

---

## Project Structure

```
CBG_explainable_NIDS/
├── data/raw/              # Input CSV (gitignored)
├── src/
│   ├── run_explanations.py    # Single entry point
│   ├── config.py              # Env vars
│   ├── load_data.py           # CSV loader
│   ├── prompt_builder.py      # Prompt construction
│   ├── md_writer.py           # Per-flow markdown
│   ├── configs/
│   │   └── experiments.json   # Experiment definitions
│   ├── core/
│   │   ├── pipeline.py        # Experiment orchestration
│   │   └── run_state.py       # Checkpoint, JSONL, resume
│   ├── layers/
│   │   ├── baseline.py
│   │   ├── augmented.py
│   │   └── consensus.py
│   ├── clients/
│   │   ├── gpt_client.py
│   │   └── gemini_client.py
│   ├── services/
│   │   ├── ipqualityscore_service.py
│   │   ├── virustotal_service.py
│   │   ├── abuseipdb_service.py
│   │   ├── synthetic_reputation.py
│   │   ├── evaluation_writer.py
│   │   └── evaluation_metrics.py
│   └── utils/
│       └── llm_utils.py
├── outputs/               # Results (runs/, experiments/)
├── docs/
│   └── EXPERIMENTS.md     # Experiment design notes
└── requirements.txt
```

---

## Further Reading

- [Experiment design & synthetic CTI](docs/EXPERIMENTS.md)

---

CBG Internship – Explainable NIDS
