import subprocess
import sys
from multiprocessing import Pool


commands = [
    # שופט נאיבי
    [sys.executable, "-m", "src.run_explanations",
     "--layer", "consensus",
     "--consensus_mode", "baseline",
     "--mode", "default",
     "--start", "0", "--end", "539"],

    # שופט מעושר
    [sys.executable, "-m", "src.run_explanations",
     "--layer", "consensus",
     "--consensus_mode", "augmented",
     "--mode", "synthetic",
     "--start", "0", "--end", "539"],
]


def run_command(cmd):
    print(f"\n🚀 Running: {' '.join(cmd)}\n")
    subprocess.run(cmd)


if __name__ == "__main__":
    with Pool(2) as pool:
        pool.map(run_command, commands)