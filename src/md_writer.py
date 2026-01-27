from pathlib import Path

def write_flow_md(flow_id: int, features: dict, explanation: str):
    md_dir = Path("outputs/md")
    md_dir.mkdir(parents=True, exist_ok=True)

    md_path = md_dir / f"flow_{flow_id}.md"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Flow {flow_id} – Anomaly Explanation\n\n")

        f.write("## 🔍 Summary\n")
        f.write("- Long-lived or unusual flow characteristics\n")
        f.write("- Timing or volume patterns deviating from typical traffic\n")
        f.write("- Flagged based on observable statistical behavior\n\n")

        f.write("---\n\n")
        f.write("## 📊 Observable Features\n")
        f.write("| Feature | Value |\n")
        f.write("|------|------|\n")

        for k, v in features.items():
            f.write(f"| {k} | {v} |\n")

        f.write("\n---\n\n")
        f.write("## 🧠 Model Explanation\n")
        f.write(explanation)
