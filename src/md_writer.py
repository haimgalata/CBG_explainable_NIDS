from pathlib import Path


def write_flow_md(
    flow_id: int,
    features: dict,
    explanation: str,
    output_dir: Path,
    ipqs_fraud_score=None,
    vt_malicious_count=None,
    abuse_score=None
):
    md_dir = output_dir / "md"
    md_dir.mkdir(parents=True, exist_ok=True)

    md_path = md_dir / f"flow_{flow_id}.md"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Flow {flow_id}\n\n")

        # -------------------------
        # Features Section
        # -------------------------
        f.write("## Features\n")
        for k, v in features.items():
            f.write(f"- {k}: {v}\n")

        # -------------------------
        # External Signals Section
        # -------------------------
        if ipqs_fraud_score is not None or vt_malicious_count is not None or abuse_score is not None:
            f.write("\n## External Reputation Signals\n")

            if ipqs_fraud_score is not None:
                f.write(f"- IPQualityScore Fraud Score: {ipqs_fraud_score}\n")

            if vt_malicious_count is not None:
                f.write(f"- VirusTotal Malicious Count: {vt_malicious_count}\n")

            if abuse_score is not None:
                f.write(f"- AbuseIPDB Confidence Score: {abuse_score}\n")

        # -------------------------
        # LLM Analysis Section
        # -------------------------
        f.write("\n## LLM Analysis\n")
        f.write(explanation.strip())
        f.write("\n")
