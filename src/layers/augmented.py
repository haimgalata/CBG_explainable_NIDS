import time
from datetime import datetime

from src.prompt_builder import extract_observable_features, build_enriched_prompt
from src.clients.gpt_client import GPTClient
from src.services.ipqualityscore_service import IPQSASNScoreService
from src.services.virustotal_service import VirusTotalService
from src.config import IPQS_API_KEY, VT_API_KEY
from src.md_writer import write_flow_md


def run_enriched_layer(rows, run_output_dir):
    llm = GPTClient()

    # External services only exist here
    ipqs_service = IPQSASNScoreService(api_key=IPQS_API_KEY)
    vt_service = VirusTotalService(api_key=VT_API_KEY)

    results = []

    for idx, row in enumerate(rows, start=1):
        observable = extract_observable_features(row)

        dst_ip = row["IP_DST_ADDR"]

        # ---- External enrichment ----
        ipqs_response = ipqs_service.lookup(dst_ip)
        vt_malicious_count = vt_service.get_malicious_count(dst_ip)

        ipqs_fraud_score = ipqs_response[1] if ipqs_response else None

        # ---- Build enriched prompt ----
        prompt = build_enriched_prompt(
            observable,
            ipqs_fraud_score=ipqs_fraud_score,
            vt_malicious_count=vt_malicious_count
        )

        start_time = time.perf_counter()
        explanation = llm.explain(prompt)
        end_time = time.perf_counter()

        latency = end_time - start_time

        write_flow_md(
            flow_id=observable.get("ID", idx),
            features=observable,
            explanation=explanation,
            output_dir=run_output_dir,
            ipqs_fraud_score=ipqs_fraud_score,
            vt_malicious_count=vt_malicious_count
        )

        results.append({
            "flow_index": idx,
            "timestamp": datetime.now().isoformat(),
            "layer": "enriched",
            "model": llm.__class__.__name__,
            "llm_latency_seconds": round(latency, 3),
            "observable_features": observable,
            "ipqs_fraud_score": ipqs_fraud_score,
            "vt_malicious_count": vt_malicious_count,
            "explanation": explanation
        })

    return results
