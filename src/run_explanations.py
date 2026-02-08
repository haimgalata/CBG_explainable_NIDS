from pathlib import Path
from datetime import datetime
import json
import time

from src.services.ipqualityscore_service import IPQSASNScoreService
from src.services.virustotal_service import VirusTotalService
from src.config import IPQS_API_KEY, VT_API_KEY

from src.load_data import load_netflow_csv
from src.prompt_builder import extract_observable_features, build_explanation_prompt
from src.clients.gemini_client import GeminiClient
# from src.clients.gpt_client import GPTClient
from src.md_writer import write_flow_md

RUN_ID = datetime.now().strftime("%Y-%m-%d_%H-%M")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "may_hamalka80-85.csv"
OUTPUT_FILE = PROJECT_ROOT / "outputs" / f"explanations_{RUN_ID}.json"


def explain_flows(rows):
    llm = GeminiClient()
    # llm = GPTClient()

    ipqs_service = IPQSASNScoreService(api_key=IPQS_API_KEY)
    vt_service = VirusTotalService(api_key=VT_API_KEY)

    results = []

    for idx, row in enumerate(rows, start=1):
        observable = extract_observable_features(row)

        dst_ip = row["IP_DST_ADDR"]

        ipqs = ipqs_service.lookup(dst_ip)
        vt = vt_service.get_malicious_count(dst_ip)

        ipqs_fraud_score = ipqs[1] if ipqs else None
        vt_malicious_count = vt

        prompt = build_explanation_prompt(
            observable,
            ipqs_fraud_score=ipqs_fraud_score,
            vt_malicious_count=vt_malicious_count
        )

        start_time = time.perf_counter()
        explanation = llm.explain(prompt)
        end_time = time.perf_counter()

        llm_latency = end_time - start_time

        write_flow_md(
            flow_id=observable["ID"],
            features=observable,
            explanation=explanation,
            md_subdir=f"md_{RUN_ID}"
        )

        results.append({
            "flow_index": idx,
            "timestamp": datetime.now().isoformat(),
            "model": llm.__class__.__name__,
            "llm_latency_seconds": round(llm_latency, 3),
            "observable_features": observable,
            "ipqs_fraud_score": ipqs_fraud_score,
            "vt_malicious_count": vt_malicious_count,
            "explanation": explanation
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def main():
    df = load_netflow_csv(CSV_PATH)
    rows_to_explain = [df.iloc[i] for i in range(20, 25)]
    explain_flows(rows_to_explain)


if __name__ == "__main__":
    main()
