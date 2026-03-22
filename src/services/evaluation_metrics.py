import argparse
import glob
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import precision_recall_curve, auc
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_EXPERIMENTS_DIR = PROJECT_ROOT / "outputs" / "experiments"


def _find_latest_evaluation_csv(experiments_dir: Path, layer: str, mode: str, rows_pattern: str = "rows_*") -> Path | None:
    """Find most recent evaluation CSV matching layer/mode."""
    pattern = experiments_dir / layer / mode / rows_pattern / "evaluation_*.csv"
    files = sorted(glob.glob(str(pattern)), key=lambda p: Path(p).stat().st_mtime, reverse=True)
    return Path(files[0]) if files else None


def load_curve(csv_path: Path):
    df = pd.read_csv(csv_path)

    # ניקוי Nullים
    df = df.dropna(subset=["Label", "LLM_Prediction"])

    y_true = df["Label"]
    y_score = df["LLM_Prediction"]

    precision, recall, _ = precision_recall_curve(y_true, y_score)

    # 🔥 חישוב AUC אמיתי שמתאים לגרף
    pr_auc = auc(recall, precision)

    return precision, recall, pr_auc


def plot_precision_recall(entries: list[tuple[Path, str]] | None = None, output_file: Path | None = None):
    """
    Plot precision-recall curves. If entries is None, auto-discover from experiments dir.
    entries: list of (csv_path, label) tuples.
    """
    if entries is None:
        base = DEFAULT_EXPERIMENTS_DIR
        entries = []
        for layer, mode, label in [
            ("baseline", "default", "Baseline"),
            ("augmented", "synthetic", "Augmented Synthetic"),
            ("consensus_augmented", "synthetic", "Consensus Augmented"),
            ("consensus_baseline", "default", "Consensus Baseline"),
        ]:
            p = _find_latest_evaluation_csv(base, layer, mode)
            if p and p.exists():
                entries.append((p, label))

    if not entries:
        print("No evaluation CSVs found. Run experiments first.")
        return

    plt.figure(figsize=(8, 8))

    for csv_path, label in entries:
        try:
            p, r, pr_auc = load_curve(csv_path)
            plt.plot(r, p, label=f"{label} (AUC={pr_auc:.3f})")
        except FileNotFoundError:
            print(f"Skipping {csv_path}: not found")
        except Exception as e:
            print(f"Skipping {csv_path}: {e}")

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve Comparison")
    plt.legend()
    plt.grid(True)

    if output_file is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        output_file = DEFAULT_EXPERIMENTS_DIR / f"precision_recall_comparison_{timestamp}.png"

    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300)
    print(f"Saved: {output_file}")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot precision-recall from evaluation CSVs")
    parser.add_argument("--csv", nargs="+", type=Path, help="Evaluation CSV paths (optional)")
    parser.add_argument("--output", type=Path, help="Output PNG path")
    parser.add_argument("--experiments-dir", type=Path, default=DEFAULT_EXPERIMENTS_DIR, help="Base experiments dir for auto-discovery")
    args = parser.parse_args()

    if args.csv:
        entries = [(p, p.stem) for p in args.csv]
        plot_precision_recall(entries=entries, output_file=args.output)
    else:
        import src.services.evaluation_metrics as mod
        mod.DEFAULT_EXPERIMENTS_DIR = args.experiments_dir
        plot_precision_recall(output_file=args.output)