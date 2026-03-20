import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import precision_recall_curve, auc
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


# === Latest CSVs ===
BASELINE_CSV = PROJECT_ROOT / "outputs/experiments/baseline/default/rows_0_538/evaluation.csv"

AUGMENTED_SYNTHETIC_CSV = PROJECT_ROOT / "outputs/experiments/augmented/synthetic/rows_0_538/evaluation.csv"

CONSENSUS_SYNTHETIC_CSV = PROJECT_ROOT / "outputs/experiments/consensus_augmented/synthetic/rows_0_538/evaluation.csv"

CONSENSUS_BASELINE_CSV = PROJECT_ROOT / "outputs/experiments/consensus_baseline/default/rows_0_538/evaluation.csv"


# === Output with timestamp ===
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
OUTPUT_FILE = PROJECT_ROOT / f"outputs/experiments/precision_recall_comparison_{timestamp}.png"


def load_curve(csv_path):
    df = pd.read_csv(csv_path)

    # ניקוי Nullים
    df = df.dropna(subset=["Label", "LLM_Prediction"])

    y_true = df["Label"]
    y_score = df["LLM_Prediction"]

    precision, recall, _ = precision_recall_curve(y_true, y_score)

    # 🔥 חישוב AUC אמיתי שמתאים לגרף
    pr_auc = auc(recall, precision)

    return precision, recall, pr_auc


def plot_precision_recall():

    plt.figure(figsize=(8, 8))

    # === Baseline ===
    p, r, pr_auc = load_curve(BASELINE_CSV)
    plt.plot(r, p, label=f"Baseline (AUC={pr_auc:.3f})")

    # === Augmented Synthetic ===
    p, r, pr_auc = load_curve(AUGMENTED_SYNTHETIC_CSV)
    plt.plot(r, p, label=f"Augmented Synthetic (AUC={pr_auc:.3f})")

    # === Consensus Augmented ===
    p, r, pr_auc = load_curve(CONSENSUS_SYNTHETIC_CSV)
    plt.plot(r, p, label=f"Consensus Augmented (AUC={pr_auc:.3f})")

    # === Consensus Baseline ===
    p, r, pr_auc = load_curve(CONSENSUS_BASELINE_CSV)
    plt.plot(r, p, label=f"Consensus Baseline (AUC={pr_auc:.3f})")

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve Comparison (4 Models)")

    plt.legend()
    plt.grid(True)

    plt.savefig(OUTPUT_FILE, dpi=300)
    plt.show()


if __name__ == "__main__":
    plot_precision_recall()