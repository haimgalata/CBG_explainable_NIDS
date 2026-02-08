from pathlib import Path

def write_flow_md(
    flow_id: int,
    features: dict,
    explanation: str,
    md_subdir: str = "md"
):
    md_dir = Path("outputs") / md_subdir
    md_dir.mkdir(parents=True, exist_ok=True)

    md_path = md_dir / f"flow_{flow_id}.md"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Flow {flow_id}\n\n")

        f.write("## Features\n")
        for k, v in features.items():
            f.write(f"- {k}: {v}\n")

        f.write("\n## LLM Analysis\n")
        f.write(explanation.strip())
        f.write("\n")



