import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import precision_recall_curve, average_precision_score


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


BASELINE_CSV = PROJECT_ROOT / "outputs/experiments/baseline/default/rows_0_538/evaluation.csv"

AUGMENTED_SYNTHETIC_CSV = PROJECT_ROOT / "outputs/experiments/augmented/synthetic/rows_0_538/evaluation.csv"

CONSENSUS_SYNTHETIC_CSV = PROJECT_ROOT / "outputs/experiments/consensus_augmented/synthetic/rows_0_538/evaluation.csv"

CONSENSUS_BASELINE_DEFAULT_CSV = PROJECT_ROOT / "outputs/experiments/consensus_baseline/default/rows_0_538/evaluation.csv"


OUTPUT_FILE = PROJECT_ROOT / "outputs/experiments/precision_recall_comparison.png"



def load_curve(csv_path):

    df = pd.read_csv(csv_path)

    y_true = df["Label"]
    y_score = df["LLM_Prediction"]

    precision, recall, _ = precision_recall_curve(y_true, y_score)
    ap = average_precision_score(y_true, y_score)

    return precision, recall, ap



def plot_precision_recall():

    plt.figure(figsize=(8,8))


    # Baseline
    p, r, ap = load_curve(BASELINE_CSV)
    plt.plot(r, p, label=f"Baseline (AP={ap:.3f})")


    # Augmented Synthetic
    p, r, ap = load_curve(AUGMENTED_SYNTHETIC_CSV)
    plt.plot(r, p, label=f"Augmented Synthetic (AP={ap:.3f})")


    # Consensus Augmented
    p, r, ap = load_curve(CONSENSUS_SYNTHETIC_CSV)
    plt.plot(r, p, label=f"Consensus Augmented (AP={ap:.3f})")


    # Consensus Baseline
    p, r, ap = load_curve(CONSENSUS_BASELINE_DEFAULT_CSV)
    plt.plot(r, p, label=f"Consensus Baseline (AP={ap:.3f})")


    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve Comparison")

    plt.legend()
    plt.grid(True)

    plt.savefig(OUTPUT_FILE, dpi=300)
    plt.show()



if __name__ == "__main__":
    plot_precision_recall()